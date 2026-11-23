# QR Code Creator

**Branded QR codes from the command line.** Generate a QR code with your logo in the centre and optional rounded corners.

[![License: MIT](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![qrcode + Pillow](https://img.shields.io/badge/qrcode-Pillow-555?style=flat-square)

<img src="docs/example.png" alt="Example QR code with a centred logo" width="260">

## Features

- Interactive CLI: paste a URL, pick a logo, choose a corner radius.
- Picks up every logo in `images/` (PNG, JPG, WebP, SVG, ...).
- High error correction, so the logo can cover up to ~30% of the code and it still scans.
- Optional rounded corners for the whole image.

## Install

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

SVG logos need Inkscape **or** ImageMagick installed; otherwise convert them to PNG first.

## Usage

1. Put your logo files in `images/` (git-ignored).
2. Run the generator and answer the prompts:

```bash
python qr_with_logo.py
```

```
Enter the URL to encode: https://example.com
Select a logo by number (or choose 'No logo'): 1
Enter border radius (0 for square corners): 30
```

The PNG is saved in the project root, named after the URL.

### As a library

```python
from qr_with_logo import generate_qr_with_logo

generate_qr_with_logo("https://example.com", "images/logo.png", "out.png", border_radius=30)
```

## Tips

- High-contrast logos scan most reliably.
- If a code scans poorly, lower `logo_scale` (default 0.2) or the corner radius.

## License

[MIT](LICENSE)
