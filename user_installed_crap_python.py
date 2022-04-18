#!/usr/bin/env python3

import os
import sys
from shutil import which
from subprocess import run
import random

script_directory = os.path.dirname(os.path.realpath(__file__))
github_directory = os.path.join(os.environ['HOME'], 'Github')
python3_upgrade_script = os.path.join(script_directory, 'pip3_upgrade.sh')

def homebrew_upgrade():
    if sys.platform == 'darwin':
        doctor = run(['brew', 'doctor'], capture_output=True)
        if random.randint(0, 3) == 1: #  running brew doctor at random
            print("::: Running random brew doctor")
            run([doctor])

        print("::: Updating Homebrew")
        run(['brew', 'update'])
        run(['brew', 'upgrade'])
        run(['brew', 'upgrade', '--cask'])

        # Running brew cleanup
        cleanup_choice = input("Cleanup Homebrew? [y/N] --> ")
        if cleanup_choice.lower() == 'y':
            print("::: Running brew cleanup")
            run(['brew', 'cleanup'])
        else:
            pass
    else:
        print("::: Not on a mac, skipping homebrew")
        sys.exit()


def python_upgrade():
    if which('pip-review'):
        run(['pip-review', '--auto'])
    else:
        run([python3_upgrade_script])


def apt_upgrade():
    cmds = ['update', 'upgrade', 'dist-upgrade', 'autoremove', 'autoclean']
    for cmd in cmds:
        run(['sudo', 'apt-get', cmd])
        
        
def flatpak_upgrade():
    run(['flatpak', 'update'])


def bulk_git_update():
    for repo in os.listdir(github_directory):
        repo_path = os.path.join(github_directory, repo)
        if os.path.isdir(repo_path):
            print(f"Updating {repo}")
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
    if which('brew'):
        brew_choice = input("Update Homebrew? [y/N] --> ")
        if brew_choice.lower() == 'y':
            homebrew_upgrade()

    if sys.platform == 'linux':
        apt_choice = input("Update apt repo? [y/N] --> ")
        if apt_choice.lower() == 'y':
            apt_upgrade()

    if which('flatpak'):
        flatpak_choice = input("Update flatpak? [y/N] --> ")
        if flatpak_choice.lower() == 'y':
            flatpak_upgrade()

    if python3_upgrade_script:
        python_choice = input("Update python? [y/N] --> ")
        if python_choice.lower() == 'y':
            python_upgrade()

    if which('gem'):
        ruby_choice = input("Update ruby? [y/N] --> ")
        if ruby_choice.lower() == 'y':
            ruby_update()

    if which('git'):
        git_choice = input("Update git repos? [y/N] --> ")
        if git_choice.lower() == 'y':
            bulk_git_update()

    if sys.platform == 'darwin':
        apple_choice = input("Check for Apple updates? [y/N] --> ")
        if apple_choice.lower() == 'y':
            run(['softwareupdate', '--list'])

    if sys.platform == 'darwin':
        app_store_choice = input("Check for App Store updates? [y/N] --> ")
        if app_store_choice.lower() == 'y':
            run(['mas', 'outdated'])
            run(['mas', 'upgrade'])


if __name__ == '__main__':
    main()
