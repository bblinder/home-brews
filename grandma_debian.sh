#!/usr/bin/env bash

set -euo pipefail
IFS=$'\n\t'

if [[ "$(uname -s)" != "Linux" ]] ; then
  echo "::: ERROR: this script will only run on Linux systems"
  echo "::: Exiting..."
  exit 1
fi

# *nix utilities
apt_array=(axel vim python-pip python3-pip python-dev flatpak zsh git p7zip-full mtr \
	bleachbit nmap zenmap netcat pv gdebi lynx iftop filelight ufw glances)

# python3 utils
python_array=(httpie youtube-dl requests streamlink tldr paramiko cheat)

INSTALL_NIX_UTILS(){
	# install nix utilities
	sudo apt-get install -y "${apt_array[@]}" || return 1
}

INSTALL_PYTHON3_UTILS(){
  if [[ INSTALL_NIX_UTILS ]] ; then
    echo "::: APT Packages done. Moving on to Python packages... "
    sleep 1.5
    sudo -H pip3 install "${python_array[@]}" || return 1
  fi
}

MKDIR_GITHUB(){
	Github_Dir='$HOME/Github/'
	if [[ ! -d "$Github_Dir" ]] ; then
		mkdir -p "$Github_Dir"
		git clone https://github.com/bblinder/home-brews.git "$Github_Dir"
	fi
}

UNINSTALL_STUFF(){
	# python crap
	sudo -H pip3 uninstall --yes "${python_array[@]}"

	# apt crap
	sudo apt-get purge "${apt_array[@]}"
	sudo apt-get autoclean ; sudo apt-get autoremove ; sudo apt-get clean
}

## Now onto the actual work

read -rp "Install (1) or Uninstall (2) base packages? -->  " base_response
case "$base_response" in
	1)
		echo "::: The following will be installed: "
		printf '%s\n' "${apt_array[@]}"
		echo ""
		read -rp "::: Continue? [Y/n] -->  " install_response
		case "$install_response" in
			[yY])
				INSTALL_NIX_UTILS
				INSTALL_PYTHON3_UTILS
				MKDIR_GITHUB
				echo -n "( •_•)"
				sleep .75
				echo -n -e "\r( •_•)>⌐■-■"
				sleep .75
				echo -n -e "\r               "
				echo  -e "\r(⌐■_■)"
				sleep .5
				;;
			*)
				;;
		esac
		;;
	2)
		echo "::: The following will be removed:  "
		printf '%s\n' "${apt_array[@]}"
		read -rp "::: Are you sure? [y/N]  " uninstall_response
		case "$uninstall_response" in
			[yY])
				UNINSTALL_STUFF
				echo "::: Done."
				;;
			*)
				;;
		esac
esac
