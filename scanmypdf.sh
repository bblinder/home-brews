#!/usr/bin/env bash

set -Eeuo pipefail
#trap cleanup SIGINT SIGTERM ERR EXIT

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd -P)
DOCUMENT="$1"

if [[ -z "$DOCUMENT" ]] ; then
    echo -e "Usage: ./scanmypdf.sh <PDF_FILE>"
    exit 1
fi

die() {
  local msg=$1
  local code=${2-1} # default exit status 1
  msg "$msg"
  exit "$code"
}

# checking if imagemagick and ghostscript are installed
COMMANDS="convert gs"

for cmd in $COMMANDS; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo -e "'$cmd' is not installed. Please install it."
    exit 1
  fi
done

# cleanup() {
#   trap - SIGINT SIGTERM ERR EXIT
#   # script cleanup here
# }


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
    echo "PDF compressed!"
    rm SCANNED.pdf
fi
