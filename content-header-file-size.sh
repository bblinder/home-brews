#!/usr/bin/env bash

## Bash strict mode (keeping it disabled for now)
#set -euo pipefail
IFS=$'\n\t'
shopt -s nullglob

#set -x # debug mode

if [[ $# -eq 0 ]] ; then
	echo "No file supplied!"
	exit 1
fi

#while read -r url ; do
#	status_code=$(curl -sI -m 5 --write-out %{http_code} --silent --output /dev/null "$url")
#	content_length_exists=$(curl -sI -m 5 "$url" | grep -i "Content-Length")
#	file_size=$(curl -sI -m 5 "$url" | grep -i "Content-Length" | awk '{print $2}' | awk '{foo = $1 / 1024 / 1024 ; print foo "MB" }')
#	if [[ "$status_code" -eq 200 ]] ; then
#		if [[ "$content_length_exists" ]] ; then
#			echo -e "$url,$status_code,$file_size"
#		fi || true
#	else
#		echo -e "$url,$status_code" || true
#	fi
#done < "$1" > tmp-file_sizes.csv

while read -r url ; do
	header=$(curl -sI -m 5 "$url")
	status_code=$(echo "$header" | grep -i "HTTP" | awk '{print $2}')
	content_length_exists=$(echo "$header" | grep -i "Content-Length")
	file_size=$(echo "$header" | grep -i "Content-Length" | awk '{print $2}' | awk '{foo = $1 / 1024 / 1024 ; print foo "MB" }')

	if [[ "$status_code" -eq 200 ]] ; then
		if [[ "$content_length_exists" ]] ; then
			echo -e "$url,$status_code,$file_size"
		fi || true
	else
		echo -e "$url,$status_code" || true
	fi
done < "$1" > tmp-file_sizes.csv
