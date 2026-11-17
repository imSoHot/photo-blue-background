#!/usr/bin/env python3
"""Composite a cut-out (transparent RGBA) foreground onto a solid blue background.

Default background color is RGB(67, 142, 219) — the standard ID-photo blue.
The input MUST have an alpha channel (transparent background); typically the
output of the `matting` operation of buddy-image-processing. If the input has
no usable alpha channel, the script exits with a clear error because a solid
color replacement is impossible without a mask.
"""

import argparse
import os
import subprocess
import sys


def _ensure_pillow():
    try:
        import PIL  # noqa: F401
        return
    except ImportError:
        pass
    print("Pillow not found, installing it automatically...", file=sys.stderr)
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "Pillow", "--quiet"]
        )
    except Exception as exc:  # noqa: BLE001
        print(
            "Failed to install Pillow automatically: %s\n"
            "Please run: %s -m pip install Pillow" % (exc, sys.executable),
            file=sys.stderr,
        )
        sys.exit(2)


_ensure_pillow()

from PIL import Image  # noqa: E402


DEFAULT_COLOR = (67, 142, 219)


def parse_color(text):
    """Parse 'R,G,B' string into a tuple of ints, validate 0-255."""
    parts = text.replace(" ", "").split(",")
    if len(parts) != 3:
        raise argparse.ArgumentTypeError(
            "color must be three comma-separated integers, e.g. 67,142,219"
        )
    try:
        color = tuple(int(p) for p in parts)
    except ValueError:
        raise argparse.ArgumentTypeError("color channels must be integers")
    for channel in color:
        if channel < 0 or channel > 255:
            raise argparse.ArgumentTypeError("color channels must be 0-255")
    return color


def build_parser():
    parser = argparse.ArgumentParser(
        description="Composite a transparent cut-out onto a solid blue background."
    )
    parser.add_argument(
        "--input", "-i", required=True,
        help="Path to the transparent (RGBA) cut-out image.",
    )
    parser.add_argument(
        "--output", "-o",
        help="Output path. Defaults to <input>_blue.<ext> next to the input.",
    )
    parser.add_argument(
        "--color", "-c", type=parse_color, default=DEFAULT_COLOR,
        help="Background color as R,G,B. Default: 67,142,219 (ID-photo blue).",
    )
    parser.add_argument(
        "--format", "-f",
        help="Output image format (e.g. JPEG, PNG). Inferred from --output suffix.",
    )
    return parser


def default_output(input_path):
    base, ext = os.path.splitext(input_path)
    if not ext:
        ext = ".png"
    return "%s_blue%s" % (base, ext)


def main(argv=None):
    args = build_parser().parse_args(argv)
    input_path = os.path.abspath(args.input)
    if not os.path.isfile(input_path):
        print("Input file not found: %s" % input_path, file=sys.stderr)
        sys.exit(1)

    output_path = os.path.abspath(args.output or default_output(input_path))
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with Image.open(input_path) as img:
        foreground = img.convert("RGBA")

    alpha = foreground.getchannel("A")
    if alpha.getextrema()[1] == 255 and alpha.getextrema()[0] == 255:
        print(
            "Input image is fully opaque — no transparent background detected. "
            "Run the `matting` operation first to cut out the subject.",
            file=sys.stderr,
        )
        sys.exit(3)

    background = Image.new("RGBA", foreground.size, args.color + (255,))
    merged = Image.alpha_composite(background, foreground).convert("RGB")

    save_kwargs = {}
    fmt = args.format
    if not fmt:
        fmt = os.path.splitext(output_path)[1].lstrip(".").upper() or "PNG"
    fmt = fmt.upper()
    if fmt in ("JPEG", "JPG"):
        save_kwargs["quality"] = 95
    merged.save(output_path, format=fmt, **save_kwargs)

    print(
        "Saved composite to %s (background RGB%s, size %dx%d)"
        % (output_path, args.color, merged.width, merged.height)
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
