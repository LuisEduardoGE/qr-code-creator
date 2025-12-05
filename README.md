# QR Code Generator with Logo

Generate QR codes with a centered logo and optional rounded corners via a simple CLI.

## Prerequisites

- Python 3.8+
- Inkscape **or** ImageMagick (optional) — only needed when using SVG logos

## Setup

Create a virtual environment (recommended) and install dependencies:

```bash
python -m venv .venv
.\.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

## Usage

1) Add your logo images (PNG, JPG, SVG, WebP, etc.) to the `images/` folder.  
2) Run the generator:

```bash
python qr_with_logo.py
```

3) Follow the prompts:
   - Enter the URL to encode
   - Pick a logo by number (or choose “No logo” for a plain QR)
   - Enter border radius (0 for square corners, ~20–50 for rounded)

### Output

- A QR image is saved in the project root (named from the URL).  
- If you include an SVG logo, make sure Inkscape or ImageMagick is installed; otherwise, convert it to PNG first.

## Features

- Interactive CLI flow
- Auto-detects logos in `images/`
- Configurable rounded corners
- High error correction (logo can cover ~30% of the QR)

## Project structure

```
qr-code-creator/
├─ images/           # Place your logos here (gitignored)
├─ qr_with_logo.py   # Main script
├─ requirements.txt  # Dependencies
└─ README.md
```

## Tips

- Keep logos high-contrast for best scan reliability.
- If the QR scans poorly, try reducing the logo size or using a smaller border radius.
