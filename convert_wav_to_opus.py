#!/usr/bin/env python3
"""Convenience entry point for convert_wav_to_opus."""

from __future__ import annotations

from pathlib import Path
import sys


def main() -> int:
    """Locate the installed package and invoke its CLI main."""
    src = Path(__file__).resolve().parent / "src"
    if src.is_dir():
        sys.path.insert(0, str(src))

    from convert_wav_to_opus.cli import main as cli_main

    return cli_main()


if __name__ == "__main__":
    raise SystemExit(main())
