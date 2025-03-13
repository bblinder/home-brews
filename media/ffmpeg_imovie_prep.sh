#!/usr/bin/env bash

# using this to prep MPEG 1/2 multiplexed files for editing and viewability in QT and iMovie.

set -eou pipefail
IFS=$'\n\t'
#shopt -s nullglob

ffmpeg_check(){
	type ffmpeg >/dev/null 2>&1 || { echo >$2 "::: ffmpeg not installed. Please install it at: https://ffmpeg.org/download.html" ; exit 1; }
}

ffmpeg_single(){
	while read -r x ; do
		ffmpeg -i "${x}" -strict experimental -pix_fmt yuv420p \
		-c:v libx264 -c:a aac \
		-ab 160000 -preset slow \
		-crf 15 "${x/%.*/_imovie.mp4}" < /dev/null
	done
}
DEAL_WITH_IT(){
	echo -n "( •_•)"
	sleep .75
	echo -n -e "\r( •_•)>⌐■-■"
	sleep .75
	echo -n -e "\r               "
	echo  -e "\r(⌐■_■)"
	sleep .5
}

ffmpeg_check
echo "Drag and Drop your file HERE -->  "
ffmpeg_single && DEAL_WITH_IT

# Saving this for when I'm ready to do batch files.
<<EOL
ffmpeg_batch(){
	for x in *.mp4; do
		ffmpeg -i "${x}" -strict experimental \
		-pix_fmt yuv420p -vcodec libx264 -acodec aac \
		-ab 160000 -preset slow \
		-crf 18 "${x/.mp4/_imovie.mp4}"
	done
	exit 0
}
read -rp "Enter (1) to transcode a single file, or (2) to transcode a folder -->   " TRANSCODE_CHOICE
case "$TRANSCODE_CHOICE" in
	1)
			echo "Drag and drop file HERE -->  "
			ffmpeg_single
			;;

	2)
			ffmpeg_batch
			;;

	*)
			echo "Please enter (1) or (2)"
			;;
	esac
EOL

