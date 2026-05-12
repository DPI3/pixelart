import argparse
from PIL import Image, ImageEnhance, ImageDraw

def apply_custom_palette(img, hex_colors):
    """Maps an image to a specific list of hex colors."""
    rgb_colors = []
    # Convert hex codes (e.g., "#FF0000") to RGB values (255, 0, 0)
    for hex_code in hex_colors:
        hex_code = hex_code.lstrip('#')
        rgb_colors.extend(tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4)))

    # A Pillow palette must have exactly 768 integers (256 colors * 3 channels)
    # We pad the rest of the list with zeroes if we provide fewer than 256 colors
    rgb_colors = rgb_colors + [0] * (768 - len(rgb_colors))

    # Create a 1x1 dummy image to store the palette
    palette_image = Image.new('P', (1, 1))
    palette_image.putpalette(rgb_colors)

    # Convert the original image to use this palette
    # dither=0 (NONE) ensures crisp, unblended pixel art colors
    return img.quantize(palette=palette_image, dither=0).convert('RGB')


def create_pixel_art(input_path, output_path, pixel_size=8, num_colors=None, custom_palette=None,
                     brightness=1.0, contrast=1.0, saturation=1.0, 
                     scale_up=True, add_grid=False):
    
    # 1. Open the image
    try:
        img = Image.open(input_path).convert('RGB')
    except Exception as e:
        print(f"Error opening image: {e}")
        return

    # 2. Apply Adjustments
    if brightness != 1.0:
        img = ImageEnhance.Brightness(img).enhance(brightness)
    if contrast != 1.0:
        img = ImageEnhance.Contrast(img).enhance(contrast)
    if saturation != 1.0:
        img = ImageEnhance.Color(img).enhance(saturation)

    # 3. Calculate target pixelated dimensions
    orig_width, orig_height = img.size
    pixel_size = max(1, int(pixel_size))
    small_width = max(1, orig_width // pixel_size)
    small_height = max(1, orig_height // pixel_size)
    
    # 4. Pixelate by downscaling
    small_img = img.resize((small_width, small_height), Image.Resampling.NEAREST)
    
    # 5. Color Palette Processing
    if custom_palette:
        # Apply strict custom hex colors
        small_img = apply_custom_palette(small_img, custom_palette)
    elif num_colors is not None and num_colors > 0:
        # Fallback to the adaptive method if just a number is provided
        small_img = small_img.convert('P', palette=Image.Palette.ADAPTIVE, colors=num_colors)
        small_img = small_img.convert('RGB')
        
    # 6. Output Scaling
    if scale_up:
        final_img = small_img.resize(
            (small_width * pixel_size, small_height * pixel_size), 
            Image.Resampling.NEAREST
        )
    else:
        final_img = small_img
        
    # 7. Add Grid
    if add_grid and scale_up:
        draw = ImageDraw.Draw(final_img)
        grid_color = (0, 0, 0)
        for x in range(0, final_img.width, pixel_size):
            draw.line([(x, 0), (x, final_img.height)], fill=grid_color)
        for y in range(0, final_img.height, pixel_size):
            draw.line([(0, y), (final_img.width, y)], fill=grid_color)

    # 8. Save
    final_img.save(output_path)
    print(f"Success! Pixel art saved to '{output_path}'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert an image to Pixel Art")
    parser.add_argument("input", help="Path to input image")
    parser.add_argument("output", help="Path to save output image")
    parser.add_argument("--size", type=int, default=8, help="Pixel block size")
    parser.add_argument("--colors", type=int, default=None, help="Number of adaptive colors")
    parser.add_argument("--palette", type=str, default=None, help="Comma-separated hex colors (e.g., '#FF0000,#00FF00')")
    parser.add_argument("--bright", type=float, default=1.0, help="Brightness multiplier")
    parser.add_argument("--contrast", type=float, default=1.0, help="Contrast multiplier")
    parser.add_argument("--sat", type=float, default=1.0, help="Saturation multiplier")
    parser.add_argument("--small", action="store_true", help="Download 'Small' version")
    parser.add_argument("--grid", action="store_true", help="Add a grid to the image")
    
    args = parser.parse_args()
    
    # Parse the custom palette string into a list
    hex_palette_list = args.palette.split(',') if args.palette else None

    create_pixel_art(
        input_path=args.input,
        output_path=args.output,
        pixel_size=args.size,
        num_colors=args.colors,
        custom_palette=hex_palette_list,
        brightness=args.bright,
        contrast=args.contrast,
        saturation=args.sat,
        scale_up=not args.small,
        add_grid=args.grid
    )