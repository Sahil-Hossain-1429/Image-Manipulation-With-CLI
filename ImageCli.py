#!/usr/bin/env python3
"""
imgtool - A polished command-line image processing tool.

Same functionality as the original script, with a redesigned,
responsive terminal UI built on `rich`.
"""

import os
import sys
import time
import argparse

import cv2
import argcomplete

from rich.console import Console
from rich.theme import Theme
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.align import Align
from rich.rule import Rule
from rich.box import ROUNDED, HEAVY
from rich.traceback import install as install_rich_traceback

install_rich_traceback(show_locals=False)

# --------------------------------------------------------------------------
# Theme & console
# --------------------------------------------------------------------------

THEME = Theme(
    {
        "brand": "bold cyan",
        "accent": "bold magenta",
        "ok": "bold green",
        "warn": "bold yellow",
        "err": "bold red",
        "muted": "grey62",
        "value": "bold white",
        "label": "cyan",
        "step": "bold blue",
    }
)

console = Console(theme=THEME, highlight=False)

ICON_OK = "[ok]\u2714[/ok]"
ICON_ERR = "[err]\u2716[/err]"
ICON_WARN = "[warn]\u26a0[/warn]"
ICON_ARROW = "\u2192"
ICON_IMAGE = "\U0001f5bc"
ICON_SAVE = "\U0001f4be"
ICON_INFO = "\u2139"
ICON_GEAR = "\u2699"
ICON_SPARK = "\u2728"


def term_width():
    return console.size.width


def size_class():
    """Classify terminal width into small / medium / large."""
    w = term_width()
    if w < 70:
        return "small"
    if w < 110:
        return "medium"
    return "large"


# --------------------------------------------------------------------------
# Banner / header
# --------------------------------------------------------------------------

def print_banner():
    sc = size_class()

    if sc == "small":
        title = Text("imgtool", style="brand", justify="center")
        subtitle = Text("image processing CLI", style="muted", justify="center")
        console.print(Panel(Text.assemble(title, "\n", subtitle), box=ROUNDED, border_style="brand"))
        return

    title = Text()
    title.append(f"{ICON_SPARK} ", style="accent")
    title.append("imgtool", style="brand")
    title.append("  ", style="")
    title.append("\u2014 command-line image processing", style="muted")

    console.print(Panel(Align.center(title), box=HEAVY, border_style="brand", padding=(1, 2)))


# --------------------------------------------------------------------------
# Helpers: messages
# --------------------------------------------------------------------------

def success(msg):
    console.print(f"  {ICON_OK} {msg}")


def error(msg):
    console.print(f"  {ICON_ERR} [err]{msg}[/err]")


def warn(msg):
    console.print(f"  {ICON_WARN} [warn]{msg}[/warn]")


def info(msg):
    console.print(f"  [muted]{ICON_INFO}[/muted] {msg}")


def step(label, detail=""):
    line = f"  [step]{ICON_GEAR}[/step] [label]{label}[/label]"
    if detail:
        line += f"  [muted]{detail}[/muted]"
    console.print(line)


# --------------------------------------------------------------------------
# Progress helper for any "operation" with a tiny simulated bar
# (keeps real work synchronous & instant, but gives premium feedback)
# --------------------------------------------------------------------------

def run_with_progress(description, func, *args, **kwargs):
    with Progress(
        SpinnerColumn(style="brand"),
        TextColumn("[label]{task.description}[/label]"),
        BarColumn(bar_width=None, complete_style="brand", finished_style="ok"),
        TimeElapsedColumn(),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task(description, total=100)
        result = func(*args, **kwargs)
        # quick visual fill — real work already happened above
        for _ in range(20):
            progress.update(task, advance=5)
            time.sleep(0.005)
    return result


# --------------------------------------------------------------------------
# Core image functions (logic unchanged from original, only messaging styled)
# --------------------------------------------------------------------------

def load_image(filename):
    """Load image from disk"""
    image = cv2.imread(filename)

    if image is None:
        error(f"Could not load image '{filename}'")
        sys.exit(1)

    success(f"Loaded [value]{filename}[/value]")
    return image


def generate_output_filename(args):
    """Generate output filename based on applied operations"""
    operations = []

    if args.resize:
        operations.append("resize")
    if args.crop:
        operations.append("crop")
    if args.flip:
        if args.flip == "h":
            operations.append("flipH")
        elif args.flip == "v":
            operations.append("flipV")
        elif args.flip == "b":
            operations.append("flipB")
    if args.rotate:
        operations.append(f"rotate{args.rotate}")
    if args.grayscale:
        operations.append("grayscale")
    if args.convert_rgb:
        operations.append("rgb")
    if args.convert_bgr:
        operations.append("bgr")

    if not operations:
        operations.append("output")

    operation_name = "_".join(operations)

    _, ext = os.path.splitext(args.input_file)

    base_filename = f"{operation_name}Output"
    output_filename = f"{base_filename}{ext}"

    counter = 1
    while os.path.exists(output_filename):
        output_filename = f"{base_filename}{counter}{ext}"
        counter += 1

    return output_filename


def save_image(image, output_path):
    """Save image to disk"""
    is_success = cv2.imwrite(output_path, image)

    if not is_success:
        error(f"Could not save image to '{output_path}'")
        sys.exit(1)

    console.print()
    console.print(
        Panel(
            f"{ICON_SAVE}  Saved to [value]{output_path}[/value]",
            box=ROUNDED,
            border_style="ok",
            padding=(0, 2),
        )
    )


def show_image_info(image):
    """Display image metadata as a responsive table/panel"""
    height, width = image.shape[:2]
    channels = 1 if len(image.shape) == 2 else image.shape[2]
    dtype = image.dtype
    size_mb = image.nbytes / (1024 * 1024)

    sc = size_class()

    table = Table(
        box=None,
        show_header=False,
        padding=(0, 2, 0, 0),
        expand=(sc != "large"),
    )
    table.add_column("Property", style="label", no_wrap=True)
    table.add_column("Value", style="value")

    table.add_row("Width", f"{width} px")
    table.add_row("Height", f"{height} px")
    table.add_row("Channels", str(channels))
    table.add_row("Data type", str(dtype))
    table.add_row("Memory size", f"{size_mb:.2f} MB")

    title = f"{ICON_IMAGE} Image Information"
    console.print()
    console.print(Panel(table, title=title, title_align="left", border_style="brand", box=ROUNDED))


def validate_args(args):
    if not os.path.exists(args.input_file):
        error(f"File '{args.input_file}' does not exist")
        sys.exit(1)

    if args.resize:
        width, height = args.resize
        if width <= 0 or height <= 0:
            error("Resize dimensions must be positive")
            sys.exit(1)

    if args.crop:
        x, y, width, height = args.crop
        if width <= 0 or height <= 0:
            error("Crop width/height must be positive")
            sys.exit(1)


# --------------------------------------------------------------------------
# Image operations (unchanged logic)
# --------------------------------------------------------------------------

def crop_image(image, x, y, width, height):
    cropped_image = image[y:y + height, x:x + width]
    return cropped_image


def resize_image(image, width, height):
    return cv2.resize(image, (width, height))


def flip_image(image, direction):
    if direction == "h":
        return cv2.flip(image, 1)
    elif direction == "v":
        return cv2.flip(image, 0)
    else:
        return cv2.flip(image, -1)


def rotate_image(image, angle):
    if angle == 90:
        return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    elif angle == 180:
        return cv2.rotate(image, cv2.ROTATE_180)
    else:
        return cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)


def grayscale_image(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def convert_bgr_image(image):
    return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)


def convert_rgb_image(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


FLIP_LABELS = {"h": "Horizontal", "v": "Vertical", "b": "Horizontal + Vertical"}


# --------------------------------------------------------------------------
# Pipeline summary table (shown before processing)
# --------------------------------------------------------------------------

def print_pipeline_summary(args):
    sc = size_class()
    ops = []

    if args.resize:
        ops.append(("Resize", f"{args.resize[0]} x {args.resize[1]} px"))
    if args.crop:
        x, y, w, h = args.crop
        ops.append(("Crop", f"x={x}, y={y}, w={w}, h={h}"))
    if args.flip:
        ops.append(("Flip", FLIP_LABELS[args.flip]))
    if args.rotate:
        ops.append(("Rotate", f"{args.rotate}\u00b0"))
    if args.grayscale:
        ops.append(("Grayscale", "enabled"))
    if args.convert_rgb:
        ops.append(("Convert", "BGR \u2192 RGB"))
    if args.convert_bgr:
        ops.append(("Convert", "RGB \u2192 BGR"))

    if not ops:
        return

    table = Table(
        box=None,
        show_header=True,
        header_style="accent",
        expand=(sc != "large"),
    )
    table.add_column("#", style="muted", width=3, justify="right")
    table.add_column("Operation", style="label")
    table.add_column("Details", style="value")

    for i, (name, detail) in enumerate(ops, start=1):
        table.add_row(str(i), name, detail)

    console.print()
    console.print(Panel(table, title=f"{ICON_GEAR} Pipeline", title_align="left", border_style="muted"))
    console.print()


# --------------------------------------------------------------------------
# Argument parser
# --------------------------------------------------------------------------

def create_parser():
    parser = argparse.ArgumentParser(
        prog="imgtool",
        description="A polished command-line image processing tool.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("input_file", help="Path to input image file")
    parser.add_argument("-o", "--output", help="Custom output file path (optional)")
    parser.add_argument("--info", action="store_true", help="Show image metadata and exit")
    parser.add_argument(
        "--resize", nargs=2, type=int, metavar=("WIDTH", "HEIGHT"), help="Resize image"
    )
    parser.add_argument(
        "--crop",
        nargs=4,
        type=int,
        metavar=("X", "Y", "WIDTH", "HEIGHT"),
        help="Crop image",
    )
    parser.add_argument(
        "--flip", choices=["h", "v", "b"], help="Flip direction: horizontal, vertical, or both"
    )
    parser.add_argument(
        "--rotate", type=int, choices=[90, 180, 270], help="Rotation angle (90, 180, or 270)"
    )
    parser.add_argument("--grayscale", action="store_true", help="Convert to grayscale")
    parser.add_argument("--convert_rgb", action="store_true", help="Convert image to RGB")
    parser.add_argument("--convert_bgr", action="store_true", help="Convert image to BGR")
    parser.add_argument(
        "--no-banner", action="store_true", help="Suppress the startup banner"
    )

    return parser


# --------------------------------------------------------------------------
# Main processing pipeline
# --------------------------------------------------------------------------

def process_image(args):
    image = load_image(args.input_file)

    if args.info:
        show_image_info(image)
        return

    print_pipeline_summary(args)

    if args.resize:
        width, height = args.resize
        image = run_with_progress(
            f"Resizing {ICON_ARROW} {width}x{height}", resize_image, image, width, height
        )
        success(f"Resized to [value]{width} x {height}[/value]")

    if args.crop:
        x, y, width, height = args.crop
        image = run_with_progress("Cropping image", crop_image, image, x, y, width, height)
        success(f"Cropped [value]x={x}, y={y}, w={width}, h={height}[/value]")

    if args.flip:
        image = run_with_progress("Flipping image", flip_image, image, args.flip)
        success(f"Flipped: [value]{FLIP_LABELS[args.flip]}[/value]")

    if args.rotate:
        image = run_with_progress(f"Rotating {args.rotate}\u00b0", rotate_image, image, args.rotate)
        success(f"Rotated [value]{args.rotate}\u00b0[/value]")

    if args.grayscale:
        image = run_with_progress("Converting to grayscale", grayscale_image, image)
        success("Converted to [value]grayscale[/value]")

    if args.convert_rgb:
        image = run_with_progress("Converting BGR \u2192 RGB", convert_rgb_image, image)
        success("Converted [value]BGR \u2192 RGB[/value]")

    if args.convert_bgr:
        image = run_with_progress("Converting RGB \u2192 BGR", convert_bgr_image, image)
        success("Converted [value]RGB \u2192 BGR[/value]")

    console.print()
    save_image(image, args.output)


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------

def main():
    parser = create_parser()
    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    if not args.no_banner:
        print_banner()
        console.print()

    if args.output is None:
        args.output = generate_output_filename(args)

    try:
        validate_args(args)
        process_image(args)
    except KeyboardInterrupt:
        console.print()
        warn("Interrupted by user.")
        sys.exit(130)
    except Exception as exc:  # noqa: BLE001
        error(f"Unexpected error: {exc}")
        sys.exit(1)

    console.print()
    console.print(Rule(style="muted"))


if __name__ == "__main__":
    main()