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

# python3
python_array=(httpie youtube-dl requests streamlink)

INSTALL_STUFF(){
  # install *nix utilities
  apt_install='apt install'
  for item in ${apt_array[*]} ; do
    $apt_install "$item"
  done

  # install python utilities
  pip_install='sudo -H pip3 install'
  for item in ${python_array[*]} ; do
    $pip_install "$item"
  done
}

UNINSTALL_STUFF(){
  # apt crap
  APT_ZAP='sudo apt-get purge'
  CLEANUP='sudo apt-get autoclean ; sudo apt-get autoremove ; sudo apt-get clean'

  for item in ${apt_array[*]} ; do
    $APT_ZAP "$item"
  done
  $CLEANUP

  # python crap
  PYTHON_ZAP='sudo -H pip3 uninstall'
  for item in ${python_array[*]} ; do
    $PYTHON_ZAP "$item"
  done
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
  *)
    echo "::: Please enter (1) or (2)"
    ;;
esac    
