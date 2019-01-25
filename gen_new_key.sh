#!/usr/bin/env bash

DATENOW="$(date +%Y-%m-%d)"

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
