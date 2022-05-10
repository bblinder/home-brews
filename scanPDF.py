#!/usr/bin/env python3

from shutil import which
import os
import subprocess
from halo import Halo

cmds = {
    "convert": "ImageMagick", 
    "gs": "GhostScript"
}

for cmd in cmds:
    if not which(cmd):
        # print dict values
        print("{} is not installed".format(cmds[cmd]))

script_dir = os.path.dirname(os.path.realpath(__file__))


def get_downloads_folder():
    if os.name == 'nt':
        return os.path.join(os.environ['USERPROFILE'], 'Downloads')
    else:
        return os.path.join(os.path.expanduser('~'), 'Downloads')


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


@Halo(text="Scanning PDF... please wait... ", spinner="dots")
def main():
    IM_PDF = imageMagick_convert(args.pdf)
    ghostScript_convert(IM_PDF)


if __name__ == "__main__":
    import argparse
    argparser = argparse.ArgumentParser(description="Make your PDF look manually scanned")
    argparser.add_argument("pdf", help="PDF file to scan")
    argparser.add_argument("-o", "--output", help="Output location (optional)", default=os.path.join(get_downloads_folder(), "SCANNED.pdf"))
    args = argparser.parse_args()

    main()
