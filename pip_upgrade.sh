#!/bin/bash

# Tested only on Debian 8 "Jessie"

general_packages(){
	pip list | awk '{ print $1 }' > /tmp/pip_list.txt
}

choice_packages(){
	pip list | awk '{ print $1 }' | egrep -i "(pip)|(livestreamer)|(youtube-dl)|\
    (thefuck)|(tldr)|(zenmap)|(paramiko)|(clf)|(Fabric)|\
    (speedtest-cli)|(setuptools)|(ohmu)|(httpie)" > /tmp/pip_list.txt
}

pip_upgrade(){
    while read -r package; do
        sudo pip install "$package" --upgrade
    done < /tmp/pip_list.txt &> /dev/null ; return 0 || return 1
}


read -rp "General update (1) or just the favorites? (2)" CHOICE

case "$CHOICE" in
	1)
		general_packages
		pip_upgrade
		;;
	2)
		choice_packages
		pip_upgrade
		;;
	*)
		echo "Please enter (1) or (2)"
		;;
esac

if [[ pip_upgrade -eq 0 ]] ; then
    echo "Done."
    rm /tmp/pip_list.txt
else
    echo "There was an error. Please try again."
fi

