"""
QR Code Generator with optional centered logo and rounded corners.

Generates QR codes with or without a logo. Place your logo images in the
'images' folder (PNG, JPG, SVG, WebP, etc.).
"""

import os
import subprocess
import sys

import qrcode
from PIL import Image, ImageDraw
from qrcode.constants import ERROR_CORRECT_H


def convert_svg_to_image(svg_path: str) -> Image.Image:
    """Convert SVG to PIL Image using available tools."""
    import shutil
    
    # Try Inkscape first (most reliable)
    inkscape_path = shutil.which("inkscape")
    if inkscape_path:
        temp_png = svg_path.replace(".svg", "_temp.png")
        try:
            subprocess.run(
                [inkscape_path, svg_path, "--export-type=png", f"--export-filename={temp_png}", "-w", "500"],
                capture_output=True,
                check=True
            )
            img = Image.open(temp_png).convert("RGBA")
            os.remove(temp_png)
            return img
        except subprocess.CalledProcessError:
            pass
    
    # Try ImageMagick (magick convert)
    magick_path = shutil.which("magick")
    if magick_path:
        temp_png = svg_path.replace(".svg", "_temp.png")
        try:
            subprocess.run(
                [magick_path, "convert", "-background", "none", "-density", "300", svg_path, temp_png],
                capture_output=True,
                check=True
            )
            img = Image.open(temp_png).convert("RGBA")
            os.remove(temp_png)
            return img
        except subprocess.CalledProcessError:
            pass
    
    # No converter available
    print("\n❌ SVG conversion requires Inkscape or ImageMagick.")
    print("   Options:")
    print("   1. Install Inkscape: https://inkscape.org/release/")
    print("   2. Install ImageMagick: https://imagemagick.org/script/download.php")
    print("   3. Convert your SVG to PNG manually and use that instead.")
    sys.exit(1)


def get_images_from_folder(folder: str = "images") -> list[str]:
    """Get list of image files from the specified folder."""
    supported_extensions = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".svg")
    
    if not os.path.exists(folder):
        os.makedirs(folder)
        return []
    
    images = [
        f for f in os.listdir(folder)
        if f.lower().endswith(supported_extensions)
    ]
    return sorted(images)


def add_rounded_corners(image: Image.Image, radius: int) -> Image.Image:
    """Add rounded corners to an image."""
    # Create a mask with rounded corners
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle(
        [(0, 0), (image.size[0] - 1, image.size[1] - 1)],
        radius=radius,
        fill=255
    )
    
    # Apply the mask
    output = Image.new("RGBA", image.size, (255, 255, 255, 0))
    output.paste(image, mask=mask)
    return output


def generate_qr_with_logo(
    data: str,
    logo_path: str | None,
    output_path: str = "qr_with_logo.png",
    qr_box_size: int = 10,
    qr_border: int = 4,
    logo_scale: float = 0.2,
    border_radius: int = 0,
):
    """
    Generate a QR code with an optional logo in the center.

    :param data: Text/URL to encode in the QR code.
    :param logo_path: Path to the logo image.
    :param output_path: Path to save the final QR image.
    :param qr_box_size: Size of each QR pixel.
    :param qr_border: Border size of the QR code.
    :param logo_scale: Fraction of QR code size that logo should occupy (0–1).
    :param border_radius: Radius for rounded corners (0 = no rounding).
    """
    # Create QR Code
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_H,
        box_size=qr_box_size,
        border=qr_border,
    )
    qr.add_data(data)
    qr.make(fit=True)

    if logo_path:
        # Open and resize logo first to calculate center area
        if logo_path.lower().endswith(".svg"):
            logo = convert_svg_to_image(logo_path)
        else:
            logo = Image.open(logo_path).convert("RGBA")

        # Get QR matrix dimensions
        matrix_size = len(qr.modules)
        
        # Calculate logo size in modules (with padding)
        logo_module_size = int(matrix_size * logo_scale) + 4  # extra modules for padding
        
        # Clear center modules so QR data avoids the logo area
        center_start = (matrix_size - logo_module_size) // 2
        center_end = center_start + logo_module_size
        
        for row in range(center_start, center_end):
            for col in range(center_start, center_end):
                if 0 <= row < matrix_size and 0 <= col < matrix_size:
                    qr.modules[row][col] = False  # Set to white (no data)

    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")

    if logo_path:
        qr_width, qr_height = qr_img.size
        logo_size = int(min(qr_width, qr_height) * logo_scale)

        logo.thumbnail((logo_size, logo_size), Image.LANCZOS)

        # Calculate position (center)
        logo_w, logo_h = logo.size
        pos = ((qr_width - logo_w) // 2, (qr_height - logo_h) // 2)

        # Create white background box behind logo (with padding and rounded corners)
        padding = 8
        box_w = logo_w + padding * 2
        box_h = logo_h + padding * 2
        box_pos = (pos[0] - padding, pos[1] - padding)
        
        # Create rounded white box
        white_box = Image.new("RGBA", (box_w, box_h), (255, 255, 255, 0))
        box_draw = ImageDraw.Draw(white_box)
        box_radius = 15  # Rounded corners for the logo background
        box_draw.rounded_rectangle(
            [(0, 0), (box_w - 1, box_h - 1)],
            radius=box_radius,
            fill=(255, 255, 255, 255)
        )
        
        # Paste rounded white box onto QR code
        qr_img.paste(white_box, box_pos, mask=white_box)
        
        # Paste logo on top
        qr_img.paste(logo, pos, mask=logo)

    # Apply rounded corners if specified
    if border_radius > 0:
        qr_img = add_rounded_corners(qr_img, border_radius)

    # Save result
    qr_img.save(output_path)
    print(f"\n✅ QR code saved to: {output_path}")


def get_user_input() -> tuple[str, str | None, int]:
    """Get URL, optional logo selection, and border radius from user."""
    print("\n" + "=" * 50)
    print("       QR CODE GENERATOR WITH LOGO")
    print("=" * 50)
    
    # Get URL
    url = input("\n📎 Enter the URL to encode: ").strip()
    if not url:
        print("❌ URL cannot be empty.")
        sys.exit(1)
    
    # Get available images
    images = get_images_from_folder()
    if not images:
        print("\n⚠️  No images found in the 'images' folder.")
        print("   Add PNG/JPG/SVG/WebP/etc. files there or continue without a logo.")
        use_logo = input("Proceed without a logo? (y/N): ").strip().lower()
        if use_logo != "y":
            sys.exit(1)
        selected_logo = None
    else:
        print("\nAvailable logos:")
        for idx, img_name in enumerate(images, start=1):
            print(f" {idx}) {img_name}")
        print(f" {len(images) + 1}) No logo (generate plain QR)")
    
        choice = input("\nSelect a logo by number (or choose 'No logo'): ").strip()
        try:
            choice_idx = int(choice) - 1
            if choice_idx == len(images):
                selected_logo = None
            elif 0 <= choice_idx < len(images):
                selected_logo = os.path.join("images", images[choice_idx])
            else:
                raise ValueError
        except ValueError:
            print("❌ Invalid selection.")
            sys.exit(1)
    
    # Border radius
    while True:
        radius_input = input("Enter border radius (0 for square corners): ").strip()
        try:
            border_radius = int(radius_input)
            if border_radius >= 0:
                break
            print("   ⚠️  Border radius must be 0 or positive")
        except ValueError:
            print("   ⚠️  Please enter a valid number")
    
    return url, selected_logo, border_radius


def main():
    """Main entry point."""
    url, selected_logo, border_radius = get_user_input()
    
    # Generate output filename based on input
    safe_name = "".join(c if c.isalnum() else "_" for c in url[:30])
    output_path = f"qr_{safe_name}.png"
    
    print("\n⏳ Generating QR code...")
    print(f"   URL: {url}")
    print(f"   Logo: {selected_logo if selected_logo else 'None'}")
    print(f"   Border radius: {border_radius}px")
    
    generate_qr_with_logo(
        data=url,
        logo_path=selected_logo,
        output_path=output_path,
        logo_scale=0.2,
        border_radius=border_radius,
        qr_border=2,
    )


if __name__ == "__main__":
    main()
