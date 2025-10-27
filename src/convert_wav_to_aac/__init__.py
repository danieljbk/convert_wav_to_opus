"""Public package interface for convert_wav_to_aac."""

from __future__ import annotations

from .core import (
    DEFAULT_BITRATE,
    DEFAULT_PATTERNS,
    SUPPORTED_INPUT_EXTENSIONS,
    ConversionError,
    ConversionSummary,
    collect_audio_files,
    convert_directory,
    sanitize_output,
)

__all__ = [
    "ConversionError",
    "ConversionSummary",
    "DEFAULT_BITRATE",
    "DEFAULT_PATTERNS",
    "SUPPORTED_INPUT_EXTENSIONS",
    "collect_audio_files",
    "convert_directory",
    "sanitize_output",
]
