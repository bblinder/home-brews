#!/usr/bin/env bash

set -Eeuo pipefail
IFS=$'\n\t'
trap cleanup SIGINT SIGTERM ERR EXIT

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd -P)
LIST='/tmp/pip3_list.txt' # where we're temporarily keeping our stuff

usage() {
  cat <<EOF
Usage: $(basename "${BASH_SOURCE[0]}")

Updates Python 3 packages.

Available options:

-h, --help      Print this help and exit
-v, --verbose   Print script debug info
EOF
  exit
}

cleanup() {
  trap - SIGINT SIGTERM ERR EXIT
  # script cleanup here
  rm -f "$LIST"
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

setup_colors

#trap '{ rm -f "$LIST"; }' EXIT # cleaning up on successful exit or ctrl-c.

general_packages(){
	python3 -m pip list --outdated | awk '{ print $1 }' | sed -e '/^\s*$/d' | tail -n +3 > "$LIST"
}

pip3_upgrade(){
	while read -r package; do
		python3 -m pip install "$package" --upgrade --user
	done < "$LIST" || return 1
}

if [[ -z "$LIST" ]] ; then
	rm "$LIST"
fi

echo -e "::: Updating python3 packages... please wait..."
general_packages && pip3_upgrade

if [[ pip3_upgrade ]] ; then
	echo "Done."
	rm "$LIST"
else
	echo "There was a problem. Try again."
fi
