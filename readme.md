# Image to Pixel Art Converter

A Python command-line tool that transforms any image into stunning pixel art. This script replicates the core functionality of [Pixel Art Village](https://pixelartvillage.com), allowing you to modify pixel size, apply color restrictions (quantization), use custom hex color palettes, adjust image settings, and export in different resolutions.

## Features
* **Adjustable Pixel Size:** Control how "blocky" the image gets.
* **Custom Color Palettes:** Force the image to use a specific set of hex colors (e.g., Game Boy, 1-bit Macintosh, Synthwave).
* **Adaptive Color Reduction:** Restrict the image to a specific number of colors (e.g., 8, 16) using an adaptive palette.
* **Image Enhancements:** Tweak brightness, contrast, and saturation before pixelation to get the perfect lighting for your palette.
* **Automatic Output Organization (New!):** Automatically saves images to an `outputs/` folder, or any custom directory you specify, keeping your workspace clean.
* **Dual Export Modes:**
    * **Large (Default):** Scales the image back up to its original dimensions using nearest-neighbor resampling to keep the pixel edges perfectly crisp.
    * **Small:** Outputs the literal tiny resolution (e.g., a 64x64 actual image).
* **Pixel Grid Overlay:** Option to overlay a grid to help with cross-stitching or recreation.

## Prerequisites

You need Python installed on your system along with the **Pillow** (PIL) library.

Install Pillow using pip:
```bash
pip install Pillow
```

## Usage

Basic syntax:
```bash
python pixelart.py <input_image> <output_filename> [options]
```

### Examples

**1. Basic Conversion**
Pixelates the image into 8x8 blocks and saves it as `outputs/result.png`.
```bash
python pixelart.py photo.jpg result.png
```

**2. Custom Output Directory**
Saves the result in a specific folder (e.g., `gameboy_art/`). The script will create the folder if it doesn't exist.
```bash
python pixelart.py photo.jpg result.png --outdir gameboy_art --palette "#0f380f,#306230,#8bac0f,#9bbc0f"
```

**3. Custom Palettes**
Map your image to specific hex codes. Great for recreating retro console aesthetics.
* *1-Bit Black & White:*
  ```bash
  python pixelart.py photo.jpg result.png --size 8 --palette "#000000,#ffffff"
  
```

**4. Change Pixel Size & Limit Adaptive Colors**
Creates larger 12x12 pixel blocks and reduces the image to a 16-color palette.
```bash
python pixelart.py photo.jpg result.png --size 12 --colors 16
```

**5. Adjust Colors & Add a Grid**
Boosts saturation and contrast by 20%, makes blocks 10px wide, and overlays a grid.
```bash
python pixelart.py photo.jpg result.png --size 10 --sat 1.2 --contrast 1.2 --grid
```

**6. Export Actual Tiny Resolution ("Small Download")**
Instead of scaling the blocky image up so it looks normal in a standard photo viewer, it creates the raw, scaled-down pixel art image.
```bash
python pixelart.py photo.jpg result.png --size 8 --small
```

## Command-Line Arguments

| Argument     | Type    | Default   | Description |
|--------------|---------|-----------|-------------|
| `input`      | String  | Required  | Path to the original input image. |
| `output`     | String  | Required  | Filename to save the generated pixel art image (e.g., `result.png`). |
| `--outdir`   | String  | `outputs` | **New:** Directory to save the image. Will be created automatically if missing. |
| `--size`     | Integer | `8`       | Size of the pixel blocks (higher = more pixelated). |
| `--colors`   | Integer | `None`    | Number of adaptive colors to reduce the image to (ignored if `--palette` is used). |
| `--palette`  | String  | `None`    | Comma-separated hex colors to force a custom palette (e.g., `"#FF0000,#00FF00"`). |
| `--bright`   | Float   | `1.0`     | Brightness multiplier (1.0 = no change, <1.0 = darker, >1.0 = brighter). |
| `--contrast` | Float   | `1.0`     | Contrast multiplier (1.0 = no change). |
| `--sat`      | Float   | `1.0`     | Color saturation multiplier (1.0 = no change). |
| `--small`    | Flag    | False     | If included, downloads the image at its actual tiny pixel resolution. |
| `--grid`     | Flag    | False     | If included, overlays a grid over the pixel blocks (requires large scale output). |

## How it Works
1.  **Downscaling:** The script mathematically shrinks the image.
2.  **Nearest Neighbor Resampling:** Unlike standard scaling (which blurs pixels to make them smooth), this method strictly duplicates exact colors, creating sharp, blocky "pixel art" squares.
3.  **Quantization:** Analyzes the image and groups similar colors together to map the image down to a strict number of colors (when `--colors` is used), or maps the image's pixels to the nearest match in a user-provided hex list (when `--palette` is used).