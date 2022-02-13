#!/usr/bin/env bash

## Blindy Cask/Brewfile

set -Eeuo pipefail
trap cleanup SIGINT SIGTERM ERR EXIT

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd -P)

cleanup() {
  trap - SIGINT SIGTERM ERR EXIT
  # script cleanup here
}


if [[ $(uname -s) != "Darwin" ]] ; then
	# Ruling out non-Mac OS systems
	echo "::: ERROR: This script will only run on Mac OS"
	exit 1
fi

# Checking if xcode command line tools are installed.
# Can't install homebrew without it.
if [[ ! $(xcode-select -p) ]] ; then
	echo "::: Xcode command line tools not installed"
	echo "::: install with 'xcode-select --install'"
	exit 1
fi

# Be sure to install HomeBrew first via 'brew.sh'
# Or via ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

# *nix utilities
brew_array=(ccat neofetch ack axel curl cmus exiftool csshx cowsay htop icdiff\
	irssi httpie lynx mplayer mtr osxfuse p7zip pstree sshfs tcpdump musikcube\
	speedtest_cli pv rtmpdump tldr wget youtube-dl zsh git m-cli pwgen\
	gnu-units lnav ranger watch iftop ffmpeg ssh-copy-id spoof-mac fzf nextdns\
	parallel pdfgrep dtrx lepton sslh jq woof coreutils goaccess exa wifi-password\
	zsh-syntax-highlighting mediainfo pandoc rtv cheat figlet rig fortune httrack\
	akamai bat prettyping magic-wormhole python3 heroku streamlink imagemagick aria2\
	restic ncdu minikube lazydocker dive plantuml rkhunter switchaudio-osx rga mas jo)

#brew taps
tap_array=(federico-terzi/espanso hashicorp/tap homebrew/cask homebrew/cask-fonts \
	homebrew/cask-versions homebrew/core nextdns/tap brew clangen/musikcube \
	apparition47/tap)

# Casks/GUI stuff
cask_array=(alfred firefox krisp nightowl docker lulu obsidian onedrive dozer keybase \
	iterm2 xquartz caprine calibre ransomwhere microsoft-edge telegram espanso latest \
	spotify beardedspice the-unarchiver gpgtools iina visual-studio-code font-jetbrains-mono \
	numi handbrake carbon-copy-cloner font-terminus yippy etrecheckpro rectangle beekeeper-studio \
	charles visual-studio-code malwarebytes postman anki appcleaner font-juliamono skim \
	oversight font-input grandperspective bunch signal android-platform-tools coteditor \
	imageoptim deckset lastpass backblaze do-not-disturb reikey gas-mask appcleaner raycast)

# App Store stuff (list acquired by `mas list | awk '{print $1, "#"$2}')`
app_store_array=(
	#Reeder
    1529448980 \
    #Things
	904280696 \
    #Simplenote
	692867256 \
	#Keynote
    409183694 \
	#Notion Web Clipper
    1559269364 \
	#Reader
    1179373118 \
	#DaisyDisk
    411643860 \
    #Wipr
	1320666476 \
    #Cardhop
	1290358394 \
    #Craft
	1487937127 \
    #Dark Reader for Safari
	1438243180 \
    #PDFScanner
	410968114 \
    #TextSniper
	1528890965 \
    #WhatsApp
	1147396723 \
    #Bear
	1091189122 \
    #Pages
	409201541 \
    #Numbers
	409203825 \
    #Spark
	1176895641 \
    #Save to Pocket
	1477385213 \
     #Boop
	1518425043 \
    #Parcel
	639968404
)

INSTALL_STUFF(){

	# Install HomeBrew
	/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

	# install taps
	brew_tap='brew tap'

	if which brew >/dev/null 2>&1 ; then
		for item in ${tap_array[*]} ; do
			$brew_tap "$item"
		done
	fi

	# Install utilities/formulae
	brew_install='brew install'

	if which brew >/dev/null 2>&1 ; then
		for item in ${brew_array[*]} ; do
			$brew_install "$item"
		done
	fi

	# Install casks
	# (side note: caskroom was deprecated in favor of tapping homebrew/cask.)
	# (It's been reflected in the "brew taps" array above.)
	cask_install='brew install --cask'

	for item in ${cask_array[*]} ; do
		$cask_install "$item"
	done

	# Cleaning up after ourselves
	brew cleanup

	if which mas >/dev/null 2>&1 ; then
		for item in ${app_store_array[*]} ; do
			mas install "$item"
		done
	fi
}

CONFIG_PREFERENCES(){
	if INSTALL_STUFF; then
		## installing keybindings and fuzzy completion
		$(brew --prefix)/opt/fzf/install
	fi
}

UNINSTALL_STUFF(){
	UNINSTALL='brew uninstall'
	ZAP='brew uninstall --cask --zap --ignore-dependencies'

	# Uninstalling app store apps
	for item in ${app_store_array[*]} ; do
		mas uninstall "$item"
	done

	# killing brew utils
	for item in ${brew_array[*]} ; do
		$UNINSTALL "$item"
	done

	# zapping casks
	for item in ${cask_array[*]} ; do
		$ZAP "$item"
	done

	brew cleanup -s

	brew uninstall caskroom/cask/brew-cask

}

PURGE_HOMEBREW(){
	read -rp "Do you want to remove HomeBrew as well? [y/n]   " response
	if [[ $response == "y" ]] ; then
		## a rare instance where homebrew requires sudo privileges.
		/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/uninstall.sh)"
	else
		exit 0
	fi
}

# Now onto the actual work...

read -rp "Install (1) or Uninstall (2) ?   " response
case $response in
	1)
		INSTALL_STUFF
		CONFIG_PREFERENCES
		;;
	2)
		read -rp "Are you sure? [y/n]  " uninstall_response
		case "$uninstall_response" in
			[yY])
				UNINSTALL_STUFF
				PURGE_HOMEBREW
				;;
			*)
				;;
		esac
		;;
	*)
		echo "::: Please enter (1) or (2)"
		;;
esac

exit