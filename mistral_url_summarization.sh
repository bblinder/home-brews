#!/usr/bin/env bash

set -Eeuo pipefail

# Functions
cleanup() {
    trap - SIGINT SIGTERM ERR EXIT
    # Add cleanup tasks here if any
}

check_dependencies() {
    local dependencies=("curl" "links" "sed")
    for cmd in "${dependencies[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            echo "Error: Required command '$cmd' not found."
            exit 1
        fi
    done
}

# Trap signals for cleanup
trap cleanup SIGINT SIGTERM ERR EXIT

# Check for dependencies
check_dependencies

# Get the script directory
script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd -P)

# Check arguments
if [[ "${1-}" =~ ^-*h(elp)?$ ]]; then
    echo "Usage: $0 URL LLAMAFILE"
    exit 0
fi

if [ "$#" -ne 2 ]; then
    echo "Error: Incorrect number of arguments."
    echo "Usage: $0 URL LLAMAFILE"
    exit 1
fi

URL=$1
LLAMAFILE=$2

# Check if the URL is valid
if ! curl --output /dev/null --silent --head --fail "$URL"; then
    echo "Error: URL does not exist: $URL"
    exit 1
fi

# Summarize the text from the URL
(
  echo '[INST]Summarize the following text:'
  links -codepage utf-8 \
        -force-html \
        -width 500 \
        -dump $URL |
    sed 's/   */ /'
  echo '[/INST]'
) | $LLAMAFILE \
      -c 6700 \
      -f /dev/stdin \
      --temp 0 \
      -n 500 \
      --silent-prompt 2>/dev/null
