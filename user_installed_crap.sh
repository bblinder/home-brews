#!/bin/bash

# First off, this is messy as hell and probably offensive to an actual developer.
# Second, I'm sincerely sorry to any developer
# who has the misfortune of reading this...

# Tested only on Debian 8 "Jessie" and Mac OS X 10.10

set -euo pipefail
IFS=$'\n\t'


LIST="/tmp/pip_list.txt" # Where we're temporarily keeping our stuff.

if [[ -z "$LIST" ]] ; then # cleaning up beforehand
	rm "$LIST"
fi

MAKE_LIST(){
	pip list | awk '{ print $1 }'
}

REMOVE_LIST(){
	if pip_upgrade ; then
		if [[ -e "$LIST" ]] ; then
			rm "$LIST"
		fi
	else
		echo "There was an error. Please try again." && \
			if [[ -e /usr/local/bin/noti ]] ; then
				noti -t PIP_Update -m "There was an error upgrading python packages..."
			fi
		rm "$LIST"
	fi
}

general_packages(){
	MAKE_LIST > "$LIST"
}

choice_packages(){
	MAKE_LIST | grep -Ei "pip|livestreamer|youtube-dl|\
	thefuck|tldr|zenmap|paramiko|clf|Fabric|\
	speedtest-cli|setuptools|haxor-news|ohmu|httpie|\
	waybackpack|http-prompt|rtv|glances|musicrepair" > "$LIST"
}

homebrew_upgrade(){
	brew update ; brew upgrade
	brew cleanup ; brew cask cleanup ; brew prune
}

pip_upgrade(){
    while read -r package; do
        sudo -H pip install "$package" --upgrade || return 1
    done < "$LIST" ; return 0
}

ruby_upgrade(){
	sudo gem update ; sudo gem update --system
}

bulk_git_update(){
	Github='/Users/bblinder/Github'
	for dir in "$Github"/* ; do (cd "$dir" && git remote update && git pull && git gc --auto); done
}

# Ruling out non Mac OS X systems...
if [[ "$(uname -s)" == "Darwin" ]] ; then
	read -rp "Update Homebrew? [y/n] -->  " BREW_CHOICE

	case "$BREW_CHOICE" in
		[yY])
			homebrew_upgrade
			;;
		[nN])
			;;
		*)
			;;
	esac
fi

read -rp "Update Python packages? [y/n]? -->  " PYTHON_CHOICE

case "$PYTHON_CHOICE" in
	[yY])
		read -rp "General update (1) or just the favorites (2) ? -->  " PYTHON_TYPE_CHOICE
		case "$PYTHON_TYPE_CHOICE" in
			1)
				general_packages
				pip_upgrade
				REMOVE_LIST
				;;
			2)
				choice_packages
				pip_upgrade
				REMOVE_LIST
				;;

			*)
				;;
		esac
		;;
	[nN])
		;;
	*)
		;;
esac

read -rp "Move on to ruby update? [y/n] -->  "  RUBY_CHOICE
if [[ $RUBY_CHOICE == "y" ]] ; then
	ruby_upgrade
fi


read -rp "Bulk update Git repos? [y/n]? -->  " GIT_CHOICE
case "$GIT_CHOICE" in
	[yY])
		bulk_git_update
		;;
	[nN])
		;;
	*)
		;;
esac

if [[ "$(uname -s)" == "Darwin" ]] ; then
	read -rp "Check for Apple Updates? [y/n] -->  " APPLE_CHOICE

	case "$APPLE_CHOICE" in
		[yY])
			sudo softwareupdate -lv
			;;
		[nN])
			;;
		*)
			;;
	esac
fi
