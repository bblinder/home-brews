#!/usr/bin/env bash

# Adapted from a coworker's script to generate internal SSH keys.

DATENOW="$(date +%Y-%m-%d)"

# checking if we gave it a key name, else exiting.
if [[ "$#" -eq 0 ]] ; then
	echo "::: No key name specified. Exiting..."
	exit 1
fi

# Onto the actual work. Generating a 2048 bit RSA key to the directory
# specificed in the "$1" input (ex: personal, work, dev, etc)
for i in "$@"; do
	[[ ! -d "$HOME/.ssh/$i/" ]] && { mkdir -p "$HOME/.ssh/$i"; }

	echo "Generating $i"
	ssh-keygen -t rsa -b 2048 -C "$(whoami)-$i-$DATENOW" -f "$HOME/.ssh/$i/$DATENOW"
	[[ -L "$HOME/.ssh/$i/previous" ]] && { rm "$HOME/.ssh/$i/previous"; }
	[[ -L "$HOME/.ssh/$i/previous.pub" ]] && { rm "$HOME/.ssh/$i/previous.pub"; }
	[[ -L "$HOME/.ssh/$i/current" ]] && { mv "$HOME/.ssh/$i/current" "$HOME/.ssh/$i/previous"; }
	[[ -L "$HOME/.ssh/$i/current.pub" ]] && { mv "$HOME/.ssh/$i/current.pub" "$HOME/.ssh/$i/previous.pub"; }
	ln -s "$HOME/.ssh/$i/$DATENOW" "$HOME/.ssh/$i/current"
	ln -s "$HOME/.ssh/$i/$DATENOW.pub" "$HOME/.ssh/$i/current.pub"
done
