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

# Quick pre-requisite install:
echo -e "::: Quick pre-requisite install..."
echo -e "::: Standby..."
apt-get -qq install dirmngr > /dev/null # per APT: server for managing certificate revocation lists

# *nix utilities
apt_array=(axel vim curl python-pip python3-pip python-dev python3-dev flatpak \
    zsh git p7zip-full mtr bleachbit nmap zenmap netcat pv gdebi lynx iftop \
    tlp redshift filelight ufw glances fail2ban clementine terminator \
	spotify-client unzip exiftool mediainfo inkscape neofetch sassc autogen dh-autoreconf \
	libgdk-pixbuf2.0-dev)

# Stuff I need newer packages of. Will include the kernel here when I'm a little braver...
backports_array=(ffmpeg mkchromecast chromium vagrant virtualbox)

# python3 utils
python_array=(httpie hangups youtube-dl requests streamlink tldr paramiko gmusicapi gmusicapi-scripts cheat)

INSTALL_NIX_UTILS(){
	# Backing up our sources list
	cp /etc/apt/sources.list /etc/apt/sources.list.bak
	rm /etc/apt/sources.list
	# tweaking it to include non-free sources
	sed -e 's/main/main contrib non-free/g' /etc/apt/sources.list.bak > /etc/apt/sources.list

	# adding stretch-backports
	echo -e "\\ndeb http://ftp.us.debian.org/debian stretch-backports main contrib non-free" >> /etc/apt/sources.list

	# 1. Add the Spotify repository signing keys to be able to verify downloaded packages
	apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 0DF731E45CE24F27EEEB1450EFDC8610341D9410
	# 2. Add the Spotify repository
	echo deb http://repository.spotify.com stable non-free | tee /etc/apt/sources.list.d/spotify.list

	apt-get update ;  apt-get -y upgrade ;  apt-get -y dist-upgrade
	# install nix utilities
	apt-get install -y "${apt_array[@]}" || return 1
        apt-get -t stretch-backports install -y "${backports_array[@]}" || return 1
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

TUNNELBEAR(){
	apt-get install network-manager-openvpn-gnome
	wget https://s3.amazonaws.com/tunnelbear/linux/openvpn.zip -P /home/$username/Downloads
}

ADAPTA_ICONS(){
	rm -rf /usr/share/themes/{Adapta,Adapta-Eta,Adapta-Nokto,Adapta-Nokto-Eta}
	rm -rf ~/.local/share/themes/{Adapta,Adapta-Eta,Adapta-Nokto,Adapta-Nokto-Eta}
	rm -rf ~/.themes/{Adapta,Adapta-Eta,Adapta-Nokto,Adapta-Nokto-Eta}

	if [[ "$(command -v git)" ]] ; then
		git clone https://github.com/adapta-project/adapta-gtk-theme.git /home/$username/Downloads/adapta-gtk-theme
	fi
}

OH_MY_ZSH(){
	if [[ "$(command -v curl)" ]] ; then
		su "$username" sh -c "$(curl -fsSL https://raw.github.com/robbyrussell/oh-my-zsh/master/tools/install.sh)" || \
		su "$username" sh -c "$(wget https://raw.github.com/robbyrussell/oh-my-zsh/master/tools/install.sh -O -)"
	fi

	# sh -s /usr/bin/zsh # Changing default shell
	echo -e "\\nDon't forget to run 'chsh -s /usr/bin/zsh'\\n"
}

INSTALL_DEB_PERSONALS(){
	deb_array=('https://go.skype.com/skypeforlinux-64-preview.deb' \
		'https://launchpadlibrarian.net/337311622/paper-icon-theme_1.4+r692~daily~ubuntu16.04.1_all.deb' \
		'https://github.com/sindresorhus/caprine/releases/download/v2.9.0/caprine_2.9.0_amd64.deb' \
		'https://github.com/atom/atom/releases/download/v1.23.3/atom-amd64.deb' \
		'https://az764295.vo.msecnd.net/stable/490ef761b76b3f3b3832eff7a588aac891e5fe80/code_1.19.2-1515599945_amd64.deb' \
		'https://www.fadeinpro.com/download/demo/fadein-linux-amd64-demo.deb')

	echo -e "\\n\\n::: Installing personals:\\n"

	mkdir Deb_Packages ; cd Deb_Packages
	wget "${deb_array[@]}"

	dpkg -iR /home/$username/Deb_Packages/ || apt-get install -f || apt --fix-broken install -y
	cd ; rm -rf /home/$username/Deb_Packages

	# Installing...
	#deb_search=(`find ./ -maxdepth 1 -name "*.deb"`) # kinda a legacy array method, but it works.

	# Batch installation
	#if [[ "${#deb_search[@]}" -gt 0 ]] ; then
	#	for d in *.deb ; do
	#		dpkg -i "$d"
	#	done || apt-get install -f || apt --fix-broken install -y
		# rm *.deb* # in case of missing dependencies
	#fi
}

LAZYADMIN(){
	echo -e "::: Installing the Lazy Admin...\\n"
	wget http://www.debian.wayoflinux.com/a.downloads/pwladmin_1.0.tar.gz
	tar -xzvf pwladmin_1.0.tar.gz -C /home/$username/Downloads/
	rm /home/$username/pwladmin_1.0.tar.gz
	echo -e "\n::: Don't forget to run Lazy Admin after install. You'll need it for Firefox Quantum ;)\n\n"
	sleep 1
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

## Now onto the actual work...

read -rp "::: Enter Username --> " username
#echo "::: Username: $username"
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
				INSTALL_DEB_PERSONALS
				TUNNELBEAR
				ADAPTA_ICONS
				OH_MY_ZSH
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
