#!/usr/bin/env bash

#IFS=$'\n\t'
IFS=","
shopt -s nullglob

if [[ $# -eq 0 ]] ; then
	echo "No file supplied!"
	exit 1
fi

set -x #debug mode

while read -r url ; do
	header=$(curl -sI -m 5 "$url")
	status_code=$(echo "$header" | grep -i "HTTP" | awk '{print $2}')
	content_length_exists=$(echo "$header" | grep -i "Content-Length")
	file_size=$(echo "$header" | grep -i "Content-Length" | awk '{print $2}' | awk '{foo = $1 / 1024 / 1024 ; print foo "MB" }')
	
	if [[ "$status_code" -eq 200 ]] || [[ "$status_code" -eq 206 ]] || [[ "$status_code" -eq 301 ]] || [[ "$status_code" -eq 302 ]] || [[ "$status_code" -eq 304 ]] ; then
		if [[ "$content_length_exists" ]] ; then
			echo -e "$url,$status_code,$file_size"
		fi
	else
		echo -e "$url,$status_code" || true
	fi
done < "$1" > $1.new.csv

