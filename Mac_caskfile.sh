#!/bin/sh

# Be sure to install HomeBrew first via 'brew.sh'
# Or via ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

array=(flux ccleaner google-chrome firefox flash-player adobe-reader microsoft-office slack skype livestream-producer vlc)

install_crap(){
	## Install Caskroom
	brew install caskroom/cask/brew-cask
	
	INSTALL='brew cask install'
	
	for item in ${array[*]}; do
		$INSTALL $item
	done

	# Cleaning up after ourselves
	brew cleanup ; brew cask cleanup ; brew prune
}

uninstall_crap(){
	UNINSTALL='brew cask zap'

	for item in ${array[*]}; do
		$UNINSTALL $item
	done

	brew cleanup ; brew cask cleanup ; brew prune

	brew uninstall caskroom/cask/brew-cask
}


echo "Install (1) or Uninstall (2) ?"
read response

case $response in
	1)
		install_crap
		;;
	2)
		uninstall_crap
		;;
	*)
		echo "Please enter (1) or (2)"
		;;
esac

