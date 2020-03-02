#!/usr/bin/env bash

# First off, this is messy as hell and probably offensive to an actual developer.
# Second, I'm sincerely sorry to any developer
# who has the misfortune of reading this...

# Tested Debian 8/9 and Mac OS X 10.{11-14}

set -euo pipefail
IFS=$'\n\t'

PIP2_LIST="/tmp/pip2_list.txt" # Where we're temporarily keeping our stuff.
PIP3_LIST="/tmp/pip3_list.txt"

PIP2_MAKE_LIST(){
	python2 -m pip list --outdated --no-python-version-warning | awk '{ print $1 }' | sed -e '/^\s*$/d' | tail -n +3 > "$PIP2_LIST"
}

PIP3_MAKE_LIST(){
	python3 -m pip list --outdated | awk '{ print $1 }' | sed -e '/^\s*$/d' | tail -n +3 > "$PIP3_LIST"
}

REMOVE_LIST(){
	if pip2_upgrade ; then
		if [[ -z "$PIP2_LIST" ]] ; then
			rm "$PIP2_LIST"
		fi
	else
		echo "There was an error. Please try again."
		rm "$PIP2_LIST"
	fi

	if pip3_upgrade ; then
		if [[ -z "$PIP3_LIST" ]] ; then
			rm "$PIP3_LIST"
	else
		echo "::: There was an error. Please try again."
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
		echo -e "::: Running random brew doctor...\\n"
		brew doctor
	fi

	brew update ; brew upgrade ; brew cask upgrade ; brew cleanup

	read -rp "Clean up Homebrew caches too? (y/N) --> " cache_response
	case "$cache_response" in
		[yY])
			brew cleanup -s
			;;
	esac
}

pip2_upgrade(){
    while read -r package; do
	    python2 -m pip install "$package" --upgrade --user --no-python-version-warning
    done < "$PIP2_LIST"
    	# return 1
}

pip3_upgrade(){
	while read -r package; do
		python3 -m pip install "$package" --upgrade --user
	done < "$PIP3_LIST"
	# return 1
}

ruby_upgrade(){
	if [[ "$(uname -s)" == "Darwin" ]] ; then
		## Weird Mac OS thing where it does not let you write to /usr/bin
		sudo gem update -n /usr/local/bin ; sudo gem update --system
	else
		sudo gem update ; sudo gem update --system
	fi
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
	if [[ "$(command -v brew)" ]] ; then
		read -rp "Update Homebrew? [y/n] -->  " BREW_CHOICE
		case "$BREW_CHOICE" in
			[yY])
				homebrew_upgrade
				;;
			*)
				;;
		esac
	fi
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

	if [[ -n "$(command -v pihole)" ]] ; then
		read -rp "Update Pihole? [y/n]? -->  " PIHOLE_CHOICE
		case "$PIHOLE_CHOICE" in
			[yY])
				pihole_update
				;;
			*)
				;;
		esac
	fi

	if [[ -n "$(command -v flatpak)" ]] ; then
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

		## checking if pip lists exists
		if [[ -s "$PIP2_LIST" ]] || [[ -s "$PIP3_LIST" ]] ; then
			pip2_upgrade & pip3_upgrade
			REMOVE_LIST
		else
			echo -e "::: No new pip packages..."
		fi
		
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
	*)
		;;
esac

if [[ "$(uname -s)" == "Darwin" ]] ; then
	read -rp "Check for Apple Updates? [y/n] -->  " APPLE_CHOICE

	case "$APPLE_CHOICE" in
		[yY])
			softwareupdate --list
			;;
		*)
			;;
	esac
fi
