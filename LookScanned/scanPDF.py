#!/usr/bin/env python3

"""
Uses imagemagick and ghostscript to make a PDF 'look scanned', and crappily at that.
"""

import os
import subprocess
import sys
from shutil import which

from halo import Halo

cmds = {"convert": "ImageMagick", "gs": "GhostScript"}

# iterate with .items()
for cmd, package in cmds.items():
    if which(cmd) is None:
        print(f"Please install {package} first")
        sys.exit(1)

script_dir = os.path.dirname(os.path.realpath(__file__))


def get_downloads_folder():
    """
    Returns the path to the user's Downloads folder
    """
    if os.name == "nt":
        return os.path.join(os.environ["USERPROFILE"], "Downloads")
    else:
        return os.path.join(os.path.expanduser("~"), "Downloads")


def imagemagick_convert(pdf):
    """
    Uses ImageMagick to convert the PDF to a crappy looking scanned PDF
    """
    imagemagick_commands = [
        "convert",
        "-density",
        "150",
        args.pdf,
        "-colorspace",
        "gray",
        "-linear-stretch",
        "3.5%x10%",
        "-blur",
        "0x0.5",
        "-attenuate",
        "0.25",
        "+noise",
        "Gaussian",
        "-rotate",
        "0.5",
        "TEMP.pdf",
    ]

    temp_file = os.path.join(script_dir, "TEMP.pdf")

    subprocess.run(imagemagick_commands, cwd=script_dir, check=True)
    # return the pdf
    return temp_file


def ghostscript_convert(imagemagick_output_pdf):
    """
    Uses GhostScript to manage size and put on the finishing touches"
    """
    ghostscript_commands = [
        "gs",
        "-dSAFER",
        "-dBATCH",
        "-dNOPAUSE",
        "-dNOCACHE",
        "-sDEVICE=pdfwrite",
        "-sOutputFile=" + args.output,
        "-sColorConversionStrategy=LeaveColorUnchanged",
        "-dAutoFilterColorImages=true",
        "-dAutoFilterGrayImages=true",
        "-dDownsampleMonoImages=true",
        "-dDownsampleGrayImages=true",
        "-dDownsampleColorImages=true",
        imagemagick_output_pdf,
    ]

    if subprocess.run(ghostscript_commands, cwd=script_dir, check=True):
        os.remove(imagemagick_output_pdf)


@Halo(text="Scanning PDF... please wait... ", spinner="dots")
def main():
    im_pdf = imagemagick_convert(args.pdf)
    ghostscript_convert(im_pdf)


if __name__ == "__main__":
    import argparse

    argparser = argparse.ArgumentParser(
        description="Make your PDF look manually scanned"
    )
    argparser.add_argument("pdf", help="PDF file to scan")
    argparser.add_argument(
        "-o",
        "--output",
        help="Output location (optional)",
        default=os.path.join(get_downloads_folder(), "SCANNED.pdf"),
    )
    args = argparser.parse_args()

    main()
