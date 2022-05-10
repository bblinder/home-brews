#!/usr/bin/env python3

from shutil import which
import os, sys
import argparse
import subprocess

cmds = ["convert", "gs"]

# checking if imagemagick and ghostscript are installed
for cmd in cmds:
    if not which(cmd):
        print(f"{cmd} is not installed")
        sys.exit(1)

script_dir = os.path.dirname(os.path.realpath(__file__))

argparser = argparse.ArgumentParser(description="Scan a PDF file and convert it to a series of images")
argparser.add_argument("pdf", help="PDF file to scan")
argparser.add_argument("-o", "--output", help="Output directory", default=os.path.join(script_dir, "SCANNED.pdf"))
args = argparser.parse_args()


def imageMagick_convert(pdf):
    imagemagick_commands = [
        "convert", "-density", "150", args.pdf, "-colorspace", "gray", 
        "-linear-stretch", "3.5%x10%", "-blur", "0x0.5",
        "-attenuate", "0.25", "+noise", "Gaussian", "-rotate", "0.5", "TEMP.pdf"
    ]

    temp_file = os.path.join(script_dir, "TEMP.pdf")

    subprocess.run(imagemagick_commands, cwd=script_dir, check=True)
    # return the pdf
    return temp_file


def ghostScript_convert(imageMagick_output_pdf):
    ghostscript_commands = [
        "gs", "-dSAFER", "-dBATCH", "-dNOPAUSE", "-dNOCACHE",
        "-sDEVICE=pdfwrite", "-sOutputFile=" + args.output, "-sColorConversionStrategy=LeaveColorUnchanged",
        "-dAutoFilterColorImages=true", "-dAutoFilterGrayImages=true",
        "-dDownsampleMonoImages=true", "-dDownsampleGrayImages=true", "-dDownsampleColorImages=true",
        imageMagick_output_pdf
    ]

    if subprocess.run(ghostscript_commands, cwd=script_dir, check=True):
        os.remove(imageMagick_output_pdf)


if __name__ == "__main__":
    IM_PDF = imageMagick_convert(args.pdf)
    ghostScript_convert(IM_PDF)

