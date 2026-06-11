"""
Create a simple ICO file for Debt Manager
This creates a basic 256x256 icon with a professional design
"""
import struct
from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(output_path, size=256):
    """Create a professional icon for Debt Manager"""
    
    # Create image with gradient background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw rounded rectangle background (dark blue)
    margin = 20
    radius = 40
    draw.rounded_rectangle(
        [margin, margin, size-margin, size-margin],
        radius=radius,
        fill=(30, 64, 175)  # Dark blue
    )
    
    # Draw inner rounded rectangle (lighter blue)
    inner_margin = 35
    draw.rounded_rectangle(
        [inner_margin, inner_margin, size-inner_margin, size-inner_margin],
        radius=radius-10,
        fill=(59, 130, 246)  # Lighter blue
    )
    
    # Draw "DM" text in white
    try:
        font = ImageFont.truetype("arial.ttf", size=120)
    except:
        font = ImageFont.load_default()
    
    # Center text
    text = "DM"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size - text_width) // 2
    y = (size - text_height) // 2 - 10
    
    draw.text((x, y), text, fill=(255, 255, 255), font=font)
    
    # Add dollar sign at bottom
    try:
        small_font = ImageFont.truetype("arial.ttf", size=60)
    except:
        small_font = ImageFont.load_default()
    
    dollar_text = "$"
    dollar_bbox = draw.textbbox((0, 0), dollar_text, font=small_font)
    dollar_width = dollar_bbox[2] - dollar_bbox[0]
    dollar_x = (size - dollar_width) // 2
    dollar_y = size - 100
    
    draw.text((dollar_x, dollar_y), dollar_text, fill=(255, 255, 255), font=small_font)
    
    # Save as ICO
    img.save(output_path, format='ICO', sizes=[(size, size)])
    print(f"✅ Icon created: {output_path}")
    print(f"   Size: {size}x{size}")

if __name__ == "__main__":
    icon_path = os.path.join("installer", "icon.ico")
    create_icon(icon_path)
