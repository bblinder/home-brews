#!/usr/bin/env bash

# First off, this is messy as hell and probably offensive to an actual developer.
# Second, I'm sincerely sorry to any developer
# who has the misfortune of reading this...

# Tested Debian 8/9, Mac OS X 10.{11-15}, and WSL (Win 10)

set -euo pipefail
IFS=$'\n\t'

homebrew_upgrade(){
	## Randomly doing some housekeeping ##
	if [[ $((1 + RANDOM %5)) -eq 4 ]] ; then
		echo -e "::: Running random brew doctor...\\n"
		brew doctor
	fi

	brew update ; brew upgrade

	# Only have homebrew/cask installed on my Mac; trying to keep it that way...
	if [[ "$(uname -s)" == "Darwin" ]]; then
		 brew upgrade --cask ; brew cleanup
	fi

	read -rp "Clean up Homebrew caches too? (y/N) --> " cache_response
	case "$cache_response" in
		[yY])
			brew cleanup -s --prune=all
			;;
	esac
}

ruby_upgrade(){
	if [[ "$(uname -s)" == "Darwin" ]] ; then
		## Weird Mac OS thing where it does not let you write to /usr/bin
		sudo gem update -n /usr/local/bin ; sudo gem update -n /usr/local/bin --system
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

# Checking for and updating homebrew (Mac OS or Linuxbrew)
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
	if [[ "$(command -v mas)" ]] ; then
		read -rp "Check for App Store updates? [y/n] -->  " APP_STORE_CHOICE

		case "$APP_STORE_CHOICE" in
			[yY])
				mas outdated
				mas upgrade
				;;
			*)
				;;
		esac
	fi
fi

if [[ "$(uname -s)" == "Darwin" ]] ; then
	read -rp "Check for Apple updates? [y/n] -->  " APPLE_CHOICE

	case "$APPLE_CHOICE" in
		[yY])
			softwareupdate --list
			;;
		*)
			;;
	esac
fi
