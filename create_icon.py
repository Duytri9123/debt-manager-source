"""
Create the Windows ICO file from the application logo asset.
"""
import os

from PIL import Image


ICON_SIZES = [256, 128, 64, 48, 32, 16]


def square_canvas(image, size):
    """Fit a logo into a transparent square canvas."""
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    fitted = image.copy()
    fitted.thumbnail((size, size), Image.Resampling.LANCZOS)
    x = (size - fitted.width) // 2
    y = (size - fitted.height) // 2
    canvas.alpha_composite(fitted, (x, y))
    return canvas


def create_icon(source_path, output_path):
    """Create a multi-size ICO from the logo PNG."""
    logo = Image.open(source_path).convert("RGBA")
    base = square_canvas(logo, ICON_SIZES[0])

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    base.save(output_path, format="ICO", sizes=[(size, size) for size in ICON_SIZES])
    print(f"Icon created: {output_path}")
    print(f"Source logo: {source_path}")


if __name__ == "__main__":
    create_icon(
        os.path.join("src", "assets", "icon", "logo.png"),
        os.path.join("installer", "icon.ico"),
    )
