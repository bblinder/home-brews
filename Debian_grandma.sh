#!/usr/bin/env bash

set -euo pipefail
IFS=$'\n\t'

if [[ "$(uname -s)" != "Linux" ]] ; then
	echo "::: ERROR: this script will only run on Linux systems"
	echo "::: Exiting..."
	exit 1
fi

if [[ "$EUID" -ne 0 ]] ; then
	echo "::: Please run as root"
	exit
fi

# *nix utilities
apt_array=(axel vim python-pip python3-pip python-dev python3-dev flatpak zsh git p7zip-full mtr \
	bleachbit nmap zenmap netcat pv gdebi lynx iftop filelight ufw ffmpeg glances fail2ban)

# python3 utils
python_array=(httpie youtube-dl requests streamlink tldr paramiko cheat)

INSTALL_NIX_UTILS(){
	sources_list='/etc/apt/sources.list'
	# backing up our sources list
	cp "$sources_list" /etc/apt/sources.list.bak
	rm "$sources_list"

	# Tweaking it to include non-free sources
	sed -e 's/main/main contrib non-free/g' /etc/apt/sources.list.bak > "$sources_list"
	# adding stretch-backports
	echo -e "\\ndeb http://ftp.us.debian.org/debian stretch-backports main contrib non-free" >> "$sources_list"

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
	Github_Dir="/home/$username/Github"
	if [[ ! -d "$Github_Dir" ]] ; then
		mkdir -p $Github_Dir ; chmod -R 777 $Github_Dir
		git clone https://github.com/bblinder/home-brews.git $Github_Dir/home-brews/
	fi
}

INSTALL_GRANDMA_PERSONALS(){
	deb_array=('https://go.skype.com/skypeforlinux-64-preview.deb' \
		'https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb')
	
	#Skype='https://go.skype.com/skypeforlinux-64.deb' # mainstream release

	echo -e "\\n\\n::: Installing personals:\\n"
	echo -e "::: Skype (preview version), Chrome (stable)...\n\n"

	if [[ "$(command -v axel)" ]] ; then
		axel -an 5 "${deb_array[@]}" || wget "${deb_array[@]}"
	fi

	# Installing...
	deb_search=(`find ./ -maxdepth 1 -name "*.deb"`) # kinda a legacy array method, but it works.

	if [[ "${#deb_search[@]}" -gt 0 ]] ; then
		for d in *.deb ; do
			dpkg -i "$d"
		done || apt --fix-broken install -y ; rm *.deb* # in case of missing dependencies
	fi
}

LAZYADMIN(){
	echo -e "::: Installing the Lazy Admin...\\n"
	wget http://www.debian.wayoflinux.com/a.downloads/pwladmin_1.0.tar.gz
	echo -e "\n::: Don't forget to run Lazy Admin after install. You'll need it for Firefox Quantum ;)\n\n"
	sleep 1.5
}

FIREWALL_RULES(){
	ufw enable
	ufw default deny incoming ; ufw default allow outgoing

	service fail2ban start
}


UNINSTALL_STUFF(){
	# python crap
	sudo -H pip3 uninstall --yes "${python_array[@]}"

	# apt crap
	apt-get purge -y "${apt_array[@]}"
	apt-get autoclean ;  apt-get autoremove ;  apt-get clean
}

## Now onto the actual work

read -rp "::: Enter Username --> " username

if [[ ! -n "$username" ]] ; then
	echo -e "::: Username can't be empty."
	exit 1
fi

echo -e "\\n::: Username is '$username'"
echo
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
				dpkg-reconfigure tzdata #double check our timezone
				LAZYADMIN
				FIREWALL_RULES

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
