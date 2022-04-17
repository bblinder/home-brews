#!/usr/bin/env python3

import os
import sys
from shutil import which
from subprocess import run
import random

script_directory = os.path.dirname(os.path.realpath(__file__))
python3_upgrade_script = os.path.join(script_directory, 'pip3_upgrade.sh')


def homebrew_upgrade():
    if sys.platform == 'darwin':
        doctor = run(['brew', 'doctor'], capture_output=True)
        # run brew doctor at random
        if random.randint(0, 3) == 1:
            print("::: Running random brew doctor")
            run(['brew', 'doctor'])
            print(doctor.stdout.decode('utf-8'))

        print("::: Updating Homebrew")
        run(['brew', 'update'])
        run(['brew', 'upgrade'])
        run(['brew', 'upgrade', '--cask'])

        # Running brew cleanup
        cleanup_choice = input("Cleanup Homebrew? [y/N] ")
        if cleanup_choice.lower() == 'y':
            run(['brew', 'cleanup'])
            print("::: Running brew cleanup")
            run(['brew', 'cleanup'])
        else:
            pass

    else:
        print("::: Not on a mac, skipping homebrew")
        sys.exit()


def python_upgrade():
    run([python3_upgrade_script])


def apt_upgrade():
    run(['sudo', 'apt', 'update'])
    run(['sudo', 'apt', 'upgrade', '--yes'])
    run(['sudo', 'apt', 'dist-upgrade'])
    run(['sudo', 'apt', 'autoremove'])
    run(['sudo', 'apt', 'autoclean'])


def flatpak_upgrade():
    run(['flatpak', 'update'])


def bulk_git_update():
    github_directory = os.path.join(os.environ['HOME'], 'Github')
    for directory in github_directory:
        run(['git', 'remote', 'update'], cwd=directory)
        run(['git', 'pull', '--rebase'], cwd=directory)
        run(['git', 'gc', '--auto'], cwd=directory)


def ruby_update():
    if sys.platform == 'darwin':
        run(['sudo', 'gem', 'update', '-n', '/usr/local/bin/'])
        run(['sudo', 'gem', 'update', '-n', '/usr/local/bin/', '--system'])
        run(['sudo', 'gem', 'update'])
        run(['sudo', 'gem', 'update', '--system'])


def main():
    if which('brew'):
        brew_choice = input("Update Homebrew? [y/N] ")
        if brew_choice.lower() == 'y':
            homebrew_upgrade()

    if sys.platform == 'linux':
        apt_choice = input("Update apt repo? [y/N] ")
        if apt_choice.lower() == 'y':
            apt_upgrade()

    if which('flatpak'):
        flatpak_choice = input("Update flatpak? [y/N] ")
        if flatpak_choice.lower() == 'y':
            flatpak_upgrade()

    if python3_upgrade_script:
        python_choice = input("Update python? [y/N] ")
        if python_choice.lower() == 'y':
            python_upgrade()

    if which('gem'):
        ruby_choice = input("Update ruby? [y/N] ")
        if ruby_choice.lower() == 'y':
            ruby_update()

    if sys.platform == 'darwin':
        apple_choice = input("Check for Apple updates? [y/N] ")
        if apple_choice.lower() == 'y':
            run(['softwareupdate', '--list'])

    if sys.platform == 'darwin':
        app_store_choice = input("Check for App Store updates? [y/N] ")
        if app_store_choice.lower() == 'y':
            run(['mas', 'outdated'])
            run(['mas', 'upgrade'])


if __name__ == '__main__':
    main()
