"""Command-line interface for convert_wav_to_aac."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from convert_wav_to_opus import __version__  # reuse shared version

from .core import DEFAULT_PATTERNS, ConversionError, convert_directory


def build_parser() -> argparse.ArgumentParser:
    """Return the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        description="Convert audio files in a directory to AAC using ffmpeg.",
    )
    parser.add_argument(
        "directory",
        help="Directory containing audio files to convert.",
    )
    parser.add_argument(
        "--patterns",
        nargs="+",
        default=None,
        help=(
            "Glob patterns for input files. "
            f"Defaults to: {' '.join(DEFAULT_PATTERNS)}."
        ),
    )
    parser.add_argument(
        "--bitrate",
        default=None,
        help="Target bitrate for AAC (default: 96k).",
    )
    parser.add_argument(
        "--channels",
        type=int,
        default=None,
        help="Override channel count for the output audio (default: keep source layout).",
    )
    parser.add_argument(
        "--mono",
        action="store_true",
        help="Force mono output (overrides --channels).",
    )
    parser.add_argument(
        "--sample-rate",
        type=int,
        default=None,
        help="Sample rate for the output audio in Hz (default: keep source rate).",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Process subdirectories recursively.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing outputs.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show planned actions without running ffmpeg.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)

    root = Path(args.directory).expanduser().resolve()
    if not root.is_dir():
        parser.error(f"Directory '{root}' does not exist or is not a directory.")

    channels = args.channels
    if args.mono:
        if channels is not None and channels != 1:
            parser.error("--mono cannot be combined with --channels (use one or the other).")
        channels = 1

    bitrate = args.bitrate
    sample_rate = args.sample_rate

    def on_convert(source: Path, output: Path, dry_run: bool) -> None:
        action = "Planning" if dry_run else "Converting"
        print(f"{action} '{source}' -> '{output.name}'")

    def on_skip(source: Path, output: Path) -> None:
        print(f"Skipping '{source}': '{output.name}' already exists (use --overwrite to replace).")

    def on_failure(error: ConversionError) -> None:
        message = error.ffmpeg_error or "ffmpeg exited with a non-zero status."
        print(f"  ERROR: {message}")

    summary = convert_directory(
        root,
        patterns=args.patterns,
        recursive=args.recursive,
        bitrate=bitrate,
        channels=channels,
        overwrite=args.overwrite,
        dry_run=args.dry_run,
        sample_rate=sample_rate,
        on_convert=on_convert,
        on_skip=on_skip,
        on_failure=on_failure,
    )

    print("\nDone.")
    print(f"Converted: {summary.converted} file(s)")
    print(f"Skipped:   {summary.skipped} file(s)")
    print(f"Failed:    {summary.failed} file(s)")

    return 0 if summary.failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
