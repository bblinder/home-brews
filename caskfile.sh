#!/bin/sh

## BlindySupport Cask/Brewfile

## A quick check to see if Homebrew is installed.

if [[ ! (-d /usr/local/Library/Homebrew) || ( -d /usr/local/Cellar) ]]
then
	echo "Homebrew not installed!"
	echo "Would you like to install it? [y/n]"
	read input
	if [[ $input == "y" ]]
	then
		ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
	fi
fi

## Install unix utilities

brew install archey
brew install axel
brew install curl
brew install exiftool
brew install csshx
brew install cowsay
brew install htop
brew install icdiff
brew install irssi
brew install lynx
brew install mplayer
brew install mtr
brew install netcat
brew install osxfuse
brew install p7zip
brew install pstree
brew install sshfs
brew install speedtest_cli
brew install pv
brew install rtmpdump
brew install tldr
brew install wget
brew install youtube-dl
brew install zsh
brew install git
brew install gnu-units
brew install lnav
brew install ranger

## Install Cask
brew install caskroom/cask/brew-cask

## Install Casks

brew cask install alfred
brew cask install flux
brew cask install ccleaner

brew cask install virtualbox
brew cask install google-chrome
brew cask install firefox

brew cask install iterm2
brew cask install adium
brew cask install slack
brew cask install skype

brew cask install sublime-text
brew cask install atom

brew cask install spotify
brew cask install livestream-producer
brew cask install gpgtools
brew cask install vlc
brew cask install wireshark
brew cask install spectacle
brew cask install github
brew cask install gfxcardstatus
brew cask install superduper
brew cask install chrome-remote-desktop-host
brew cask install xquartz
brew cask install handbrake
brew cask install teamviewer


## Use "cat caskfile.sh | sed -e 's/install/uninstall/g' > caskfile_removeall.sh && chmod a+x caskfile_removeall.sh"
## to generate a removal script for all of the above.

## Remove Homebrew entirely

if [[ -d /usr/local/Library/Homebrew ]]
then
	sudo ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/uninstall)"
else
	exit
fi

