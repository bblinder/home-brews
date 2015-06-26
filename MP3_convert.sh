#!/bin/bash

mp3_convert(){
	for fname in *.m4a ; do
		ffmpeg -i "$fname" -c:a libmp3lame -b:a 320k "${fname%.*}.mp3"
	done
}

if [[ -e "${fname%.*}.mp3" ]] ; then
	echo "'${fname%.*}.mp3' already exists!"
	echo "Do you want to overwite it? [y/n]"
	
	read response
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
	read response
	
	if [[ $response == "y" ]] ; then
		rm ./*.m4a
		echo "Deleting..."
		sleep 1
		exit 0
	else
		exit 0
	fi
fi

##written by Brandon Blinderman 2015
