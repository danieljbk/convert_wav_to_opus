#!/usr/bin/env python3
"""Convert Opus files to CAF (Core Audio Format) using ffmpeg."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def convert_opus_to_caf(
    source: Path,
    output: Path,
    *,
    overwrite: bool = False,
    dry_run: bool = False,
) -> bool:
    """Convert a single opus file to CAF format.

    Returns True if successful, False otherwise.
    """
    if output.exists() and not overwrite:
        print(f"Skipping '{source}': '{output.name}' already exists (use --overwrite to replace).")
        return False

    if dry_run:
        print(f"Planning '{source}' -> '{output.name}'")
        return True

    print(f"Converting '{source}' -> '{output.name}'")

    command = [
        "ffmpeg",
        "-i",
        str(source),
        "-c:a",
        "copy",
        "-y" if overwrite else "-n",
        str(output),
    ]

    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
        return True
    except subprocess.CalledProcessError as exc:
        error_msg = exc.stderr.strip() or "ffmpeg exited with a non-zero status."
        print(f"  ERROR: {error_msg}")
        return False


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Convert Opus files to CAF (Core Audio Format) using ffmpeg.",
    )
    parser.add_argument(
        "directory",
        help="Directory containing .opus files to convert.",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Process subdirectories recursively.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing .caf files.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show planned actions without running ffmpeg.",
    )

    args = parser.parse_args()

    root = Path(args.directory).expanduser().resolve()
    if not root.is_dir():
        print(f"Error: Directory '{root}' does not exist or is not a directory.", file=sys.stderr)
        return 1

    # Find all .opus files
    pattern = "**/*.opus" if args.recursive else "*.opus"
    opus_files = sorted(root.glob(pattern))

    if not opus_files:
        print(f"No .opus files found in '{root}'")
        return 0

    # Convert each file
    converted = 0
    skipped = 0
    failed = 0

    for source in opus_files:
        if not source.is_file():
            continue

        output = source.with_suffix(".caf")

        result = convert_opus_to_caf(
            source,
            output,
            overwrite=args.overwrite,
            dry_run=args.dry_run,
        )

        if result:
            if args.dry_run or output.exists():
                converted += 1
        elif output.exists() and not args.overwrite:
            skipped += 1
        else:
            failed += 1

    print("\nDone.")
    print(f"Converted: {converted} file(s)")
    print(f"Skipped:   {skipped} file(s)")
    print(f"Failed:    {failed} file(s)")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
