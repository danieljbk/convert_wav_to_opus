"""Core conversion helpers for AAC outputs."""

from __future__ import annotations

import subprocess
from collections.abc import Callable, Iterable, Iterator, Sequence
from dataclasses import dataclass, field
from pathlib import Path

SUPPORTED_INPUT_EXTENSIONS: tuple[str, ...] = (
    ".wav",
    ".mp3",
    ".m4a",
    ".flac",
    ".aac",
    ".ogg",
    ".wma",
    ".aiff",
    ".aif",
    ".aifc",
)

DEFAULT_PATTERNS: tuple[str, ...] = tuple(
    f"*{extension}" for extension in SUPPORTED_INPUT_EXTENSIONS
)

_OUTPUT_EXTENSION = ".aac"
_OUTPUT_CODEC = "libfdk_aac"
_DEFAULT_BITRATE = "96k"

DEFAULT_BITRATE = _DEFAULT_BITRATE


def _same_path(a: Path, b: Path) -> bool:
    try:
        return a.resolve() == b.resolve()
    except FileNotFoundError:
        return a.absolute() == b.absolute()


class ConversionError(RuntimeError):
    """Raised when a conversion fails."""

    def __init__(self, source: Path, ffmpeg_error: str | None = None) -> None:
        self.source = source
        self.ffmpeg_error = ffmpeg_error
        message = f"ffmpeg failed for '{source}'"
        if ffmpeg_error:
            message = f"{message}: {ffmpeg_error}"
        super().__init__(message)


@dataclass
class ConversionSummary:
    """Aggregated results from a conversion run."""

    converted: int = 0
    skipped: int = 0
    failed: int = 0
    errors: list[ConversionError] = field(default_factory=list)

    def __iter__(self) -> Iterator[int]:
        return iter((self.converted, self.skipped, self.failed))


def collect_audio_files(root: Path, patterns: Iterable[str], recursive: bool) -> list[Path]:
    """Return a sorted list of unique files that match the provided patterns."""
    files: set[Path] = set()
    for pattern in patterns:
        matches = root.rglob(pattern) if recursive else root.glob(pattern)
        files.update(match for match in matches if match.is_file())
    return sorted(files)


def sanitize_output(source: Path, *, output_extension: str = _OUTPUT_EXTENSION) -> Path:
    """Return a path adjacent to ``source`` using a safe file name and extension."""
    safe_name = source.stem.lower().replace("-", "_").replace(" ", "_")
    return source.with_name(f"{safe_name}{output_extension}")


def _run_ffmpeg(command: Sequence[str]) -> subprocess.CompletedProcess[str]:
    """Execute ffmpeg, raising if the command fails."""
    return subprocess.run(command, check=True, capture_output=True, text=True)


def convert_file(
    source: Path,
    output: Path,
    *,
    bitrate: str,
    channels: int | None,
    dry_run: bool,
    sample_rate: int | None,
    runner: Callable[[Sequence[str]], subprocess.CompletedProcess[str]] = _run_ffmpeg,
) -> None:
    """Convert a single file to AAC, raising ConversionError on failure."""
    if dry_run:
        return

    if output.suffix.lower() != _OUTPUT_EXTENSION:
        raise ValueError(
            f"Output file '{output}' has unexpected extension; expected '{_OUTPUT_EXTENSION}'.",
        )

    command = [
        "ffmpeg",
        "-i",
        str(source),
        "-c:a",
        _OUTPUT_CODEC,
        "-b:a",
        bitrate,
    ]

    if channels is not None:
        command.extend(["-ac", str(channels)])

    if sample_rate is not None:
        command.extend(["-ar", str(sample_rate)])

    command.extend(
        [
            "-y",
            str(output),
        ],
    )

    try:
        runner(command)
    except subprocess.CalledProcessError as exc:
        raise ConversionError(source, exc.stderr.strip() or None) from exc


def convert_directory(
    root: Path,
    *,
    patterns: Iterable[str] | None = None,
    recursive: bool = False,
    bitrate: str | None = None,
    channels: int | None = None,
    overwrite: bool = False,
    dry_run: bool = False,
    sample_rate: int | None = None,
    runner: Callable[[Sequence[str]], subprocess.CompletedProcess[str]] = _run_ffmpeg,
    on_convert: Callable[[Path, Path, bool], None] | None = None,
    on_skip: Callable[[Path, Path], None] | None = None,
    on_failure: Callable[[ConversionError], None] | None = None,
) -> ConversionSummary:
    """Convert files within ``root`` according to the supplied options."""
    source_patterns = tuple(patterns) if patterns is not None else DEFAULT_PATTERNS
    audio_files = collect_audio_files(root, source_patterns, recursive)

    summary = ConversionSummary()
    effective_bitrate = bitrate or _DEFAULT_BITRATE
    effective_sample_rate = sample_rate
    for source in audio_files:
        output = sanitize_output(source, output_extension=_OUTPUT_EXTENSION)

        if output.exists() and not overwrite:
            if on_skip is not None:
                on_skip(source, output)
            summary.skipped += 1
            continue

        if not dry_run and _same_path(source, output):
            summary.skipped += 1
            if on_skip is not None:
                on_skip(source, output)
            continue

        if on_convert is not None:
            on_convert(source, output, dry_run)

        try:
            convert_file(
                source,
                output,
                bitrate=effective_bitrate,
                channels=channels,
                dry_run=dry_run,
                sample_rate=effective_sample_rate,
                runner=runner,
            )
        except ConversionError as error:
            summary.failed += 1
            summary.errors.append(error)
            if on_failure is not None:
                on_failure(error)
        else:
            summary.converted += 1

    return summary
