#!/bin/bash

set -euo pipefail
IFS=$'\n\t'
#shopt -s nullglob

type lepton >/dev/null 2>&1 || { echo >&2 "::: Lepton not installed.  Aborting."; exit 1; }

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

THE_NEEDFUL(){
	case "$COMPRESS_CHOICE" in
		1)
			JPEG_TO_LEP
			;;
		2)
			LEP_TO_JPEG
			;;
		*)
			echo "Please enter (1) or (2)"
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
