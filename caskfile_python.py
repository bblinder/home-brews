#!/usr/bin/env python3

import subprocess
import os
import platform
import sys
import logging


# Initialize logging
logging.basicConfig(level=logging.INFO, format="%(message)s")


def run_command(command, continue_on_error=False):
    try:
        result = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        logging.info(result.stdout)
    except subprocess.CalledProcessError as e:
        logging.error(f"An error occurred while executing {' '.join(command)}: {e}")
        logging.error(f"Error output: {e.stderr}")
        if not continue_on_error:
            sys.exit(1)


def install_homebrew():
    """
    Installs Homebrew.
    """
    logging.info("Installing HomeBrew...")
    run_command(
        [
            "/bin/bash",
            "-c",
            "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh) | bash"
        ]
    )

def install_stuff():
    """
    Installs taps, utilities/formulae, casks, and App Store apps as listed in respective arrays.
    It first installs Homebrew, then proceeds with taps, utilities, casks, and finally App Store apps.
    """

    install_homebrew()

    print("Installing taps: ", end="")
    for item in tap_array:
        run_command(["brew", "tap", item], continue_on_error=True)
        print("#", end="", flush=True)
    print(" Done!")

    print("Installing utilities/formulae: ", end="")
    for item in brew_array:
        run_command(["brew", "install", item], continue_on_error=True)
        print("#", end="", flush=True)
    print(" Done!")

    print("Installing casks: ", end="")
    for item in cask_array:
        run_command(["brew", "install", "--cask", item], continue_on_error=True)
        print("#", end="", flush=True)
    print(" Done!")

    print("Installing App Store apps: ", end="")
    for item in app_store_array:
        run_command(["mas", "install", item], continue_on_error=True)
        print("#", end="", flush=True)
    print(" Done!")

    logging.info("Cleaning up...")
    run_command(["brew", "cleanup"], continue_on_error=True)

def uninstall_stuff():
    """
    Uninstalls Homebrew utilities/formulae, casks, and App Store apps listed in respective arrays.
    It performs a cleanup after uninstalling to ensure no residual files are left.
    """
    print("Uninstalling App Store apps: ", end="")
    for item in app_store_array:
        run_command(["mas", "uninstall", item], continue_on_error=True)
        print("#", end="", flush=True)
    print(" Done!")

    print("Uninstalling utilities/formulae: ", end="")
    for item in brew_array:
        run_command(["brew", "uninstall", item], continue_on_error=True)
        print("#", end="", flush=True)
    print(" Done!")

    print("Uninstalling casks: ", end="")
    for item in cask_array:
        run_command(
            ["brew", "uninstall", "--cask", "--zap", "--ignore-dependencies", item],
            continue_on_error=True,
        )
        print("#", end="", flush=True)
    print(" Done!")

    logging.info("Cleaning up...")
    run_command(["brew", "cleanup", "-s"], continue_on_error=True)

    logging.info("Uninstalling Homebrew...")
    run_command(["brew", "uninstall", "caskroom/cask/brew-cask"], continue_on_error=True)


def purge_homebrew():
    """
    Purges Homebrew from the system.
    Called after uninstalling and asks for user confirmation before proceeding.
    """
    response = input("Do you want to remove HomeBrew as well? [y/n] ")
    if response.lower() == "y":
        run_command(
            [
                "/bin/bash",
                "-c",
                "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/uninstall.sh) | bash",
            ]
        )


# Arrays converted from the Bash script
brew_array = [
    "ccat",
    "fastfetch",
    "ack",
    "axel",
    "curl",
    "cmus",
    "exiftool",
    "csshx",
    "cowsay",
    "htop",
    "icdiff",
    "python-tk",
    "irssi",
    "httpie",
    "lynx",
    "mplayer",
    "mtr",
    "osxfuse",
    "p7zip",
    "pstree",
    "sshfs",
    "tcpdump",
    "musikcube",
    "speedtest_cli",
    "pv",
    "rtmpdump",
    "tldr",
    "wget",
    "yt-dlp",
    "zsh",
    "git",
    "m-cli",
    "pwgen",
    "glow",
    "detox",
    "gnu-units",
    "lnav",
    "ranger",
    "watch",
    "iftop",
    "ffmpeg",
    "ssh-copy-id",
    "spoof-mac",
    "fzf",
    "difftastic",
    "parallel",
    "pdfgrep",
    "dtrx",
    "sslh",
    "jq",
    "woof",
    "coreutils",
    "goaccess",
    "eza",
    "wifi-password",
    "angle-grinder",
    "zsh-syntax-highlighting",
    "mediainfo",
    "pandoc",
    "rtv",
    "cheat",
    "figlet",
    "rig",
    "fortune",
    "httrack",
    "bat",
    "prettyping",
    "magic-wormhole",
    "python3",
    "heroku",
    "streamlink",
    "imagemagick",
    "aria2",
    "restic",
    "ncdu",
    "minikube",
    "rm-improved",
    "lazydocker",
    "dive",
    "plantuml",
    "rkhunter",
    "switchaudio-osx",
    "rga",
    "mas",
    "jo",
    "monolith",
    "localsend",
]

tap_array = [
    "federico-terzi/espanso",
    "hashicorp/tap",
    "homebrew/cask",
    "homebrew/cask-fonts",
    "homebrew/cask-versions",
    "homebrew/core",
    "clangen/musikcube",
    "apparition47/tap",
    "localsend/localsend",
]

cask_array = [
    "alfred",
    "firefox",
    "krisp",
    "docker",
    "dangerzone",
    "lulu",
    "obsidian",
    "onedrive",
    "dozer",
    "keybase",
    "iterm2",
    "xquartz",
    "calibre",
    "ransomwhere",
    "microsoft-edge",
    "microsoft-auto-update",
    "telegram",
    "espanso",
    "latest",
    "spotify",
    "beardedspice",
    "the-unarchiver",
    "gpgtools",
    "iina",
    "visual-studio-code",
    "font-jetbrains-mono",
    "numi",
    "handbrake",
    "carbon-copy-cloner",
    "font-terminus",
    "yippy",
    "etrecheckpro",
    "rectangle",
    "beekeeper-studio",
    "charles",
    "visual-studio-code",
    "malwarebytes",
    "postman",
    "anki",
    "appcleaner",
    "font-juliamono",
    "skim",
    "monitorcontrol",
    "oversight",
    "font-input",
    "bunch",
    "signal",
    "android-platform-tools",
    "coteditor",
    "keka",
    "dropbox",
    "1password-cli",
    "imageoptim",
    "deckset",
    "backblaze",
    "do-not-disturb",
    "reikey",
    "gas-mask",
    "appcleaner",
    "raycast",
    "istat-menus",
]

# App Store stuff (list acquired by `mas list | awk '{print "#" $2 "\n" $1}')`
app_store_array = [
    # Things
    "904280696",
    # Simplenote
    "692867256",
    # BetterSnapTool
    "417375580",
    # Keynote
    "409183694",
    # iA Writer
    "775737590",
    # WhatsApp
    "310633997",
    # Hush
    "1544743900",
    # Notion
    "1559269364",
    # Reader
    "1179373118",
    # DaisyDisk
    "411643860",
    # Wipr
    "1320666476",
    # Cardhop
    "1290358394",
    # Craft
    "1487937127",
    # Dark Reader for Safari
    "1438243180",
    # PDFScanner
    "410968114",
    # TextSniper
    "1528890965",
    # Pages
    "409201541",
    # Reeder
    "1529448980",
    # Numbers
    "409203825",
    # Flighty
    "1358823008",
    # Bear
    "1091189122",
    # Save to Pocket
    "1477385213",
    # Yoink
    "457622435",
    # Boop
    "1518425043",
    # Ulysses
    "1225570693",
    # TestFlight
    "899247664",
    # NextDNS
    "1464122853",
]


def main():
    """
    Checks system compatibility, prompts user for install/uninstall choice.
    """
    if platform.system() != "Darwin":
        logging.error("::: ERROR: This script will only run on Mac OS")
        sys.exit(1)

    try:
        subprocess.run(["xcode-select", "-p"], check=True)
    except subprocess.CalledProcessError:
        logging.error("::: Xcode command line tools not installed")
        logging.error("::: install with 'xcode-select --install'")
        sys.exit(1)

    response = input("Install (1) or Uninstall (2) ? ")
    if response == "1":
        install_stuff()
    elif response == "2":
        uninstall_response = input("Are you sure you want to uninstall? [y/n] ")
        if uninstall_response.lower() in ["y", "yes"]:
            uninstall_stuff()
            purge_response = input("Do you want to purge Homebrew as well? [y/n] ")
            if purge_response.lower() == "y":
                purge_homebrew()
    else:
        logging.error("::: Please enter (1) or (2)")


if __name__ == "__main__":
    main()
