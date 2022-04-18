#!/usr/bin/env python3

import os
import sys
from shutil import which
from subprocess import run
import random

script_directory = os.path.dirname(os.path.realpath(__file__))
github_directory = os.path.join(os.environ['HOME'], 'Github')
python3_upgrade_script = os.path.join(script_directory, 'home-brews', 'pip3_upgrade.sh')


def homebrew_upgrade():
    if sys.platform == 'darwin':
        doctor = run(['brew', 'doctor'])
        if random.randint(0, 3) == 1:  # running brew doctor at random
            print("::: Running random brew doctor")
            doctor

        print("::: Updating Homebrew")
        run(['brew', 'update'])
        run(['brew', 'upgrade'])
        run(['brew', 'upgrade', '--cask'])

        # Running brew cleanup
        cleanup_choice = input("Cleanup Homebrew? [y/N] --> ")
        if cleanup_choice.lower() == 'y':
            print("::: Running brew cleanup")
            run(['brew', 'cleanup'])
            run(['brew', 'cleanup', '-s', '--prune=all'])
        else:
            pass
    else:
        print("::: Not on a mac, skipping homebrew")
        sys.exit()


def python_upgrade():
    user_choice = input("Upgrade Python? [y/N] --> ")
    if user_choice.lower() == 'y':
        if which('pip-review'):
            run(['pip-review', '--auto'])
        elif os.path.isfile(python3_upgrade_script):
            run([python3_upgrade_script])
        else:
            print("::: No pip-review or pip3_upgrade.sh found")


def apt_upgrade():
    cmds = ['update', 'upgrade', 'dist-upgrade', 'autoremove', 'autoclean']
    for cmd in cmds:
        run(['sudo', 'apt-get', cmd])


def flatpak_upgrade():
    run(['flatpak', 'update'])


def bulk_git_update():
    for repo in os.listdir(github_directory):
        repo_path = os.path.join(github_directory, repo)
        if os.path.isdir(repo_path) and not repo.startswith('.'):
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
    cmds = ['brew', 'flatpak', 'gem', 'git']
    for cmd in cmds:
        if which(cmd):
            user_choice = input(f"Update {cmd}? [y/N] --> ")
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

    if sys.platform == 'linux':
        user_choice = input("Update apt? [y/N] --> ")
        if user_choice.lower() == 'y':
            apt_upgrade()

    python_upgrade()

    if sys.platform == 'darwin':
        user_choice = input("Check for Apple updates? [y/N] --> ")
        if user_choice.lower() == 'y':
            run(['softwareupdate', '--list'])

    if sys.platform == 'darwin':
        user_choice = input("Check for App Store updates? [y/N] --> ")
        if user_choice.lower() == 'y':
            run(['mas', 'outdated'])
            run(['mas', 'upgrade'])


if __name__ == '__main__':
    main()
