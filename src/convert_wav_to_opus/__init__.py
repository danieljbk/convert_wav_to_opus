"""Public package interface for convert_wav_to_opus."""

from __future__ import annotations

from .core import (
    DEFAULT_PATTERNS,
    ConversionError,
    ConversionSummary,
    collect_audio_files,
    convert_directory,
    sanitize_output,
)

__all__ = [
    "DEFAULT_PATTERNS",
    "ConversionError",
    "ConversionSummary",
    "collect_audio_files",
    "convert_directory",
    "sanitize_output",
]

__version__ = "0.1.0"
