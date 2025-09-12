# File: functions_folder/image_optimizer.py
from PIL import Image

import argparse
import os

def image_optimizer(image_path, resize_dims=(800, 600), output_format='JPEG', quality=85):
    """
    Optimizes an image by resizing, converting format, and compressing.

    Parameters:
    - image_path (str): Path to the input image
    - resize_dims (tuple): (width, height) to resize to. Default: (800, 600)
    - output_format (str): Format to convert to. Default: 'JPEG'
    - quality (int): Compression quality (1–100). Default: 85

    Returns:
    - dict: Optimization results
    """
    try:
        img = Image.open(image_path)
        original_size = os.path.getsize(image_path)

        # Resize
        if resize_dims:
            img = img.resize(resize_dims, Image.LANCZOS)

        # Format
        ext = output_format.lower()
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        
        # Save directly to static/
        static_dir = "static"
        os.makedirs(static_dir, exist_ok=True)
        optimized_path = os.path.join(static_dir, f"{base_name}_optimized.{ext}")

        # Save with compression
        img.save(optimized_path, format=output_format, optimize=True, quality=quality)
        optimized_size = os.path.getsize(optimized_path)

        return {
            "original_size": original_size,
            "optimized_size": optimized_size,
            "compression_ratio": round((1 - optimized_size / original_size) * 100, 2),
            "optimized_path": optimized_path,
            "status": "Success"
        }

    except Exception as e:
        return {"error": f"Image optimization failed: {e}"}
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Image Optimizer CLI")
    parser.add_argument("image_path", help="Path to the image file")
    parser.add_argument("--resize", nargs=2, type=int, metavar=('WIDTH', 'HEIGHT'), help="Resize dimensions")
    parser.add_argument("--format", type=str, help="Convert image format (JPEG, PNG, WEBP, etc.)")
    parser.add_argument("--quality", type=int, help="Compression quality (1–100)")

    args = parser.parse_args()
    resize_dims = tuple(args.resize) if args.resize else (800, 600)
    output_format = args.format if args.format else 'JPEG'
    quality = args.quality if args.quality else 85

    result = image_optimizer(
        image_path=args.image_path,
        resize_dims=resize_dims,
        output_format=output_format,
        quality=quality
    )

    print(result)