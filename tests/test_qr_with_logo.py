from pathlib import Path

import pytest
from PIL import Image

import qr_with_logo
from qr_with_logo import (
    add_rounded_corners,
    generate_qr_with_logo,
    get_images_from_folder,
)

URL = "https://example.com"
LOGO_RGB = (200, 30, 30)


def decode(path: Path) -> list[str]:
    """Decode with zxing-cpp (a small wheel in requirements-dev.txt); skip if it is missing."""
    zxingcpp = pytest.importorskip("zxingcpp")
    image = Image.open(path).convert("RGBA")
    flat = Image.new("RGBA", image.size, "white")
    flat.alpha_composite(image)  # transparent rounded corners -> white, as a phone would see it
    return [r.text for r in zxingcpp.read_barcodes(flat.convert("RGB"))]


def assert_qr_geometry(image: Image.Image, box_size: int, border: int) -> None:
    width, height = image.size
    assert width == height
    assert width % box_size == 0
    modules = width // box_size - 2 * border
    assert modules >= 21 and (modules - 21) % 4 == 0  # QR versions are 21, 25, 29, ... modules wide


@pytest.fixture
def logo(tmp_path):
    path = tmp_path / "logo.png"
    Image.new("RGBA", (200, 200), (*LOGO_RGB, 255)).save(path)
    return path


def test_plain_qr_is_written_with_expected_size_and_decodes(tmp_path):
    out = tmp_path / "plain.png"
    generate_qr_with_logo(URL, None, str(out))

    assert out.is_file()
    with Image.open(out) as image:
        assert image.format == "PNG"
        assert_qr_geometry(image, box_size=10, border=4)
        assert image.size == (370, 370)  # version 3 (29 modules) at error correction H
    assert decode(out) == [URL]


def test_box_size_and_border_set_the_dimensions(tmp_path):
    out = tmp_path / "small.png"
    generate_qr_with_logo(URL, None, str(out), qr_box_size=5, qr_border=2)
    with Image.open(out) as image:
        assert_qr_geometry(image, box_size=5, border=2)
        assert image.size == (165, 165)
    assert decode(out) == [URL]


def test_logo_is_centred_and_code_still_decodes(tmp_path, logo):
    out = tmp_path / "logo_qr.png"
    generate_qr_with_logo(URL, str(logo), str(out))

    with Image.open(out) as image:
        rgba = image.convert("RGBA")
        cx, cy = rgba.width // 2, rgba.height // 2
        assert rgba.getpixel((cx, cy))[:3] == LOGO_RGB
    assert decode(out) == [URL]


def test_long_url_with_logo_still_decodes(tmp_path, logo):
    data = "https://example.com/" + "x" * 250
    out = tmp_path / "long.png"
    generate_qr_with_logo(data, str(logo), str(out), border_radius=30)
    assert decode(out) == [data]


def test_border_radius_makes_corners_transparent(tmp_path):
    out = tmp_path / "rounded.png"
    generate_qr_with_logo(URL, None, str(out), border_radius=30)
    with Image.open(out) as image:
        assert image.mode == "RGBA"
        assert image.getpixel((0, 0))[3] == 0
        assert image.getpixel((image.width // 2, 0))[3] == 255
    assert decode(out) == [URL]


def test_add_rounded_corners_masks_only_the_corners():
    square = Image.new("RGBA", (100, 100), (0, 0, 0, 255))
    rounded = add_rounded_corners(square, 20)
    assert rounded.size == square.size
    for corner in [(0, 0), (99, 0), (0, 99), (99, 99)]:
        assert rounded.getpixel(corner)[3] == 0
    assert rounded.getpixel((50, 50)) == (0, 0, 0, 255)


def test_get_images_from_folder_creates_missing_folder(tmp_path):
    folder = tmp_path / "images"
    assert get_images_from_folder(str(folder)) == []
    assert folder.is_dir()


def test_get_images_from_folder_filters_and_sorts(tmp_path):
    for name in ["b.PNG", "a.svg", "notes.txt", "c.webp"]:
        (tmp_path / name).write_bytes(b"")
    assert get_images_from_folder(str(tmp_path)) == ["a.svg", "b.PNG", "c.webp"]


def test_cli_without_logo_writes_file_named_after_url(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    answers = iter([URL, "y", "20"])  # URL, proceed without a logo, border radius
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(answers))

    qr_with_logo.main()

    out = tmp_path / "qr_https___example_com.png"
    assert out.is_file()
    assert decode(out) == [URL]
