#!/usr/bin/env python3
"""
Profile Photo Processing with Smart Cropping
Crops mirror reflection, focuses on upper body, removes background
"""

from PIL import Image, ImageDraw, ImageFilter
import numpy as np
from pathlib import Path
import sys

def remove_background(img: Image.Image) -> Image.Image:
    """Remove background using rembg"""
    from rembg import remove
    from io import BytesIO
    
    print("🔄 Removing background...")
    
    # Convert image to bytes
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    # Remove background
    output_data = remove(img_byte_arr)
    
    # Convert back to image
    result = Image.open(BytesIO(output_data))
    return result


def crop_mirror_and_upper_body(img: Image.Image) -> Image.Image:
    """
    Crop to mirror area and focus on upper body
    Image is rotated 90 degrees (mirror on left side)
    """
    width, height = img.size
    
    print(f"📐 Original size: {width}x{height}")
    
    # First rotate the image 90 degrees clockwise to get portrait orientation
    print("🔄 Rotating image to portrait orientation...")
    img = img.rotate(-90, expand=True)
    width, height = img.size
    
    print(f"📐 After rotation: {width}x{height}")
    
    # The mirror appears to be in the center-left portion
    # Let's crop to focus on the mirror reflection
    # Approximate mirror boundaries (adjust as needed)
    
    # Horizontal: mirror is roughly from 15% to 60% of width
    left = int(width * 0.15)
    right = int(width * 0.60)
    
    # Vertical: focus on upper body (top 50% of image)
    top = int(height * 0.10)
    bottom = int(height * 0.60)
    
    print(f"✂️  Cropping to mirror area: left={left}, top={top}, right={right}, bottom={bottom}")
    
    cropped = img.crop((left, top, right, bottom))
    
    # Get original aspect ratio of cropped area
    crop_width, crop_height = cropped.size
    print(f"📐 Cropped size: {crop_width}x{crop_height}")
    
    # For a professional headshot, we want roughly 3:4 or 2:3 aspect ratio (portrait)
    # Calculate target dimensions maintaining aspect ratio
    # Use height as the anchor since it's already good (upper body)
    target_height = 800
    aspect_ratio = crop_width / crop_height
    target_width = int(target_height * aspect_ratio)
    
    print(f"📐 Aspect ratio: {aspect_ratio:.2f}")
    print(f"📐 Resizing to: {target_width}x{target_height} (maintaining aspect ratio)")
    
    cropped = cropped.resize((target_width, target_height), Image.Resampling.LANCZOS)
    
    print(f"📐 Resized to: {cropped.size}")
    
    # Now create the 300x300 headshot crop
    # From top: go down 300 pixels
    # From center: extend left and right by 150 pixels (total 300px width)
    crop_w, crop_h = cropped.size
    center_x = crop_w // 2
    
    # Define the 300x300 box
    headshot_left = center_x - 150
    headshot_top = 0
    headshot_right = center_x + 150
    headshot_bottom = 300
    
    print(f"✂️  Creating 300x300 headshot: left={headshot_left}, top={headshot_top}, right={headshot_right}, bottom={headshot_bottom}")
    
    # Make sure we don't go out of bounds
    if headshot_left < 0:
        headshot_left = 0
        headshot_right = 300
    if headshot_right > crop_w:
        headshot_right = crop_w
        headshot_left = crop_w - 300
    
    headshot = cropped.crop((headshot_left, headshot_top, headshot_right, headshot_bottom))
    
    print(f"📐 Final headshot size: {headshot.size}")
    
    return headshot


def create_gradient_background(width: int, height: int, color1: tuple, color2: tuple) -> Image.Image:
    """Create a gradient background"""
    background = Image.new('RGB', (width, height), color1)
    draw = ImageDraw.Draw(background)
    
    for y in range(height):
        ratio = y / height
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    return background


def create_solid_background(width: int, height: int, color: tuple) -> Image.Image:
    """Create a solid color background"""
    return Image.new('RGB', (width, height), color)


def create_blurred_background(width: int, height: int, base_color: tuple) -> Image.Image:
    """Create a blurred bokeh-style background"""
    background = Image.new('RGB', (width, height), base_color)
    draw = ImageDraw.Draw(background)
    
    # Add bokeh effects
    np.random.seed(42)
    for _ in range(20):
        x = np.random.randint(0, width)
        y = np.random.randint(0, height)
        radius = np.random.randint(30, 100)
        
        color_var = tuple(min(255, c + np.random.randint(20, 50)) for c in base_color)
        draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=color_var)
    
    background = background.filter(ImageFilter.GaussianBlur(radius=50))
    
    return background


def combine_foreground_background(foreground: Image.Image, background: Image.Image) -> Image.Image:
    """Combine foreground (with alpha) and background"""
    if foreground.mode != 'RGBA':
        foreground = foreground.convert('RGBA')
    
    background = background.resize(foreground.size, Image.Resampling.LANCZOS)
    background = background.convert('RGBA')
    
    result = Image.alpha_composite(background, foreground)
    
    return result.convert('RGB')


def main():
    input_path = Path("input/profile_picture2.JPG")
    output_dir = Path("output/profile_options")
    output_dir.mkdir(exist_ok=True)
    
    if not input_path.exists():
        print(f"❌ Error: {input_path} not found!")
        sys.exit(1)
    
    print(f"📷 Loading image: {input_path}")
    original = Image.open(input_path)
    
    # Crop to mirror area and upper body
    cropped = crop_mirror_and_upper_body(original)
    
    # Save cropped version for review
    cropped.save(output_dir / "cropped_before_bg_removal.jpg", 'JPEG', quality=95)
    print("💾 Saved cropped version for review")
    
    # Remove background
    foreground = remove_background(cropped)
    
    print("\n🎨 Creating background variations...")
    
    width, height = foreground.size
    
    backgrounds = {
        "1_professional_blue_gradient": create_gradient_background(
            width, height,
            (37, 150, 190),  # CV blue accent
            (25, 100, 140)   # Darker blue
        ),
        "2_neutral_gray_gradient": create_gradient_background(
            width, height,
            (240, 240, 245),  # Light gray
            (200, 200, 210)   # Medium gray
        ),
        "3_solid_professional_blue": create_solid_background(
            width, height,
            (37, 150, 190)  # CV blue accent
        ),
        "4_solid_navy": create_solid_background(
            width, height,
            (30, 50, 80)  # Navy blue
        ),
        "5_bokeh_blue": create_blurred_background(
            width, height,
            (50, 120, 180)  # Medium blue
        ),
        "6_solid_light_gray": create_solid_background(
            width, height,
            (220, 225, 230)  # Light gray
        )
    }
    
    # Save variations
    for name, background in backgrounds.items():
        print(f"  ✓ Creating option: {name}")
        result = combine_foreground_background(foreground, background)
        output_path = output_dir / f"{name}.png"
        result.save(output_path, 'PNG', quality=95)
    
    print(f"\n✅ Complete! Created {len(backgrounds)} variations in {output_dir}/")
    print("\nOptions created:")
    for i, name in enumerate(backgrounds.keys(), 1):
        print(f"  {i}. {name.replace('_', ' ').title()}")
    
    # Save transparent background version
    foreground.save(output_dir / "0_no_background.png", 'PNG')
    print("\n📝 Also saved:")
    print("  - 0_no_background.png (transparent background)")
    print("  - cropped_before_bg_removal.jpg (review cropping)")


if __name__ == "__main__":
    main()
