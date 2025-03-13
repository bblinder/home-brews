#!/usr/bin/env python3

"""
A pythonic wrapper around imagemagick and ghostscript to make
a PDF 'look scanned', and crappily at that.

Example:
    python3 scanPDF.py -o ~/Downloads/SCANNED.pdf ~/Documents/original_PDF.pdf

By default, the output file will be saved to the same directory
as the input file (unless specified otherwise with the -o flag)
"""

import os
import subprocess
import sys
from pathlib import Path
from shutil import which
from typing import Optional

from halo import Halo

cmds = {"magick": "ImageMagick", "gs": "GhostScript"}

for cmd, package in cmds.items():
    if which(cmd) is None:
        print(f"Please install {package} first")
        sys.exit(1)

script_dir = Path(__file__).resolve().parent


def get_downloads_folder() -> Path:
    """
    Returns the path to the user's Downloads folder
    """
    if os.name == "nt":
        return Path(os.environ["USERPROFILE"]) / "Downloads"
    return Path.home() / "Downloads"


def imagemagick_convert(pdf: Path) -> Path:
    """
    Uses ImageMagick to convert the PDF to a crappy looking scanned PDF
    """
    temp_file = script_dir / "TEMP.pdf"
    imagemagick_commands = [
        "magick",
        "-density",
        "150",
        str(pdf),
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
        str(temp_file),
    ]

    subprocess.run(imagemagick_commands, cwd=script_dir, check=True)
    return temp_file


def ghostscript_convert(imagemagick_output_pdf: Path, output: Path):
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
        "-sOutputFile=" + str(output),
        "-sColorConversionStrategy=LeaveColorUnchanged",
        "-dAutoFilterColorImages=true",
        "-dAutoFilterGrayImages=true",
        "-dDownsampleMonoImages=true",
        "-dDownsampleGrayImages=true",
        "-dDownsampleColorImages=true",
        str(imagemagick_output_pdf),
    ]

    try:
        subprocess.run(ghostscript_commands, cwd=script_dir, check=True)
    finally:
        imagemagick_output_pdf.unlink()


@Halo(text="Scanning PDF... please wait... ", spinner="dots")
def main(pdf: Path, output: Optional[Path] = None):
    """
    Main function.
    """
    output_file = pdf.with_stem(pdf.stem + "_SCANNED")

    if output is None:
        output = get_downloads_folder() / output_file

    if output.suffix != ".pdf":
        output = output.with_suffix(".pdf")

    im_pdf = imagemagick_convert(pdf)
    ghostscript_convert(im_pdf, output)


if __name__ == "__main__":
    import argparse

    argparser = argparse.ArgumentParser(
        description="Make your PDF look manually scanned"
    )
    argparser.add_argument("pdf", type=Path, help="PDF file to scan")
    argparser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output location + file name (optional)",
    )
    args = argparser.parse_args()
    main(args.pdf, args.output)
