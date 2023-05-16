#!/usr/bin/env python3
"""
Base64 encode an image and output the element based on the specified format.

Usage:
    Base64_encode.py [options] [image]
"""

import argparse
import base64
import sys
import tempfile
from urllib.parse import urlparse

import requests

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("image", nargs="?", help="URL, or path to image file")
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


# if the image is a URL, validate and download it to a temporary file
def download_image(image):
    """Download the image to a temporary file."""
    if urlparse(image).scheme in ["http", "https"]:
        response = requests.get(image, stream=True, timeout=5)
        response.raise_for_status()

        # create a temporary file and write the image to the temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # filter out keep-alive new chunks
                    temp_file.write(chunk)
            temp_file_path = temp_file.name  # get the path of the temporary file

        # extract image format from the URL
        image_format = get_image_format(image)

        return temp_file_path, image_format

    # if not an image return the original path and the format
    return image, get_image_format(image)


def get_image_format(path):
    """Get the image format from the file extension."""
    path = urlparse(path).path  # extract the path from the URL
    filename = path.split("/")[-1]  # get the filename from the URL path
    return filename.split(".")[-1].lower()


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
        try:
            image_path, image_format = download_image(args.image)
            with open(image_path, "rb") as image:
                image_data = image.read()
                mime_type = image_formats[image_format]
        except FileNotFoundError:
            print(f"Error: The file '{args.image}' was not found.")
            return
        except PermissionError:
            print(
                f"Error: Permission denied when trying to open the file '{args.image}'."
            )
            return
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
