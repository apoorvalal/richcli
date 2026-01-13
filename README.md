# `richcli`: user-friendly terminal interfaces

User-friendly Terminal User Interfaces (TUI) for intimidating unix tools, built with the [rich](https://rich.readthedocs.io/en/stable/introduction.html) python library for modern terminal interfaces. The flagship “magnet” mode parses a CLI’s `-h/--help` output and walks new users through building a safe, explicit command line. Prebuilt FFmpeg and pdftk flows remain available for the most common media and PDF operations.

## Features

### Magnet: interactive builder for any CLI
  - Parse a command’s help text and list detected options and arguments
  - Add flags, positional arguments, and values with prompts that explain requirements
  - Pipe help text in (`mytool --help | richcli magnet mytool`) when the tool needs special flags to show usage
  - Save or run the assembled command after preview

Example of building up a pandoc command to convert a markdown file to html:
[![asciicast](https://asciinema.org/a/YLkkZAKHf3fMEVKoZD2mTYgRW.svg)](https://asciinema.org/a/YLkkZAKHf3fMEVKoZD2mTYgRW)

### Media conversion/slicing: FFmpeg presets
  - Convert between media formats
  - Resize videos
  - Trim media files
  - Adjust audio settings

Example of slicing an mp3 with timestamps:
[![asciicast](https://asciinema.org/a/9RO8sgs6USJcdUtfAXNp0icZe.svg)](https://asciinema.org/a/9RO8sgs6USJcdUtfAXNp0icZe)

### PDF tools: pdftk and ghostscript operations
  - Extract pages
  - Merge PDFs
  - Compress PDFs
  - Rotate pages
  - Add page numbers
  - Split PDFs

Example of slicing a pdf (potentially to upload into a RAG / LLM's context):
[![asciicast](https://asciinema.org/a/ORABjxo0qCnuAKX6IUYvaUO6r.svg)](https://asciinema.org/a/ORABjxo0qCnuAKX6IUYvaUO6r)


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

### Launch specific tools directly:

```bash
richcli magnet <command>  # Generic builder for any CLI (magnet mode)
richcli <command>         # Shortcut: jump straight into magnet for that command
richcli ffmpeg            # FFmpeg UI presets
richcli pdf               # PDF Tools presets
```

### Launch the main UI:

```bash
richcli
```

The main menu defaults to magnet mode so first-time CLI users can start with the guided builder, with FFmpeg and pdftk available as ready-made presets.

### Navigation

At any prompt you can type `b` to go back to the previous menu or `q`/`quit` to exit the current tool without relying on Ctrl+C/Ctrl+D.
