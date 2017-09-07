#!/bin/bash

## A quick and dirty script to losslessly compress my jpegs using Dropbox's lepton tool.
## https://github.com/dropbox/lepton

set -euo pipefail
IFS=$'\n\t'
#shopt -s nullglob

# Checks if Lepton's installed. 
type lepton >/dev/null 2>&1 || { echo >&2 "::: Lepton not installed.  Aborting."; exit 1; }

PNG_TO_JPEG(){
	for i in *.png ; do 
		convert "$i" "${i%.*}.jpg"
	done
}

JPEG_TO_LEP(){
	for j in *.jpg ; do
		lepton "$j" "${j%.*}.lep"
	done
}

LEP_TO_JPEG(){
	for j in *.lep ; do
		lepton "$j" "${j%.*}.jpg"
	done
}

count="ls *.png 2>/dev/null | wc -l"
if [[ "$count" != 0 ]] ; then
	# Checks if convert/imagemagick is installed
	type convert >/dev/null 2>&1 || { echo >&2 "::: Convert/ImageMagick not installed." ; exit 1; }
	read -rp "::: PNG's found. Convert them to JPEGs first? (Y/N)  " PNG_CHOICE
	case "$PNG_CHOICE" in
		[yY])
			PNG_TO_JPEG
			rm *.png
			;;
		*)
			;;
	esac
fi

THE_NEEDFUL(){
	case "$COMPRESS_CHOICE" in
		1)
			JPEG_TO_LEP
			read -rp "Delete .jpg files? (y/n)  " JPEG_DELETE
			case "$JPEG_DELETE" in
				yY)
					rm *.jpg
					;;
				*)
					;;
			esac
			;;
		2)
			LEP_TO_JPEG
			read -rp "Delete .lep files? (y/n)  " LEP_DELETE
			case "$LEP_DELETE" in
				yY)
					rm *.lep
					;;
				*)
					;;
			esac
			;;
		*)
			
			echo "Please enter (1) or (2)"
			exit 1
			;;
	esac
	return 0
}

<<'EOD'
if [[ ! -e  *.jpg *.JPEG *.jpg ]] ; then
	echo "No JPEGs found. Exiting..."
	exit 1
else
EOD

read -rp "Compress (1) or Uncompress (2)? --> " COMPRESS_CHOICE

THE_NEEDFUL
if [[ THE_NEEDFUL ]] ; then
	echo "Success."
else
	echo "Failed. Try again, maybe?"
fi
