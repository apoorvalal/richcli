# `richcli`: user-friendly terminal interfaces

User-friendly Terminal User Interfaces (TUI) for venerable but intimidating unix tools (`ffmpeg, pdftk`), built with the [rich](https://rich.readthedocs.io/en/stable/introduction.html) python library for modern terminal interfaces. Interactively stitches together a command (say, `ffmpeg -i input.mp3 -ss 00:00:10 -to 00:01:00`) that you can then run, or use as a learning tool.

Remembering the flags and positional arguments for pdftk or ffmpeg commands is challenging and error-prone but they can also basically do most things you might want, so I built this CLI (ably assistant by claude) to make it easier to perform common operations. It also includes a generic CLI builder that can be used to build up any command line call interactively; this functionality is demoed below with pandoc.

## Features

### PDF Tools: Terminal UI for pdftk and ghostscript operations
  - Extract pages
  - Merge PDFs
  - Compress PDFs
  - Rotate pages
  - Add page numbers
  - Split PDFs

Example of slicing a pdf (potentially to upload into a RAG / LLM's context)

[![asciicast](https://asciinema.org/a/ORABjxo0qCnuAKX6IUYvaUO6r.svg)](https://asciinema.org/a/ORABjxo0qCnuAKX6IUYvaUO6r)

### Media Conversion/slicing tools for  FFmpeg operations
  - Convert between media formats
  - Resize videos
  - Trim media files
  - Adjust audio settings

Example of slicing an mp3 with timestamps

[![asciicast](https://asciinema.org/a/9RO8sgs6USJcdUtfAXNp0icZe.svg)](https://asciinema.org/a/9RO8sgs6USJcdUtfAXNp0icZe)

### Arbirary CLI applications: build up a command line call interactively for any CLI
  - run `richcli magnet <command>`
  - add positional or keyword arguments
  - add flags
  - run the command

Example of building up a pandoc command to convert a markdown file to html

[![asciicast](https://asciinema.org/a/YLkkZAKHf3fMEVKoZD2mTYgRW.svg)](https://asciinema.org/a/YLkkZAKHf3fMEVKoZD2mTYgRW)


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
richcli pdf     # Launch PDF Tools
richcli ffmpeg  # Launch FFmpeg UI
richcli magnet <command>  # Launch arbitrary CLI builder
```

### Launch the main UI:

```bash
richcli
```

