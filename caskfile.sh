#!/usr/bin/env bash

## Blindy Cask/Brewfile

if [[ $(uname -s) != "Darwin" ]] ; then
	# Ruling out non-Mac OS X systems
	echo "::: ERROR: This script will only run on Mac OS X"
	exit 1
fi

# Be sure to install HomeBrew first via 'brew.sh'
# Or via ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

# *nix utilities
brew_array=(ccat neofetch ack axel curl cmus exiftool csshx cowsay htop icdiff\
	irssi httpie lynx mplayer mtr osxfuse p7zip pstree sshfs tcpdump\
	speedtest_cli pv rtmpdump tldr wget youtube-dl zsh git m-cli\
	gnu-units lnav ranger watch iftop ffmpeg ssh-copy-id spoof-mac\
	parallel pdfgrep dtrx lepton sslh jq woof coreutils goaccess\
	zsh-syntax-highlighting mediainfo pandoc rtv cheat figlet rig fortune httrack\
	akamai bat prettyping magic-wormhole python3 heroku streamlink imagemagick aria2\
	restic ncdu minikube lazydocker dive plantuml rkhunter)

# Casks/GUI stuff
cask_array=(alfred flux firefox krisp nightowl docker lulu\
	brave-browser iterm2 atom xquartz caprine calibre ransomwhere\
	spotify beardedspice the-unarchiver gpgtools vlc vienna ubersicht vagrant\
	github-desktop gfxcardstatus numi superduper chrome-remote-desktop-host\
	handbrake carbon-copy-cloner copyq etrecheckpro charles visual-studio-code\
	malwarebytes postman jadengeller-helium oversight font-input grandperspective\
	brave-browser bunch signal android-platform-tools imageoptim deckset lastpass\
	google-play-music-desktop-player backblaze do-not-disturb reikey gas-mask appcleaner)

INSTALL_STUFF(){
	# Install HomeBrew
	ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

	# Install utilities
	brew_install='brew install'

	if which brew >/dev/null 2>&1 ; then
		for item in ${brew_array[*]} ; do
			$brew_install "$item"
		done
	fi

	# Install Caskroom
	$brew_install caskroom/cask/brew-cask

	cask_install='brew cask install'

	for item in ${cask_array[*]} ; do
		$cask_install "$item"
	done

	# Cleaning up after ourselves
	brew cleanup ; brew cask cleanup ; brew prune
}

UNINSTALL_STUFF(){
	UNINSTALL='brew uninstall'
	ZAP='brew cask zap'

	# killing brew utils
	for item in ${brew_array[*]} ; do
		$UNINSTALL "$item"
	done

	# zapping casks
	for item in ${cask_array[*]} ; do
		$ZAP "$item"
	done

	brew cleanup ; brew cask cleanup ; brew prune

	brew uninstall caskroom/cask/brew-cask

}

PURGE_HOMEBREW(){
	read -rp "Do you want to remove HomeBrew as well? [y/n]   " response
	if [[ $response == "y" ]] ; then
		## a rare instance where homebrew requires sudo privileges.
		sudo ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/uninstall)"
	else
		exit 0
	fi
}

# Now onto the actual work...

read -rp "Install (1) or Uninstall (2) ?   " response
case $response in
	1)
		INSTALL_STUFF
		;;
	2)
		read -rp "Are you sure? [y/n]  " uninstall_response
		if [[ $uninstall_response == "y" ]] ; then
			UNINSTALL_STUFF
			PURGE_HOMEBREW
		else
			exit
		fi
		;;
	*)
		echo "::: Please enter (1) or (2)"
		;;
esac
