#!/usr/bin/env bash

# convert a gif to an mp4

# usage: gif2mp4.sh input.gif output.mp4

# requires: ffmpeg

set -euo pipefail

# suppress ffmpeg warnings
export FFREPORT="file=/dev/null:level=24"

# suppress non-usage errors
#exec 2>/dev/null


input_file="$1"
output_file="$2"

usage () {
    echo "usage: gif2mp4.sh input.gif output.mp4"
    exit 1
}

convert () {
    ffmpeg -i "$input_file" -movflags +faststart -pix_fmt yuv420p -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" "$output_file"
}

# if no arguments are given, print usage
if [ $# = 0 ]; then
    usage
fi

# if the first argument is -h, print usage
if [ "$1" = "-h" ]; then
    usage
fi

# if the first argument is --help, print usage
if [ "$1" = "--help" ]; then
    usage
fi

convert
