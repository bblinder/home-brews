#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

if [[ "$(uname -s)" != "Linux" ]] ; then
  echo "::: ERROR: this script will only run on Linux systems"
  echo "::: Exiting..."
  exit 1
fi

# *nix utilities
apt_array=(axel vim python-pip python3-pip flatpak zsh git p7zip-full mtr)

# python3 utils
python_array=(httpie youtube-dl requests streamlink)

INSTALL_STUFF(){
	# install nix utilities
	sudo apt-get install "${apt_array[@]}"
	
	# install python (3) utilities
	sudo -H pip3 install "${python_array[@]}"
}

UNINSTALL_STUFF(){
	# apt crap
	APT_ZAP='sudo apt-get purge'
	CLEANUP='sudo apt-get autoclean ; sudo apt-get autoremove ; sudo apt-get clean'

	$APT_ZAP "${apt_array[@]}"
	$CLEANUP
	
	# python crap
	PYTHON_ZAP='sudo -H pip3 uninstall'
	$PYTHON_ZAP "${python_array[@]}"
}

## Now onto the actual work

read -rp "Install (1) or Uninstall (2) base packages? -->  " base_response
case "$base_response" in
  1)
    INSTALL_STUFF
    ;;

  2)
    read -rp "Are you sure? [y/n]  " uninstall_response
    case "$uninstall_response" in
      [yY])
        UNINSTALL_STUFF
        ;;

      *)
        ;;
    esac
esac    
