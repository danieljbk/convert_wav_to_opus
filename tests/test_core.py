from __future__ import annotations

import subprocess
from pathlib import Path

from convert_wav_to_aac.core import convert_directory as convert_directory_aac
from convert_wav_to_opus.core import (
    ConversionError as OpusConversionError,
)
from convert_wav_to_opus.core import (
    ConversionSummary as OpusConversionSummary,
)
from convert_wav_to_opus.core import (
    collect_audio_files,
    sanitize_output,
)
from convert_wav_to_opus.core import (
    convert_directory as convert_directory_opus,
)


def test_collect_audio_files_respects_recursion(tmp_path: Path) -> None:
    (tmp_path / "track1.wav").write_bytes(b"")
    (tmp_path / "track2.mp3").write_bytes(b"")
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "hidden.flac").write_bytes(b"")

    non_recursive = collect_audio_files(tmp_path, ("*.wav", "*.flac"), recursive=False)
    recursive = collect_audio_files(tmp_path, ("*.wav", "*.flac"), recursive=True)

    assert (tmp_path / "track1.wav") in non_recursive
    assert (tmp_path / "nested" / "hidden.flac") not in non_recursive
    assert (tmp_path / "nested" / "hidden.flac") in recursive


def test_sanitize_output_normalizes_name(tmp_path: Path) -> None:
    source = tmp_path / "My Cool-Track.WAV"
    source.write_bytes(b"")
    output = sanitize_output(source)

    assert output.name == "my_cool_track.opus"
    assert output.parent == tmp_path


def test_convert_directory_skips_existing_outputs(tmp_path: Path) -> None:
    source = tmp_path / "episode.wav"
    source.write_bytes(b"")
    existing = tmp_path / "episode.opus"
    existing.write_bytes(b"already here")

    def runner(command: list[str]) -> None:  # pragma: no cover - should not run
        raise AssertionError(f"Runner should not be invoked: {command}")

    summary = convert_directory_opus(
        tmp_path,
        patterns=("*.wav",),
        overwrite=False,
        runner=runner,  # type: ignore[arg-type]
    )

    assert summary == OpusConversionSummary(converted=0, skipped=1, failed=0, errors=[])


def test_convert_directory_invokes_runner(tmp_path: Path) -> None:
    source = tmp_path / "episode.wav"
    source.write_bytes(b"")

    called = {"command": None}

    def runner(command: list[str]) -> subprocess.CompletedProcess[str]:
        called["command"] = command
        return subprocess.CompletedProcess(command, returncode=0, stdout="", stderr="")

    summary = convert_directory_opus(
        tmp_path,
        patterns=("*.wav",),
        runner=runner,  # type: ignore[arg-type]
    )

    assert summary.converted == 1
    assert summary.failed == 0
    assert called["command"] is not None
    assert called["command"][0] == "ffmpeg"
    assert called["command"][-1].endswith(".opus")
    assert "-ac" not in called["command"]


def test_convert_directory_handles_aac_by_default(tmp_path: Path) -> None:
    source = tmp_path / "song.aac"
    source.write_bytes(b"")

    called = {"command": None}

    def runner(command: list[str]) -> subprocess.CompletedProcess[str]:
        called["command"] = command
        return subprocess.CompletedProcess(command, returncode=0, stdout="", stderr="")

    summary = convert_directory_opus(
        tmp_path,
        runner=runner,  # type: ignore[arg-type]
    )

    assert summary.converted == 1
    assert summary.failed == 0
    assert called["command"] is not None
    assert called["command"][0] == "ffmpeg"
    assert called["command"][-1].endswith(".opus")


def test_convert_directory_outputs_aac_when_requested(tmp_path: Path) -> None:
    source = tmp_path / "episode.wav"
    source.write_bytes(b"")

    called = {"command": None}

    def runner(command: list[str]) -> subprocess.CompletedProcess[str]:
        called["command"] = command
        return subprocess.CompletedProcess(command, returncode=0, stdout="", stderr="")

    summary = convert_directory_aac(
        tmp_path,
        runner=runner,  # type: ignore[arg-type]
    )

    assert summary.converted == 1
    assert summary.failed == 0
    assert called["command"] is not None
    assert "-c:a" in called["command"]
    codec_index = called["command"].index("-c:a")
    assert called["command"][codec_index + 1] == "libfdk_aac"
    assert "-ar" not in called["command"]
    assert called["command"][-1].endswith(".aac")


def test_convert_directory_can_override_channels(tmp_path: Path) -> None:
    source = tmp_path / "episode.wav"
    source.write_bytes(b"")

    called = {"command": None}

    def runner(command: list[str]) -> subprocess.CompletedProcess[str]:
        called["command"] = command
        return subprocess.CompletedProcess(command, returncode=0, stdout="", stderr="")

    summary = convert_directory_opus(
        tmp_path,
        channels=2,
        runner=runner,  # type: ignore[arg-type]
    )

    assert summary.converted == 1
    assert summary.failed == 0
    assert called["command"] is not None
    assert "-ac" in called["command"]
    channel_index = called["command"].index("-ac")
    assert called["command"][channel_index + 1] == "2"


def test_convert_directory_force_mono(tmp_path: Path) -> None:
    source = tmp_path / "episode.wav"
    source.write_bytes(b"")

    called = {"command": None}

    def runner(command: list[str]) -> subprocess.CompletedProcess[str]:
        called["command"] = command
        return subprocess.CompletedProcess(command, returncode=0, stdout="", stderr="")

    summary = convert_directory_opus(
        tmp_path,
        channels=1,
        runner=runner,  # type: ignore[arg-type]
    )

    assert summary.converted == 1
    assert summary.failed == 0
    assert called["command"] is not None
    assert "-ac" in called["command"]
    channel_index = called["command"].index("-ac")
    assert called["command"][channel_index + 1] == "1"


def test_convert_directory_uses_custom_sample_rate(tmp_path: Path) -> None:
    source = tmp_path / "episode.wav"
    source.write_bytes(b"")

    called = {"command": None}

    def runner(command: list[str]) -> subprocess.CompletedProcess[str]:
        called["command"] = command
        return subprocess.CompletedProcess(command, returncode=0, stdout="", stderr="")

    summary = convert_directory_aac(
        tmp_path,
        sample_rate=22_050,
        runner=runner,  # type: ignore[arg-type]
    )

    assert summary.converted == 1
    assert summary.failed == 0
    assert called["command"] is not None
    assert "-ar" in called["command"]
    sample_rate_index = called["command"].index("-ar")
    assert called["command"][sample_rate_index + 1] == "22050"
    assert "-ac" not in called["command"]


def test_convert_directory_records_failures(tmp_path: Path) -> None:
    source = tmp_path / "episode.wav"
    source.write_bytes(b"")

    def runner(command: list[str]) -> subprocess.CompletedProcess[str]:
        raise subprocess.CalledProcessError(returncode=1, cmd=command, stderr="boom")

    summary = convert_directory_opus(
        tmp_path,
        patterns=("*.wav",),
        runner=runner,  # type: ignore[arg-type]
    )

    assert summary.converted == 0
    assert summary.failed == 1
    assert summary.errors and isinstance(summary.errors[0], OpusConversionError)
    assert "boom" in summary.errors[0].args[0]


def test_convert_directory_skips_existing_aac_output(tmp_path: Path) -> None:
    source = tmp_path / "song.aac"
    original_content = b"original"
    source.write_bytes(original_content)

    called = {"output_path": None}

    def runner(command: list[str]) -> subprocess.CompletedProcess[str]:
        out_path = Path(command[-1])
        out_path.write_bytes(b"new")
        called["output_path"] = out_path
        return subprocess.CompletedProcess(command, returncode=0, stdout="", stderr="")

    summary = convert_directory_aac(
        tmp_path,
        overwrite=True,
        runner=runner,  # type: ignore[arg-type]
    )

    assert summary.converted == 0
    assert summary.skipped == 1
    assert called["output_path"] is None
    assert source.read_bytes() == original_content


def test_convert_directory_overwrites_opus_generating_new_file(tmp_path: Path) -> None:
    source = tmp_path / "song.OPUS"
    source.write_bytes(b"original")

    called = {"output_path": None}

    def runner(command: list[str]) -> subprocess.CompletedProcess[str]:
        out_path = Path(command[-1])
        out_path.write_bytes(b"new")
        called["output_path"] = out_path
        return subprocess.CompletedProcess(command, returncode=0, stdout="", stderr="")

    summary = convert_directory_opus(
        tmp_path,
        patterns=("*.OPUS",),
        overwrite=True,
        runner=runner,  # type: ignore[arg-type]
    )

    assert summary.converted == 1
    assert summary.skipped == 0
    assert called["output_path"] is not None
    assert Path(called["output_path"]).suffix == ".opus"
    assert (tmp_path / "song.opus").read_bytes() == b"new"
