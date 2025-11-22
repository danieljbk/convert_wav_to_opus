# FFmpeg Batch Conversion: OPUS to CAF

This guide explains how to convert multiple `.opus` files to `.caf` format using ffmpeg.

## Simple Bash Loop (Recommended)

### For all files in current directory:

```bash
for file in *.opus; do
  ffmpeg -i "$file" -c:a copy "${file%.opus}.caf"
done
```

### For files in a specific folder:

```bash
for file in podcasts/*.opus; do
  ffmpeg -i "$file" -c:a copy "${file%.opus}.caf"
done
```

## Explanation

- `for file in *.opus` - loops through all .opus files
- `"$file"` - the input file (quotes handle spaces in filenames)
- `"${file%.opus}.caf"` - removes `.opus` extension and adds `.caf`

## Recursive (Include Subfolders)

If you want to process files in subfolders too:

```bash
find podcasts -name "*.opus" -type f -exec sh -c '
  for file; do
    ffmpeg -i "$file" -c:a copy "${file%.opus}.caf"
  done
' sh {} +
```

## As a Reusable Script

Create a file called `convert_folder.sh`:

```bash
#!/bin/bash
for file in "$1"/*.opus; do
  [ -f "$file" ] || continue
  ffmpeg -i "$file" -c:a copy "${file%.opus}.caf"
done
```

Make it executable and use it:

```bash
chmod +x convert_folder.sh
./convert_folder.sh podcasts
```

## The Command Explained

```bash
ffmpeg -i input.opus -c:a copy output.caf
```

- `-i input.opus` - input file
- `-c:a copy` - copy audio codec without re-encoding (fast)
- `output.caf` - output file in CAF format
