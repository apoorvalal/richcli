# RichCLI

User-friendly Terminal User Interfaces (TUI) for venerable but intimidating unix tools (`ffmpeg, pdftk`), built with the Rich Python library. I can almost never remember the exact syntax for pdftk or ffmpeg commands but know that they can basically do everything I want, so I built these tools to make it easier to perform common operations on PDFs and media files.

## Features

- PDF Tools: Terminal UI for pdftk and ghostscript operations
  - Extract pages
  - Merge PDFs
  - Compress PDFs
  - Rotate pages
  - Add page numbers
  - Split PDFs

- FFmpeg UI: Terminal UI for FFmpeg operations
  - Convert between media formats
  - Resize videos
  - Trim media files
  - Adjust audio settings

## Installation

### From Source

```bash
git clone https://github.com/apoorvalal/richcli.git
cd richcli
pip install -e .
```

### Dependencies

- Python 3.7+
- Rich library (installed automatically by pip)
- External tools:
  - PDF Tools requires:
    - pdftk
    - ghostscript
  - FFmpeg UI requires:
    - ffmpeg

## Usage

### Launch the main UI:

```bash
richcli
```

### Launch specific tools directly:

```bash
richcli pdf     # Launch PDF Tools
richcli ffmpeg  # Launch FFmpeg UI
```

### Help and version information:

```bash
richcli --help
richcli --version
```

## Development

This project uses Python's setuptools for packaging.

To install in development mode:

```bash
pip install -e .
```
