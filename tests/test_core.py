from __future__ import annotations

import subprocess
from pathlib import Path

from convert_wav_to_opus.core import (
    ConversionError,
    ConversionSummary,
    collect_audio_files,
    convert_directory,
    sanitize_output,
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

    summary = convert_directory(
        tmp_path,
        patterns=("*.wav",),
        overwrite=False,
        runner=runner,  # type: ignore[arg-type]
    )

    assert summary == ConversionSummary(converted=0, skipped=1, failed=0, errors=[])


def test_convert_directory_invokes_runner(tmp_path: Path) -> None:
    source = tmp_path / "episode.wav"
    source.write_bytes(b"")

    called = {"command": None}

    def runner(command: list[str]) -> subprocess.CompletedProcess[str]:
        called["command"] = command
        return subprocess.CompletedProcess(command, returncode=0, stdout="", stderr="")

    summary = convert_directory(
        tmp_path,
        patterns=("*.wav",),
        runner=runner,  # type: ignore[arg-type]
    )

    assert summary.converted == 1
    assert summary.failed == 0
    assert called["command"] is not None
    assert called["command"][0] == "ffmpeg"
    assert called["command"][-1].endswith(".opus")


def test_convert_directory_records_failures(tmp_path: Path) -> None:
    source = tmp_path / "episode.wav"
    source.write_bytes(b"")

    def runner(command: list[str]) -> subprocess.CompletedProcess[str]:
        raise subprocess.CalledProcessError(returncode=1, cmd=command, stderr="boom")

    summary = convert_directory(
        tmp_path,
        patterns=("*.wav",),
        runner=runner,  # type: ignore[arg-type]
    )

    assert summary.converted == 0
    assert summary.failed == 1
    assert summary.errors and isinstance(summary.errors[0], ConversionError)
    assert "boom" in summary.errors[0].args[0]
