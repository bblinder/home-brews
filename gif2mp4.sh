#!/usr/bin/env bash

# This script converts a GIF file to an MP4 file using ffmpeg.
#
# Usage: ./gif2mp4.sh input.gif output.mp4
#
# Arguments:
#   input.gif: The input GIF file to convert.
#   output.mp4: The output MP4 file. The file extension will be forced to .mp4.
#
# Requirements:
#   - ffmpeg must be installed and available on the system PATH.

set -euo pipefail
set -o errexit
set -o nounset
set +u

input_file="$1"
output_file="${2%.*}.mp4"

# suppress ffmpeg warnings
export FFREPORT="file=/dev/null:level=24"

input_file="$1"
output_file="${2%.*}.mp4"

ffmpeg_check() {
    # Check if ffmpeg is installed and available on the system PATH
    if ! command -v ffmpeg &> /dev/null; then
        echo "Error: ffmpeg is not installed or not available on the system PATH."
        exit 1
    fi
}

usage() {
    if [[ "${1-}" =~ ^-*h(elp)?$ ]]; then
        echo '::: Usage: ./gif2mp4.sh input-file output-file'
    elif [[ $# -eq 0 ]]; then
        echo "::: Usage: ./gif2mp4.sh input-file output-file"
        exit 1
    fi
}

convert() {
    ffmpeg -i "$1" -movflags +faststart -pix_fmt yuv420p -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" "$2"
}

ffmpeg_check
usage "$@"
convert "$input_file" "$output_file"