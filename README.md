# convert_wav_to_opus

convert_wav_to_opus scans a directory for audio files and generates companion encodes using `ffmpeg`. Use the Opus CLI for `.opus` outputs or the AAC CLI for `.aac`, keeping a simple, repeatable workflow for podcasts, voice notes, or music libraries.

## Features
- Converts the most common audio formats to `.opus` (libopus, default 24 kbps) or `.aac` (libfdk_aac, default 96 kbps).
- Creates filesystem-friendly output names alongside the original files.
- Skips existing output files unless `--overwrite` is supplied.
- Supports dry runs so you can preview the work before it happens.
- Preserves the source channel layout unless you choose to override it.
- Ships with dedicated CLIs (`convert_wav_to_opus` and `convert_wav_to_aac`) plus a small Python API.

## Requirements
- Python 3.9 or newer.
- [`ffmpeg`](https://ffmpeg.org/) available on your `PATH` (with `libfdk_aac` support if you plan to use the AAC CLI).

## Installation

```bash
python -m pip install convert_wav_to_opus
```

To work from the repository instead:

```bash
git clone https://github.com/kwon/convert_wav_to_opus.git
cd convert_wav_to_opus
python -m pip install .  # add ".[dev]" for linting + tests
```

## Usage

```bash
convert_wav_to_opus ~/Music --recursive
```

## CLI tools

### convert_wav_to_opus

| Flag | Description | Default |
|------|-------------|---------|
| `--patterns` | Override input glob patterns (e.g. `--patterns "*.wav" "*.flac"`). | Common audio formats |
| `--recursive` | Traverse subdirectories. | Off |
| `--bitrate` | Target bitrate to request from `ffmpeg`. | `24k` |
| `--channels` | Override channel count for the output audio. | Source layout |
| `--mono` | Shortcut to force mono output. | Off |
| `--sample-rate` | Output sample rate in Hz. | Source rate |
| `--overwrite` | Replace existing outputs. | Off |
| `--dry-run` | Print planned conversions without touching files. | Off |

### convert_wav_to_aac

| Flag | Description | Default |
|------|-------------|---------|
| `--patterns` | Override input glob patterns (e.g. `--patterns "*.wav" "*.flac"`). | Common audio formats |
| `--recursive` | Traverse subdirectories. | Off |
| `--bitrate` | Target bitrate to request from `ffmpeg` (uses `libfdk_aac`). | `96k` |
| `--channels` | Override channel count for the output audio. | Source layout |
| `--mono` | Shortcut to force mono output. | Off |
| `--sample-rate` | Output sample rate in Hz. | Source rate |
| `--overwrite` | Replace existing outputs. | Off |
| `--dry-run` | Print planned conversions without touching files. | Off |

### Examples

Convert everything in `~/Podcasts`, including subdirectories, to Opus:

```bash
convert_wav_to_opus ~/Podcasts --recursive
```

Convert everything in place to AAC instead:

```bash
convert_wav_to_aac /data/audio --recursive
```

Re-encode only FLAC, WAV, and AAC files to stereo 48 kbps Opus outputs:

```bash
convert_wav_to_opus /data/audio --patterns "*.flac" "*.wav" "*.aac" --bitrate 48k --channels 2
```

Force AAC outputs to 22.05 kHz if you need to reduce bandwidth further:

```bash
convert_wav_to_aac /data/audio --sample-rate 22050
```

Preview the work that would be done (applies to either CLI):

```bash
convert_wav_to_opus /data/audio --dry-run
```

## Python API

```python
from pathlib import Path
from convert_wav_to_opus import convert_directory

root = Path("~/Podcasts").expanduser()
summary = convert_directory(root, recursive=True, bitrate="48k")
print(summary.converted, summary.skipped)
```

This API powers the CLI and returns a `ConversionSummary` object with the number of converted, skipped, and failed files plus any corresponding errors.

## Development

```bash
python -m pip install --upgrade pip
python -m pip install ".[dev]"
ruff check .
mypy src
pytest
```

Code style and type checks run automatically in CI. Please update or add tests alongside code changes.

## Contributing

Bug reports and pull requests are welcome! See [`CONTRIBUTING.md`](CONTRIBUTING.md) for details on setting up your environment and the preferred development workflow.

## License

This project is released under the terms of the [MIT License](LICENSE).
