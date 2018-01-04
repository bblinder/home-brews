#!/bin/bash

# First off, this is messy as hell and probably offensive to an actual developer.
# Second, I'm sincerely sorry to any developer
# who has the misfortune of reading this...

# Tested only on Debian 8 "Jessie" and Mac OS X 10.10 and 10.11

set -euo pipefail
IFS=$'\n\t'

LIST="/tmp/pip_list.txt" # Where we're temporarily keeping our stuff.

MAKE_LIST(){
	pip2 list | awk '{ print $1 }'
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
        sudo -H pip2 install "$package" --upgrade || return 1
    done < "$LIST" ; return 0
}

ruby_upgrade(){
	sudo gem update ; sudo gem update --system
}

bulk_git_update(){
	Github="$HOME/Github"
	if [[ -e /usr/local/bin/git-up ]] ; then
		for dir in "$Github"/* ; do (cd "$dir" && git remote update && git up) ; done
	else
		for dir in "$Github"/* ; do (cd "$dir" && git remote update && git pull --rebase && git gc --auto); done
	fi
}

pihole_update(){
	pihole -up ; pihole -g ; pihole restartdns
}

apt_update(){
	sudo apt-get update ; sudo apt-get upgrade --yes
	sudo apt-get dist-upgrade
	sudo apt-get autoclean ; sudo apt-get clean ; sudo apt-get autoremove
}

flatpak_update(){
	# sudo needed here? 
	flatpak update
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

if [[ "$(uname -s)" == "Linux" ]] ; then
	read -rp "Update APT repo? [y/n]? -->  " APT_CHOICE
	case "$APT_CHOICE" in
		[yY])
			apt_update
			;;
		*)
			;;
	esac

	if [[ "$command -v pihole)" ]] ; then
		read -rp "Update Pihole? [y/n]? -->  " PIHOLE_CHOICE
		case "$PIHOLE_CHOICE" in
			[yY])
				pihole_update
				;;
			*)
				;;
		esac
	fi

	if [[ "$(command -v flatpak)" ]] ; then
		read -rp "Update Flatpak? [y/n]? -->  " FLATPAK_CHOICE
		case "$FLATPAK_CHOICE" in
			[yY])
				flatpak update
				;;
			*)
				;;
		esac
	fi
fi

read -rp "Update Python packages? [y/n]? -->  " PYTHON_CHOICE
case "$PYTHON_CHOICE" in
	[yY])
		if [[ -e "$LIST" ]] ; then # cleaning up beforehand
		rm "$LIST"
		fi
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
