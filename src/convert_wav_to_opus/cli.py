"""Command-line interface for convert_wav_to_opus."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from . import __version__
from .core import DEFAULT_PATTERNS, ConversionError, convert_directory


def build_parser() -> argparse.ArgumentParser:
    """Return the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        description="Convert audio files in a directory to Opus using ffmpeg.",
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
        default="32k",
        help="Target bitrate for libopus (default: 32k).",
    )
    parser.add_argument(
        "--channels",
        type=int,
        default=1,
        help="Number of audio channels to request (default: 1).",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Process subdirectories recursively.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing .opus files.",
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
        bitrate=args.bitrate,
        channels=args.channels,
        overwrite=args.overwrite,
        dry_run=args.dry_run,
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
