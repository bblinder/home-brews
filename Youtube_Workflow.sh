#!/bin/sh

convert='/Users/brandon/Github/home-brews/MP3_convert.sh'
youtube-dl -x $1 ; . $convert 

if [[ ! -e $1 ]]
then
	echo "Provide a link, please."
	exit
fi
