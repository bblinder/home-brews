#!/usr/bin/env bash

# First off, this is messy as hell and probably offensive to an actual developer.
# Second, I'm sincerely sorry to any developer
# who has the misfortune of reading this...

# Tested Debian 8/9, Mac OS X 10.{11-15}, and WSL (Win 10)

set -Eeuo pipefail
IFS=$'\n\t'
trap cleanup SIGINT SIGTERM ERR EXIT

cleanup() {
  trap - SIGINT SIGTERM ERR EXIT
  # script cleanup here
  #rm -f "$LIST"
}

setup_colors() {
  if [[ -t 2 ]] && [[ -z "${NO_COLOR-}" ]] && [[ "${TERM-}" != "dumb" ]]; then
    NOFORMAT='\033[0m' RED='\033[0;31m' GREEN='\033[0;32m' ORANGE='\033[0;33m' BLUE='\033[0;34m' PURPLE='\033[0;35m' CYAN='\033[0;36m' YELLOW='\033[1;33m'
  else
    NOFORMAT='' RED='' GREEN='' ORANGE='' BLUE='' PURPLE='' CYAN='' YELLOW=''
  fi
}

msg() {
  echo >&2 -e "${1-}"
}

die() {
  local msg=$1
  local code=${2-1} # default exit status 1
  msg "$msg"
  exit "$code"
}

check_for_pip_script(){
	if [[ ! -e pip3_upgrade.sh ]] ; then
	echo -e "::: Can't find python3 update script. Continuing..."
	fi
}

setup_colors

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

pip_upgrade(){
	./pip3_upgrade.sh
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

if [[ check_for_pip_script ]] ; then
	read -rp "Move on to Python update? [y/n] --> "  PIP_CHOICE
	case "$PIP_CHOICE" in 
		[yY])
			pip_upgrade
			;;
		*)
			;;
	esac
fi

read -rp "Move on to ruby update? [y/n] -->  "  RUBY_CHOICE
case "$RUBY_CHOICE" in
	[yY])
		ruby_upgrade
		;;
	*)
		;;
esac

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
