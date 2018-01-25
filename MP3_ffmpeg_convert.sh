#!/usr/bin/env bash

set -euo pipefail
shopt -s nullglob
shopt -s nocaseglob

mp3_convert() {
	for fname in *.{m4a,webm,opus,ogg,mp3}; do
		ffmpeg -i "$fname" -c:a libmp3lame -b:a 320k "${fname%.*}.mp3"
	done
}

if [[ ! "$(command -v ffmpeg)" ]]; then
	echo -e "::: ffmpeg not found. Please make it's installed.\\n"
	exit 1
fi

if [[ -e "${fname%.*}.mp3" ]]; then
	echo -e "::: '${fname%.*}.mp3' already exists."
	read -rp "Do you want to overwrite it? [y/n]? -->  " overwrite_response
	case "$overwrite_response" in
	[yY])
		mp3_convert
		;;
	*)
		exit
		;;
	esac
else
	mp3_convert
fi

shopt -u nullglob
shopt -u nocaseglob
