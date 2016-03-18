#!/bin/bash

# This script assumes you have a working version of youtube-dl and ffmpeg. If not, install youtube-dl at
# https://rg3.github.io/youtube-dl/download.html
# If on Mac OS X, you can install via homebrew with `brew install youtube-dl'

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
 
m4a_convert(){
	for fname in *.m4a ; do # Youtube-dl usually downloads audio files as m4a's
		ffmpeg -i "$fname" -c:a libmp3lame -b:a 320k "${fname%.*}.mp3"
	done
}

webm_convert(){
	for fname in *.webm ; do
		ffmpeg -i "$fname" -c:a libmp3lame -b:a 320k "${fname%.*}.mp3"
	done
}

opus_convert(){
	for fname in *.opus ; do
		ffmpeg -i "$fname" -c:a libmp3lame -b:a 320k "${fname%.*}.mp3"
	done
}

ogg_convert(){
	for fname in *.ogg ; do
		ffmpeg -i "$fname" -c:a libmp3lame -b:a 320k "${fname%.*}.mp3"
	done
}

ffmpeg_check && youtube "$@"

if [[ -e "${fname%.*}.mp3" ]] ; then
	echo "'${fname%.*}.mp3' already exists!"
	echo "Do you want to overwite it? [y/n]"

	read -r response
	if [[ $response == "y" ]] ; then
		m4a_convert || webm_convert || opus_convert || ogg_convert
	else
		exit 0
	fi
else
	m4a_convert || webm_convert || opus_convert || ogg_convert
fi

if [[ -e "$fname" ]] ; then
	echo "Do you want to delete the originals? [y/n]"
	
	read -r response
	if [[ $response == "y" ]] ; then
		rm ./*.m4a || rm ./*.webm || rm ./*.opus || rm ./*.ogg
		echo "Deleting..."
		sleep 1
		exit 0
	else
		exit 0
	fi
fi

