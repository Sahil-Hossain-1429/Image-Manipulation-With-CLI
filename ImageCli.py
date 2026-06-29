#!/usr/bin/env python3

import os
import sys
import cv2   
import argparse
import argcomplete

def load_image(filename):
    """Load image from disk"""

    image = cv2.imread(filename)

    if image is None:
        print(f"Error: Could not load image '{filename}'")
        sys.exit(1)

    print("Image loaded successfully")

    return image

def save_image(image, output_path):
    """Save image to disk"""

    isSaveFileSuccess = cv2.imwrite(output_path, image)

    if not isSaveFileSuccess:
        print(f"Error: Could not save image to '{output_path}'")
        sys.exit(1)

    print(f"Image saved successfully to '{output_path}'")


def show_image_info(image):
    """Display image metadata"""

    height, width = image.shape[:2]

    if len(image.shape) == 2:
        channels = 1
    else:
        channels = image.shape[2]

    dtype = image.dtype

    size_mb = image.nbytes / (1024 * 1024)

    print("\n----- Image Information -----")
    print(f"Width       : {width} px")
    print(f"Height      : {height} px")
    print(f"Channels    : {channels}")
    print(f"Data Type   : {dtype}")
    print(f"Memory Size : {size_mb:.2f} MB")
    print("-----------------------------")


def validate_args(args):

    #file existence
    if not os.path.exists(args.input_file):
        print(f"Error: File '{args.input_file}' does not exits")
        sys.exit(1)

    # resize validation
    if args.resize:
        width, height = args.resize

        if width <= 0 or height <= 0:
            print("Error: Resize dimensions must be positive")
            sys.exit(1)

    # crop validaiton
    if args.crop:
        x, y, width, height = args.crop

        if width <= 0 or height <= 0:
            print("Error: Crop width/height must be positive")
            sys.exit(1)

    

def create_parser():
    parser = argparse.ArgumentParser(
        description="Image processing command line tool"
    )

    # positional argument (required)
    parser.add_argument(
        "input_file",
        help = "Path to input image file"
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Output file path (defaults to input file)"
    )

    parser.add_argument(
        "--info",
        action="store_true",
        help="Show image metadata and exit"
    )

    parser.add_argument(
        "--resize",
        nargs=2,
        type=int,
        metavar=("WIDTH","HEIGHT"),
        help="Resize image"
    )

    parser.add_argument(
        "--crop",
        nargs=4,
        type=int,
        metavar=("X","Y","WIDTH","HEIGHT"),
        help="Crop Image"
    )

    parser.add_argument(
        "--flip",
        choices=["horizontal", "vertical", "both"],
         help="Choose flip direction: horizontal, vertical, or both"
    )

    parser.add_argument(
        "--rotate",
        type=int,
        choices=[90,180,270],
        help="Rotation angle (90, 180, or 270)"
    )

    parser.add_argument(
        "--grayscale",
        action="store_true",
        help="Convert to grayscale"
    )

    parser.add_argument(
        "--convert-rgb",
        action="store_true",
        help="Convert image to RGB"
    )

    return parser

def process_image(args):
    """Main image processing piple"""
    image = load_image(args.input_file)

    if args.info:
        show_image_info(image)
        return
    
    if args.resize:
        print("Applying resize")

    if args.crop:
        print("Applying crop")

    if args.flip:
        print("Applying flip")

    if args.rotate:
        print("Applying rotation")

    if args.grayscale:
        print("Applying grayscale")

    if args.convert_rgb:
        print("Converting to RGB")

    save_image(image, args.output)

def main():
    parser = create_parser()

    argcomplete.autocomplete(parser)
    
    args = parser.parse_args()

    if args.output is None:
        args.output = "output_" + os.path.basename(args.input_file)

    validate_args(args)

    process_image(args)

if __name__ == "__main__":
    main()
