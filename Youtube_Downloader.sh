#!/bin/bash

ffmpeg_check(){
	if [[ ! ( -f /usr/bin/ffmpeg || -f /usr/local/bin/ffmpeg ) ]] ; then
		echo "FFmpeg not installed!"
 		echo "Please install it at: https://ffmpeg.org/download.html"
 		exit 1
 	fi
}
 
youtube(){
	youtube-dl -x "$1"
}	
 
mp3_convert(){
	for fname in *.m4a ; do
		ffmpeg -i "$fname" -c:a libmp3lame -b:a 320k "${fname%.*}.mp3"
	done
}
 
ffmpeg_check && youtube "$@"

if [[ -e "${fname%.*}.mp3" ]] ; then
	echo "'${fname%.*}.mp3' already exists!"
	echo "Do you want to overwite it? [y/n]"

	read -r response
	if [[ $response == "y" ]] ; then
		mp3_convert
	else
		exit 0
	fi
else
	mp3_convert
fi

if [[ -e "$fname" ]] ; then
	echo "Do you want to delete the originals? [y/n]"
	
	read -r response
	if [[ $response == "y" ]] ; then
		rm ./*.m4a
		echo "Deleting..."
		sleep 1
		exit 0
	else
		exit 0
	fi
fi

