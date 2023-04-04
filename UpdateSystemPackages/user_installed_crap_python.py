#!/usr/bin/env python3

"""
A general purpose script for updating various things on my system.
Mainly a pythonic wrapper around various shell commands.
"""

import os
import random
import re
import sys
from shutil import which
from subprocess import run
import argparse
import pexpect
import getpass

from simple_colors import blue, green, yellow

script_directory = os.path.dirname(os.path.realpath(__file__))
github_directory = os.path.join(os.environ["HOME"], "Github")

operating_system = sys.platform


def homebrew_upgrade(args):
    if sys.platform in ["linux", "darwin"]:
        if random.randint(0, 3) == 1:
            print(yellow("::: Running random brew doctor"))
            run(["brew", "doctor"], check=False)

        print(green("::: Updating Homebrew"))
        run(["brew", "update"], check=False)
        run(["brew", "upgrade"], check=False)
        run(["brew", "upgrade", "--cask", "--greedy"], check=False)

        if args.no_input or input(blue("Cleanup Homebrew? [y/N] --> ", ["italic"])).lower() == "y":
            print(green("::: Running brew cleanup"))
            run(["brew", "cleanup"], check=False)
            run(["brew", "cleanup", "-s", "--prune=all"], check=False)


def python_upgrade(args):
    """Providing a couple of ways to update python/pip packages.
    The new method uses the pip-review tool, which is an abstraction around pip.
    The old method uses pip directly."""

    def pip_upgrade_new():
        run(
            ["python3", "-m", "pip_review", "--auto", "--continue-on-fail"], check=False
        )

    def pip_upgrade_old():
        pip_packages = []
        for line in (
            run(
                ["python3", "-m", "pip", "list", "--outdated"],
                capture_output=True,
                check=False,
            )
            .stdout.decode("utf-8")
            .split("\n")
        ):
            # output only the pip package names and not the versions
            if re.search(r"\s\d+\.", line):
                pip_packages.append(line.split(" ")[0])
                run(
                    ["python3", "-m", "pip", "install", "--upgrade"],
                    check=False + pip_packages,
                )

    if args.no_input or input(blue("Upgrade python? [y/N] --> ", ["italic"])).lower() == "y":
        print(green("::: Updating python packages"))
        try:
            pip_upgrade_new()
        except Exception as pip_failure:
            print(pip_failure)
            print("::: trying the old method...")
            pip_upgrade_old()


def apt_upgrade():
    """Updating apt packages for ubuntu/debian distros."""
    apt_cmds = ["update", "upgrade", "dist-upgrade", "autoremove", "autoclean"]
    for cmd in apt_cmds:
        run_with_sudo(["apt-get, cmd"], password)


def flatpak_upgrade():
    """Updating flatpak packages, if they exist"""
    if operating_system == "linux" and which("flatpak"):
        print(green("::: Updating flatpak packages"))
        run(["flatpak", "update", "--appstream"], check=False)


def bulk_git_update():
    """Updating all git repos in a directory.
    I'm hardcoding it as 'Github', but directory can be called anything."""
    for repo in os.listdir(github_directory):
        repo_path = os.path.join(github_directory, repo)
        if os.path.isdir(repo_path) and not repo.startswith("."):
            print(green(f"Updating {repo}"))
            run(["git", "remote", "update"], cwd=repo_path, check=False)
            run(["git", "pull", "--rebase"], cwd=repo_path, check=False)
            run(["git", "gc", "--auto"], cwd=repo_path, check=False)


def ruby_update(password):
    """Updating ruby gems. For some reason, MacOS doesn't like it if you don't use sudo."""
    if operating_system == "darwin":
        print(green("::: Updating ruby gems"))
        run_with_sudo(["gem", "update", "-n", "/usr/local/bin/"], password)
        run_with_sudo(["gem", "update", "-n", "/usr/local/bin/", "--system"], password)
        run_with_sudo(["gem", "update"], password)
        run_with_sudo(["gem", "update", "--system"], password)


def handle_cmd_update(cmd):
    """Handling the update for each respective command."""
    if which(cmd):
        user_choice = input(blue(f"Update {cmd}? [y/N] --> ", ["italic"]))
        if user_choice.lower() == "y":
            update_function = {
                "brew": homebrew_upgrade,
                "flatpak": flatpak_upgrade,
                "gem": ruby_update,
                "git": bulk_git_update,
            }.get(cmd)
            if update_function:
                update_function()
            else:
                print(f"::: Not updating {cmd}")

def run_with_sudo(command, password):
    """Storing a sudo password and automatically providing it to a command."""
    sudo_command = ["sudo", "-S"] + command
    child = pexpect.spawn(" ".join(sudo_command), encoding="utf-8")
    child.expect("Password:") # this probably only works on MacOS. Need to test on Linux.
    child.sendline(password)
    child.expect(pexpect.EOF)


def parse_args():
    parser = argparse.ArgumentParser(description="Update various system packages.")
    parser.add_argument(
        "--no-input",
        action="store_true",
        help="Run the script without user input (automatically update all available packages)",
    )
    return parser.parse_args()

def main():
    args = parse_args()

    if args.no_input:
        password = getpass.getpass("Enter sudo password: ")

    try:
        cmds = ["brew", "flatpak", "gem", "git"]
        for cmd in cmds:
            if args.no_input:
                update_function = {
                    "brew": lambda: homebrew_upgrade(args),
                    "flatpak": flatpak_upgrade,
                    "gem": lambda: ruby_update(password),
                    "git": bulk_git_update,
                }.get(cmd)
                if update_function:
                    update_function()
            else:
                handle_cmd_update(cmd)

        if operating_system == "linux":
            if args.no_input or input(blue("Update apt? [y/N] --> ", ["italic"])).lower() == "y":
                apt_upgrade()

        if args.no_input or input(blue("Upgrade python? [y/N] --> ", ["italic"])).lower() == "y":
            python_upgrade(args)

        if operating_system == "darwin":
            if args.no_input or input(blue("Check for Apple updates? [y/N] --> ", ["italic"])).lower() == "y":
                run(["softwareupdate", "--list"], check=False)

            if args.no_input or input(blue("Check for App Store updates? [y/N] --> ", ["italic"])).lower() == "y":
                run(["mas", "outdated"], check=False)
                run(["mas", "upgrade"], check=False)
    except KeyboardInterrupt:
        print("::: Exiting...")

if __name__ == "__main__":
    main()
