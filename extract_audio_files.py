#!/usr/bin/env python3
"""Extract audio files into separate folders by extension."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


def extract_files_by_extension(
    source_dir: Path,
    extension: str,
    output_dir: Path,
    *,
    dry_run: bool = False,
) -> int:
    """Extract files with the given extension to output directory.

    Maintains the directory structure relative to source_dir.
    Returns the number of files copied.
    """
    # Find all files with the given extension
    pattern = f"**/*{extension}"
    files = sorted(source_dir.glob(pattern))

    if not files:
        print(f"No {extension} files found in '{source_dir}'")
        return 0

    copied = 0
    for source_file in files:
        if not source_file.is_file():
            continue

        # Calculate relative path to maintain directory structure
        rel_path = source_file.relative_to(source_dir)
        dest_file = output_dir / rel_path

        # Create parent directories if needed
        if not dry_run:
            dest_file.parent.mkdir(parents=True, exist_ok=True)

        if dry_run:
            print(f"Would copy: {source_file} -> {dest_file}")
        else:
            print(f"Copying: {rel_path}")
            shutil.copy2(source_file, dest_file)

        copied += 1

    return copied


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Extract audio files into separate folders by extension.",
    )
    parser.add_argument(
        "source_directory",
        help="Source directory containing audio files.",
    )
    parser.add_argument(
        "--opus-output",
        default=None,
        help="Output directory for .opus files (default: <source>_opus).",
    )
    parser.add_argument(
        "--caf-output",
        default=None,
        help="Output directory for .caf files (default: <source>_caf).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show planned actions without copying files.",
    )

    args = parser.parse_args()

    source_dir = Path(args.source_directory).expanduser().resolve()
    if not source_dir.is_dir():
        print(f"Error: Directory '{source_dir}' does not exist or is not a directory.", file=sys.stderr)
        return 1

    # Determine output directories
    opus_output = Path(args.opus_output).expanduser().resolve() if args.opus_output else source_dir.parent / f"{source_dir.name}_opus"
    caf_output = Path(args.caf_output).expanduser().resolve() if args.caf_output else source_dir.parent / f"{source_dir.name}_caf"

    print(f"Source directory: {source_dir}")
    print(f"Opus output: {opus_output}")
    print(f"CAF output: {caf_output}")
    print()

    # Extract .opus files
    print("Extracting .opus files...")
    opus_count = extract_files_by_extension(
        source_dir,
        ".opus",
        opus_output,
        dry_run=args.dry_run,
    )
    print(f"Extracted {opus_count} .opus file(s)\n")

    # Extract .caf files
    print("Extracting .caf files...")
    caf_count = extract_files_by_extension(
        source_dir,
        ".caf",
        caf_output,
        dry_run=args.dry_run,
    )
    print(f"Extracted {caf_count} .caf file(s)\n")

    print("Done.")
    print(f"Total files extracted: {opus_count + caf_count}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
