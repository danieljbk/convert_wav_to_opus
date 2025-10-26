# convert_wav_to_opus

convert_wav_to_opus scans a directory for audio files and generates companion Opus (`.opus`) encodes using `ffmpeg`. Use it to shrink podcasts, voice notes, or music libraries while keeping a simple, repeatable workflow.

## Features
- Converts the most common audio formats to `.opus` using the libopus encoder.
- Creates filesystem-friendly output names alongside the original files.
- Skips existing `.opus` files unless `--overwrite` is supplied.
- Supports dry runs so you can preview the work before it happens.
- Ships as both a CLI (`convert_wav_to_opus`) and a small Python API.

## Requirements
- Python 3.9 or newer.
- [`ffmpeg`](https://ffmpeg.org/) available on your `PATH`.

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

### Common options

| Flag | Description | Default |
|------|-------------|---------|
| `--patterns` | Override input glob patterns (e.g. `--patterns "*.wav" "*.flac"`). | Common audio formats |
| `--recursive` | Traverse subdirectories. | Off |
| `--bitrate` | Target bitrate to request from `ffmpeg`. | `32k` |
| `--channels` | Channel count for the output audio. | `1` |
| `--overwrite` | Replace existing `.opus` outputs. | Off |
| `--dry-run` | Print planned conversions without touching files. | Off |

### Examples

Convert everything in `~/Podcasts`, including subdirectories:

```bash
convert_wav_to_opus ~/Podcasts --recursive
```

Re-encode only FLAC and WAV files to stereo 48 kbps outputs:

```bash
convert_wav_to_opus /data/audio --patterns "*.flac" "*.wav" --bitrate 48k --channels 2
```

Preview the work that would be done:

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
