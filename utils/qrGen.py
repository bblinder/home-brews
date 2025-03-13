#!/usr/bin/env python3

import argparse
import sys
import os
import urllib.parse

try:
    import qrcode
except ImportError:
    print("qrcode not installed")
    sys.exit(1)


def generate_qr_code(data, output):
    """Generate a QR code image from the provided data and save it to the output file."""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)

    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    img.save(output)


def name_the_output_file(data):
    """Create a sanitized output file name based on the provided data."""

    # Parse the input data as a URL
    parsed_data = urllib.parse.urlparse(data)

    # Use the path component of the URL
    path = parsed_data.path if parsed_data.path else data

    # Use the basename of the path as the output file name
    output = os.path.basename(path)

    # Set a default file name if the output is empty
    if not output:
        output = "output"

    return output


def main():
    parser = argparse.ArgumentParser(description="Generate a QR code")
    parser.add_argument("data", help="The data to encode in the QR code", nargs="?")
    parser.add_argument(
        "-o",
        "--output",
        help="The output file name and destination (optional)",
        default=None,
    )
    args = parser.parse_args()

    data = args.data
    output = args.output

    if data is None:
        data = sys.stdin.read()

    if not data and sys.stdin.isatty():
        sys.stderr.write("Error: No data provided\n")
        parser.print_help()
        sys.exit(1)

    if output is None:
        output = f"{name_the_output_file(data)}.png"

    generate_qr_code(data, output)


if __name__ == "__main__":
    main()
