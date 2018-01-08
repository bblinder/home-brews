#!/usr/bin/env bash

set -euo pipefail
IFS=$'\n\t'

if [[ "$(uname -s)" != "Linux" ]] ; then
	echo "::: ERROR: this script will only run on Linux systems"
	echo "::: Exiting..."
	exit 1
fi

if [[ "$EUID" -ne 0 ]] ; then
	echo "Please run as root"
	exit
fi

# *nix utilities
apt_array=(axel vim python-pip python3-pip python-dev python3-dev flatpak zsh git p7zip-full mtr \
	bleachbit nmap zenmap netcat pv gdebi lynx iftop filelight ufw glances)

# python3 utils
python_array=(httpie youtube-dl requests streamlink tldr paramiko cheat)

INSTALL_NIX_UTILS(){
	# adding stretch-backports
	echo -e "\ndeb http://ftp.us.debian.org/debian stretch-backports main contrib non-free" >> /etc/apt/sources.list
	#echo -e "\ndeb http://ftp.us.debian.org/debian sid main" >> /etc/apt/sources.list
	# Apt-pinning Firefox Quantum and its dependencies
	#echo -e "Package: *\nPin: release a=stable\nPin-Priority: 500\n\nPackage *\nPin: release a=unstable\nPin-Priority: 2\n\nPackage: firefox\nPin: release a=unstable\nPin-Priority: 1001\n\nPackage: libfontconfig1\nPin: release a=unstable\nPin-Priority: 1001\n\nPackage: fontconfig-config\nPin: release a=unstable\nPin-Priority: 1001\n\nPackage: libss3\nPin: release a=unstable\nPin-Priority: 1001" > /etc/apt/preferences.d/pinning

	apt-get update ;  apt-get -y upgrade ;  apt-get -y dist-upgrade
	# install nix utilities
	apt-get install -y "${apt_array[@]}" || return 1
	# Installing Firefox Quantum
	#apt install -t sid firefox -y || return 1
}

INSTALL_PYTHON3_UTILS(){
	if [[ INSTALL_NIX_UTILS ]] ; then
		echo "::: APT Packages done. Moving on to Python packages... "
		sleep 1.5
		sudo -H pip3 install "${python_array[@]}" || return 1
	fi
}

MKDIR_GITHUB(){
	Github_Dir='/home/vagrant/Github'
	if [[ ! -d "$Github_Dir" ]] ; then
		mkdir -p "$Github_Dir"
		chmod -R 777 "$Github_Dir"
		git clone https://github.com/bblinder/home-brews.git "$Github_Dir"/home-brews/
	fi
}

INSTALL_GRANDMA_PERSONALS(){
	#Skype='https://go.skype.com/skypeforlinux-64.deb' # mainstream release
    Skype='https://go.skype.com/skypeforlinux-64-preview.deb' # Preview release
	Chrome='https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb'

	echo -e "\n\n::: Installing personals:\n"
    echo -e "::: Skype, Chrome...\n\n"
	if [[ "$(command -v axel)" ]] ; then
		axel -an 5 "$Skype"
		axel -an 5 "$Chrome"
	else
		wget "$Skype" ; wget "$Chrome"
	fi

	# Installing...
	for d in *.deb ; do
		dpkg -i "$d"
	done
}

UNINSTALL_STUFF(){
	# python crap
	sudo -H pip3 uninstall --yes "${python_array[@]}"

	# apt crap
	apt-get purge -y "${apt_array[@]}"
	apt-get autoclean ;  apt-get autoremove ;  apt-get clean
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
				INSTALL_GRANDMA_PERSONALS
				dpkg-reconfigure tzdata #d ouble check our timezone

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