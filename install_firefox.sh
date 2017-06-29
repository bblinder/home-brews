#!/bin/bash

# adapted from another script. Used to install the latest firefox on my Debian Stretch install.

# run with sudo.
# 1. run without any parameters to download and install.
# 2. pass one parameter: -s in order to restore symlinks only.
#
# This script will automagically download the Firefox bundle.
# Firefox bundle can be downloaded from https://www.mozilla.org/en-US/firefox/all/
# or from http://mozilla.mirrors.tds.net/pub/mozilla.org/firefox/releases/latest/linux-i686/en-US/
# or from http://download.mozilla.org/?product=firefox-latest&os=linux&lang=en-US
# or: http://download.cdn.mozilla.net/pub/mozilla.org/firefox/releases/latest/linux-i686/en-US/...
#     http://download.cdn.mozilla.net/pub/mozilla.org/firefox/releases/latest/linux-x86_64/en-US/...
# or: wget 'http://download.mozilla.org/?product=firefox-latest&os=linux&lang=en-US' -O firefox-latest.tar.bz2
#

appname=firefox
appname_proper=$(echo ${appname} | sed -E 's/^(.)(.*)$/\u\1\2/')
echo "Installing latest ${appname_proper}..."

installPath=/opt

# Make sure only root can run this script
if [ "$(id -u)" != "0" ]; then
    echo "Error: This script must be run as root." 1>&2
    exit 1
fi

function pause(){
    read -p "$*"
}

function setSymlink(){
    # param 1 is "what"
    # param 2 is "where"
    # as in: ln -s what where...
    rm -f "$2"
    #pause "after removing $2..."
    ln -s "$1" "$2"
    #pause "after restoring $2 to $1..."
}

function restoreAlternatives () {
    update-alternatives --remove-all gnome-www-browser
    update-alternatives --remove-all x-www-browser
    update-alternatives --remove-all www-browser
    update-alternatives --remove-all ${appname}

    # usage:
    # update-alternatives --install symlink name path priority
    # we can only have one alternative per 'symlink' and 'name':
    update-alternatives --install "$2" ${appname} "$1" 1000
    update-alternatives --install /usr/bin/x-www-browser x-www-browser "$1" 900
    update-alternatives --install /usr/bin/www-browser www-browser "$1" 800
    update-alternatives --install /usr/bin/gnome-www-browser gnome-www-browser "$1" 700
}

function restoreSymlinks () {
    setSymlink "$1" "$2"
    altFolder=/etc/alternatives
    if [[ -d "${altFolder}" ]]; then
        restoreAlternatives "$1" "$2"
    fi
}

echo -n "Checking if installation path exists: ${installPath}..."
if [[ ! -d "${installPath}" ]]; then
    echo
    echo "Error: Directory not found: ${installPath}."
    echo "Must be created manually."
    exit 1
else
    echo " it does."
fi

if [ $# -gt 0 ]; then
    cmd=$1
    echo -n "Argument(s) passed: $1."
    if [[ "${cmd}" == "-s" ]]; then
        echo " Will only restore symlinks..."
        restoreSymlinks "${installPath}/${appname}/${appname}" /usr/bin/${appname}
        echo "...done."
        exit 0
    else
        echo " Unknown argument(s). Will be ignored."
    fi
fi

# reference: http://download-origin.cdn.mozilla.net/pub/firefox/releases/latest/README.txt
path64="https://download.mozilla.org/?product=firefox-latest&os=linux64&lang=en-US"
path32="https://download.mozilla.org/?product=firefox-latest&os=linux&lang=en-US"
urlverdetect="https://www.mozilla.org/en-US/firefox/all/"

cd /tmp
myhtm=index.html
rm -f ${myhtm}
rm -f ${myhtm}.*

echo -n "Detecting ${appname_proper} version..."
wget ${urlverdetect} -O ${myhtm}

if [[ ! -f "${myhtm}" ]]; then
    echo
    echo "Error: Download failed for: /tmp/${myhtm}."
    echo "Cannot detect ${appname_proper} version and tarball name."
    exit 1
fi
echo " done."

remotever=$(sed -n -E '/product=firefox-[0-9\.]+-SSL&amp;os=linux&amp;lang=en-US/Ip' ${myhtm} | sed -E 's/.*product=firefox-([0-9.]+)-SSL.*/\1/gi')
localver=$(firefox -version | sed -E 's/[^\.0-9]+([0-9]+[\.0-9]*)/\1/gi')

echo "Local  ${appname_proper} version found: ${localver}."
echo "Remote ${appname_proper} version found: ${remotever}."

read -p "Install remote version? [y/N] : " decision

if [[ ${decision} != [yY]* ]]; then
    echo "Error: User denied installation. Aborting."
    exit 1
fi

cd "${installPath}"

# architecture can be read this way (returns 64 for 64-bit):
arch=$(getconf LONG_BIT)
echo "Architecture found: ${arch}."

# or this way (returns x86_64 for 64-bit):
# arch=$(uname -m)

bundle=firefox-32bit-${remotever}.tar.bz2
if [[ ${arch} == "64" ]]; then
    bundle=firefox-64bit-${remotever}.tar.bz2
fi

echo -n "Cleanup destination folder before install..."
rm -f ${bundle}
echo " done."

if [[ ${arch} == "64" ]]; then
    echo "Downloading 64-bit bundle: ${bundle}..."
    echo "From: ${path64}..."
    wget ${path64} -O ${bundle}
else
    echo "Downloading 32-bit bundle: ${bundle}..."
    echo "From: ${path32}..."
    wget ${path32} -O ${bundle}
fi

if [[ ! -f "${installPath}/${bundle}" ]]; then
    echo "Error: File not found: ${installPath}/${bundle}."
    exit 1
fi

# find out the folder name where the archive is going to be extracted:
thisFolder=$(tar -tvjf "${bundle}" | head -n 1 | sed -r 's/^.* ([^ \/]*)\/*$/\1/')

if [[ -e "${thisFolder}" ]]; then
    rm -rf "${thisFolder}"
fi

echo -n "Extracting archive..."
tar -xvjf ${bundle} > /dev/null
echo " done."

echo -n "Waiting 2 seconds..."
sleep 2
echo " done."

echo -n "Restoring symlinks..."
# restore symbolic links:
restoreSymlinks "${installPath}/${thisFolder}/${appname}" /usr/bin/${appname}
echo " done."

dtopfile=/usr/share/applications/${appname}.desktop
echo -n "Creating desktop file: ${dtopfile}..."

echo "[Desktop Entry]" > ${dtopfile}
echo "Encoding=UTF-8" >> ${dtopfile}
echo "Name=${appname_proper}" >> ${dtopfile}
echo "Comment=Browse the World Wide Web" >> ${dtopfile}
echo "GenericName=Web Browser" >> ${dtopfile}
echo "X-GNOME-FullName=Mozilla ${appname_proper} Web Browser" >> ${dtopfile}
echo "Exec=${appname} %u" >> ${dtopfile}
echo "Terminal=false" >> ${dtopfile}
echo "Type=Application" >> ${dtopfile}
echo "Icon=${appname}" >> ${dtopfile}
echo "Categories=Network;WebBrowser;" >> ${dtopfile}
echo "MimeType=text/html;text/xml;application/xhtml+xml;application/xml;application/vnd.mozilla.xul+xml;application/rss+xml;application/rdf+xml;x-scheme-handler/http;x-scheme-handler/https;" >> ${dtopfile}
echo "X-KDE-StartupNotify=true" >> ${dtopfile}

echo " done."

# cleanup
echo "Cleanup..."
echo -n "Removing: /tmp/${myhtm}..."
rm -f /tmp/${myhtm}
echo " done."
echo -n "Removing: ${installPath}/${bundle}..."
rm -f "${installPath}/${bundle}"
echo " done."
echo

echo "Installation completed! Run >${appname} -version"
echo
exit 0
