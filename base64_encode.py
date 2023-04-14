#!/usr/bin/env python3
"""
Base64 encode an image and output the element based on the specified format.

Usage:
    Base64_encode.py [options] [image]
"""

import argparse
import base64
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("image", nargs="?", help="path to image file")
parser.add_argument("--html", action="store_true", help="output HTML")
parser.add_argument("--markdown", action="store_true", help="output Markdown")
parser.add_argument("--json", action="store_true", help="output JSON")
args = parser.parse_args()

image_formats = {
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "gif": "image/gif",
    "svg": "image/svg+xml",
}


def get_image_format(path):
    """Get the image format from the file extension."""
    return path.split(".")[-1].lower()


def get_image_data_url(image_data, mime_type):
    """Get the image data URL."""
    # mime_type = image_formats[image_format]
    encoded_string = base64.b64encode(image_data).decode("utf-8")
    data_url = f"data:{mime_type};base64,{encoded_string}"
    return data_url


def output_html(img_element):
    """Output the HTML."""
    return f'<img src="{img_element}">'


def output_markdown(img_element):
    """Output the Markdown."""
    return f"![image]({img_element})"


def output_json(img_element):
    """Output the JSON."""
    return f'{{"image": "{img_element}"}}'


def main():
    """Read from a file or stdin and output the encoded string."""
    if args.image:
        with open(args.image, "rb") as image:
            image_data = image.read()
            image_format = get_image_format(args.image)
            mime_type = image_formats[image_format]
    else:
        image_data = sys.stdin.buffer.read()
        mime_type = "image/png"
    data_url = get_image_data_url(image_data, mime_type)
    if args.html:
        print(output_html(data_url))
    elif args.markdown:
        print(output_markdown(data_url))
    elif args.json:
        print(output_json(data_url))
    else:
        print("No output format specified. Use --html, --markdown, or --json.")


if __name__ == "__main__":
    main()
