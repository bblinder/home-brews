#!/usr/bin/env python3

import os
import sys
from shutil import which
from subprocess import run
import random
from simple_colors import *
import re
import platform

script_directory = os.path.dirname(os.path.realpath(__file__))
github_directory = os.path.join(os.environ['HOME'], 'Github')


def homebrew_upgrade():
    if sys.platform == 'darwin' or sys.platform == 'linux':
        if random.randint(0, 3) == 1:  # running brew doctor at random
            print(yellow("::: Running random brew doctor"))
            run(['brew', 'doctor'])

        print(green("::: Updating Homebrew"))
        run(['brew', 'update'])
        run(['brew', 'upgrade'])
        run(['brew', 'upgrade', '--cask'])

        # Running brew cleanup
        cleanup_choice = input(blue("Cleanup Homebrew? [y/N] --> ", ['italic']))
        if cleanup_choice.lower() == 'y':
            print(green("::: Running brew cleanup"))
            run(['brew', 'cleanup'])
            run(['brew', 'cleanup', '-s', '--prune=all'])
        else:
            pass


def python_upgrade():
    """ Providing a couple of ways to update Python/pip packages.
    The new method uses the pip-review tool, which is a wrapper around pip.
    The old method uses pip directly."""

    def pip_upgrade_old():
        pip_packages = []
        for line in run(['pip3', 'list', '--outdated'], capture_output=True).stdout.decode('utf-8').split('\n'):
            # output only the pip package names and not the versions
            if re.search(r'\s\d+\.', line):
                pip_packages.append(line.split(' ')[0])
                run(['pip3', 'install', '--upgrade'] + pip_packages)

    user_choice = input(blue("Upgrade Python? [y/N] --> ", ['italic']))
    if user_choice.lower() == 'y':
        print(green("::: Updating Python packages"))
        if which('pip-review'):
            print("::: trying with pip-review... ")
            run(['pip-review', '--auto'])
        elif which('pip-review') is None:
            # attempting to run it directly in case it's not in $PATH
            print("pip-review not found in $PATH, trying to run it directly...")
            run(["python3", "-m", "pip_review", "--auto"])
        else:
            print("::: pip-review not found on system, trying the old-fashioned way... ")
            pip_upgrade_old()


def apt_upgrade():
    apt_cmds = ['update', 'upgrade', 'dist-upgrade', 'autoremove', 'autoclean']
    for cmd in apt_cmds:
        run(['sudo', 'apt-get', cmd])


def flatpak_upgrade():
    run(['flatpak', 'update'])


def bulk_git_update():
    for repo in os.listdir(github_directory):
        repo_path = os.path.join(github_directory, repo)
        if os.path.isdir(repo_path) and not repo.startswith('.'):
            print(green(f"Updating {repo}"))
            run(['git', 'remote', 'update'], cwd=repo_path)
            run(['git', 'pull', '--rebase'], cwd=repo_path)
            run(['git', 'gc', '--auto'], cwd=repo_path)


def ruby_update():
    if sys.platform == 'darwin':
        run(['sudo', 'gem', 'update', '-n', '/usr/local/bin/'])
        run(['sudo', 'gem', 'update', '-n', '/usr/local/bin/', '--system'])
        run(['sudo', 'gem', 'update'])
        run(['sudo', 'gem', 'update', '--system'])


def main():
    cmds = ['brew', 'flatpak', 'gem', 'git']
    for cmd in cmds:
        if which(cmd):
            user_choice = input(blue(f"Update {cmd}? [y/N] --> ", ['italic']))
            if user_choice.lower() != 'y':
                continue
            else:
                if cmd == 'brew':
                    homebrew_upgrade()
                elif cmd == 'flatpak':
                    flatpak_upgrade()
                elif cmd == 'gem':
                    ruby_update()
                elif cmd == 'git':
                    bulk_git_update()

   # platform.version() doesn't work properly if using Ubuntu via WSL, so putting in an extra check.
    if "Ubuntu" in platform.version() or run(['lsb_release', '-a'], capture_output=True).stdout.decode('utf-8').split('\n')[0].split(':')[1].strip() == 'Ubuntu':
        linux_os = 'Ubuntu'
     # Running apt update if we're on Ubuntu or Debian
    if "Debian" in platform.version() or linux_os == 'Ubuntu':
        user_choice = input(blue("Update apt? [y/N] --> ", ['italic']))
        if user_choice.lower() == 'y':
            apt_upgrade()

    python_upgrade()

    if sys.platform == 'darwin':
        macos_upgrade_choice = input(blue("Check for Apple updates? [y/N] --> ", ['italic']))
        if macos_upgrade_choice.lower() == 'y':
            run(['softwareupdate', '--list'])

        appstore_choice = input(blue("Check for App Store updates? [y/N] --> ", ['italic']))
        if appstore_choice.lower() == 'y':
            run(['mas', 'outdated'])
            run(['mas', 'upgrade'])


if __name__ == '__main__':
    main()
