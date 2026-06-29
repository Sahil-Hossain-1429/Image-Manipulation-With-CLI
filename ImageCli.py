#!/usr/bin/env python3

import os
import sys
import argparse
import argcomplete

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

def main():
    parser = create_parser()

    argcomplete.autocomplete(parser)
    
    args = parser.parse_args()

    if args.output is None:
        args.output = args.input_file

    validate_args(args)
    print(args)

if __name__ == "__main__":
    main()
