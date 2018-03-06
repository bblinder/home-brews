#!/usr/bin/env bash

# First off, this is messy as hell and probably offensive to an actual developer.
# Second, I'm sincerely sorry to any developer
# who has the misfortune of reading this...

# Tested only on Debian 8 "Jessie" and Mac OS X 10.10 and 10.11

set -euo pipefail
IFS=$'\n\t'

PIP2_LIST="/tmp/pip2_list.txt" # Where we're temporarily keeping our stuff.
PIP3_LIST="/tmp/pip3_list.txt"

PIP2_MAKE_LIST(){
	pip2 list | awk '{ print $1 }' | sed -e 's/-//g' -e 's/youtubedl/youtube-dl/g' -e '/^\s*$/d' | tail -n +2 > "$PIP2_LIST"
}

PIP3_MAKE_LIST(){
	pip3 list | awk '{ print $1 }' | sed -e 's/-//g' -e 's/youtubedl/youtube-dl/g' -e '/^\s*$/d' | tail -n +2 > "$PIP3_LIST"
}
REMOVE_LIST(){
	if pip2_upgrade ; then
		if [[ -e "$PIP2_LIST" ]] ; then
			rm "$PIP2_LIST"
		fi
	else
		echo "There was an error. Please try again."
		rm "$PIP2_LIST"
	fi

	if pip3_upgrade ; then
		if [[ -e "$PIP3_LIST" ]] ; then
			rm "$PIP3_LIST"
	else
		echo "::: There was an error. Please try again."
			rm "$PIP3_LIST"
		fi
	fi
}

general_packages(){
	PIP2_MAKE_LIST
	PIP3_MAKE_LIST
}

homebrew_upgrade(){
	## Randomly doing some housekeeping ##
	if [[ $((1 + RANDOM %5)) -eq 4 ]] ; then
		echo "::: Running random brew doctor...\n"
		brew doctor
	fi
	
	brew update ; brew upgrade
	brew cleanup ; brew cask cleanup ; brew prune
}

pip2_upgrade(){
    while read -r package; do
        sudo -H pip2 install "$package" --upgrade
    done < "$PIP2_LIST" ; return 1
}

pip3_upgrade(){
	while read -r package; do
		sudo -H pip3 install "$package" --upgrade
	done < "$PIP3_LIST" ; return 1
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

	if [[ "$(command -v pihole)" ]] ; then
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
		general_packages
		pip2_upgrade & pip3_upgrade
		REMOVE_LIST
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
