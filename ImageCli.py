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

def generate_output_filename(args):
    """Generate output filename based on applied operations"""

    operations = []

    # standard flags
    if args.resize:
        operations.append("resize")

    if args.crop:
        operations.append("crop")

    # include flip choice
    if args.flip:
        if args.flip == "h":
            operations.append("flipH")
        elif args.flip == "v":
            operations.append("flipV")
        elif args.flip == "b":
            operations.append("flipB")

    # include rotation angle
    if args.rotate:
        operations.append(f"rotate{args.rotate}")

    if args.grayscale:
        operations.append("grayscale")

    if args.convert_rgb:
        operations.append("rgb")

    if args.convert_bgr:
        operations.append("bgr")

    # no operations
    if not operations:
        operations.append("output")

    operation_name = "_".join(operations)

    # preserve original extension
    _, ext = os.path.splitext(args.input_file)

    base_filename = f"{operation_name}Output"
    output_filename = f"{base_filename}{ext}"

    # check duplicates
    counter = 1
    while os.path.exists(output_filename):
        output_filename = f"{base_filename}{counter}{ext}"
        counter += 1

    return output_filename

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

    # file existence
    if not os.path.exists(args.input_file):
        print(f"Error: File '{args.input_file}' does not exist")
        sys.exit(1)

    # resize validation
    if args.resize:
        width, height = args.resize

        if width <= 0 or height <= 0:
            print("Error: Resize dimensions must be positive")
            sys.exit(1)

    # crop validation
    if args.crop:
        x, y, width, height = args.crop

        if width <= 0 or height <= 0:
            print("Error: Crop width/height must be positive")
            sys.exit(1)


def create_parser():
    parser = argparse.ArgumentParser(
        description="Image processing command line tool"
    )

    parser.add_argument(
        "input_file",
        help="Path to input image file"
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Custom output file path (optional)"
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
        metavar=("WIDTH", "HEIGHT"),
        help="Resize image"
    )

    parser.add_argument(
        "--crop",
        nargs=4,
        type=int,
        metavar=("X", "Y", "WIDTH", "HEIGHT"),
        help="Crop image"
    )

    parser.add_argument(
        "--flip",
        choices=["h", "v", "b"],
        help="Choose flip direction: horizontal, vertical, or both"
    )

    parser.add_argument(
        "--rotate",
        type=int,
        choices=[90, 180, 270],
        help="Rotation angle (90, 180, or 270)"
    )

    parser.add_argument(
        "--grayscale",
        action="store_true",
        help="Convert to grayscale"
    )

    parser.add_argument(
        "--convert_rgb",
        action="store_true",
        help="Convert image to RGB"
    )

    parser.add_argument(
        "--convert_bgr",
        action="store_true",
        help="Convert image to BGR"
    )

    return parser


def crop_image(image, x, y, width, height):
    """Crop image"""

    cropped_image = image[y:y + height, x:x + width]

    print(f"Image cropped: x={x}, y={y}, width={width}, height={height}")

    return cropped_image


def resize_image(image, width, height):
    """Resize image to specified dimensions"""

    resized_image = cv2.resize(image, (width, height))

    print(f"Image resized to {width} x {height}")

    return resized_image


def flip_image(image, direction):
    """Flip image based on the specified direction"""

    if direction == "h":
        flipped_image = cv2.flip(image, 1)
        print("Image flipped direction: Horizontal")

    elif direction == "v":
        flipped_image = cv2.flip(image, 0)
        print("Image flipped direction: Vertical")

    else:
        flipped_image = cv2.flip(image, -1)
        print("Image flipped direction: Both Horizontal and Vertical")

    return flipped_image


def rotate_image(image, angle):
    """Rotate image specified angle"""

    if angle == 90:
        rotated_image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

    elif angle == 180:
        rotated_image = cv2.rotate(image, cv2.ROTATE_180)

    else:
        rotated_image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)

    print(f"Image rotated: {angle} degrees")

    return rotated_image


def grayscale_image(image):
    """Convert image to grayscale"""

    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    print("Image converted to grayscale")

    return gray_image


def convert_bgr_image(image):
    """Convert image from RGB to BGR"""

    bgr_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    print("Image converted to BGR")

    return bgr_image


def convert_rgb_image(image):
    """Convert image from BGR to RGB"""

    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    print("Image converted to RGB")

    return rgb_image


def process_image(args):
    """Main image processing pipeline"""

    image = load_image(args.input_file)

    if args.info:
        show_image_info(image)
        return

    if args.resize:
        width, height = args.resize
        image = resize_image(image, width, height)

    if args.crop:
        x, y, width, height = args.crop
        image = crop_image(image, x, y, width, height)

    if args.flip:
        image = flip_image(image, args.flip)

    if args.rotate:
        image = rotate_image(image, args.rotate)

    if args.grayscale:
        image = grayscale_image(image)

    if args.convert_rgb:
        image = convert_rgb_image(image)

    if args.convert_bgr:
        image = convert_bgr_image(image)

    save_image(image, args.output)


def main():
    parser = create_parser()

    argcomplete.autocomplete(parser)

    args = parser.parse_args()

    # auto-generate output filename if user does not provide one
    if args.output is None:
        args.output = generate_output_filename(args)

    validate_args(args)

    process_image(args)


if __name__ == "__main__":
    main()
