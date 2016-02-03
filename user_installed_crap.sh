#!/bin/bash

# First off, this is messy as hell and probably offensive to an actual developer.
# Second, I'm sincerely sorry to any developer
# who has the misfortune of reading this...

# Tested only on Debian 8 "Jessie" and Mac OS X 10.10

LIST="/tmp/pip_list.txt" # Where we're temporarily keeping our stuff.

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
	MAKE_LIST | egrep -i "pip|livestreamer|youtube-dl|\
	thefuck|tldr|zenmap|paramiko|clf|Fabric|\
	speedtest-cli|setuptools|ohmu|httpie|stormssh" > "$LIST"
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
			echo "Please enter (y) or (n)"
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
				echo "Please enter (1) or (2)"
				exit 1
				;;
		esac
		;;
	[nN])
		;;
	*)
		echo "Please enter (y) or (n)"
		;;
esac

read -rp "Move on to ruby update? [y/n] -->  "  RUBY_CHOICE
if [[ $RUBY_CHOICE == "y" ]] ; then
	ruby_upgrade
else
	echo "Aborting..."
	exit 0
fi
