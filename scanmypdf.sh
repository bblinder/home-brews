#!/usr/bin/env bash

set -Eeuo pipefail
trap cleanup SIGINT SIGTERM ERR EXIT

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd -P)
DOCUMENT="$1"

die() {
  local msg=$1
  local code=${2-1} # default exit status 1
  msg "$msg"
  exit "$code"
}

# if imagemagick is not installed

if ! command -v convert >/dev/null 2>&1; then
    die "imagemagick is not installed"
    exit 1
fi

cleanup() {
  trap - SIGINT SIGTERM ERR EXIT
  # script cleanup here
}


IM(){
    convert -density 150 "$DOCUMENT" -colorspace gray \
    -linear-stretch 3.5%x10% -blur 0x0.5 \
    -attenuate 0.25 +noise Gaussian -rotate 0.5 \
    SCANNED.pdf
    return 0
}

ghostscript(){
    gs -dSAFER -dBATCH -dNOPAUSE \
    -dNOCACHE -sDEVICE=pdfwrite -sOutputFile=compressed.pdf \
    -sColorConversionStrategy=LeaveColorUnchanged -dAutoFilterColorImages=true \
    -dAutoFilterGrayImages=true -dDownsampleMonoImages=true -dDownsampleGrayImages=true -dDownsampleColorImages=true \
    SCANNED.pdf
    return 0
}

IM
if IM ; then
    ghostscript
fi

if ghostscript ; then
    read -rp "Do you want to delete the original file? [y/N] " response
    case "$response" in
        [yY])
            rm -f SCANNED.pdf
            ;;
        *)
            ;;
    esac
fi