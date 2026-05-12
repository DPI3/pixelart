import os
import argparse
import urllib.parse
import re
from PIL import Image, ImageEnhance, ImageDraw

def parse_palette_input(palette_str):
    """
    Parses a palette input string. It can handle comma-separated hex codes,
    or extract colors directly from Coolors.co and Colorkit.co URLs.
    """
    if not palette_str:
        return None
    
    # Check if the input is a URL
    if palette_str.startswith('http://') or palette_str.startswith('https://'):
        parsed_url = urllib.parse.urlparse(palette_str)
        domain = parsed_url.netloc.lower()
        
        if 'coolors.co' in domain or 'colorkit.co' in domain:
            # Extract the path, removing leading/trailing slashes
            # e.g., /palette/264653-2a9d8f-e9c46a-f4a261-e76f51/
            path = parsed_url.path.strip('/')
            
            # The colors are always the last segment of the path
            segments = path.split('/')
            color_segment = segments[-1]
            
            # Split the string by hyphens to get individual hex codes
            hex_codes = color_segment.split('-')
            
            valid_hexes = []
            for code in hex_codes:
                # Validate that the extracted string is a 6-character hex code
                if re.match(r'^[0-9a-fA-F]{6}$', code):
                    valid_hexes.append(f"#{code}")
            
            if valid_hexes:
                print(f"Extracted {len(valid_hexes)} colors from URL.")
                return valid_hexes
            else:
                print(f"Warning: Could not extract valid colors from URL {palette_str}")
                return None
        else:
            print("Warning: Unsupported URL domain. Only coolors.co and colorkit.co are supported.")
            return None
    else:
        # Standard fallback: split by comma
        return palette_str.split(',')


def apply_custom_palette(img, hex_colors):
    """Maps an image to a specific list of hex colors."""
    rgb_colors = []
    for hex_code in hex_colors:
        hex_code = hex_code.lstrip('#')
        rgb_colors.extend(tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4)))

    rgb_colors = rgb_colors + [0] * (768 - len(rgb_colors))

    palette_image = Image.new('P', (1, 1))
    palette_image.putpalette(rgb_colors)

    return img.quantize(palette=palette_image, dither=0).convert('RGB')


def create_pixel_art(input_path, output_filename, output_dir="outputs", pixel_size=8, 
                     num_colors=None, custom_palette=None, brightness=1.0, 
                     contrast=1.0, saturation=1.0, scale_up=True, add_grid=False):
    
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

    # 3. Calculate target dimensions
    orig_width, orig_height = img.size
    pixel_size = max(1, int(pixel_size))
    small_width = max(1, orig_width // pixel_size)
    small_height = max(1, orig_height // pixel_size)
    
    # 4. Pixelate by downscaling
    small_img = img.resize((small_width, small_height), Image.Resampling.NEAREST)
    
    # 5. Color Palette Processing
    if custom_palette:
        small_img = apply_custom_palette(small_img, custom_palette)
    elif num_colors is not None and num_colors > 0:
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

    # 8. Handle Directories & Saving
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created new directory: '{output_dir}/'")

    final_output_path = os.path.join(output_dir, output_filename)

    final_img.save(final_output_path)
    print(f"Success! Pixel art saved to '{final_output_path}'.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert an image to Pixel Art")
    parser.add_argument("input", help="Path to input image")
    parser.add_argument("output", help="Filename for the output image (e.g. result.png)")
    parser.add_argument("--outdir", type=str, default="outputs", help="Directory to save the image (default: 'outputs')")
    parser.add_argument("--size", type=int, default=8, help="Pixel block size")
    parser.add_argument("--colors", type=int, default=None, help="Number of adaptive colors")
    parser.add_argument("--palette", type=str, default=None, help="Comma-separated hex colors OR a coolors.co/colorkit.co URL")
    parser.add_argument("--bright", type=float, default=1.0, help="Brightness multiplier")
    parser.add_argument("--contrast", type=float, default=1.0, help="Contrast multiplier")
    parser.add_argument("--sat", type=float, default=1.0, help="Saturation multiplier")
    parser.add_argument("--small", action="store_true", help="Download 'Small' version")
    parser.add_argument("--grid", action="store_true", help="Add a grid to the image")
    
    args = parser.parse_args()
    
    # Process the palette input (URL or String)
    hex_palette_list = parse_palette_input(args.palette)

    create_pixel_art(
        input_path=args.input,
        output_filename=args.output,
        output_dir=args.outdir,
        pixel_size=args.size,
        num_colors=args.colors,
        custom_palette=hex_palette_list,
        brightness=args.bright,
        contrast=args.contrast,
        saturation=args.sat,
        scale_up=not args.small,
        add_grid=args.grid
    )