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

from simple_colors import blue, green, yellow

script_directory = os.path.dirname(os.path.realpath(__file__))
github_directory = os.path.join(os.environ["HOME"], "Github")


def homebrew_upgrade():
    """A 'greedy' upgrade of homebrew packages."""
    if sys.platform in ["linux", "darwin"]:
        # if sys.platform == "darwin" or sys.platform == "linux":
        if random.randint(0, 3) == 1:  # running brew doctor at random
            print(yellow("::: Running random brew doctor"))
            run(["brew", "doctor"], check=False)

        print(green("::: Updating Homebrew"))
        run(["brew", "update"], check=False)
        run(["brew", "upgrade"], check=False)
        run(["brew", "upgrade", "--cask", "--greedy"], check=False)

        # Running brew cleanup
        cleanup_choice = input(blue("Cleanup Homebrew? [y/N] --> ", ["italic"]))
        if cleanup_choice.lower() == "y":
            print(green("::: Running brew cleanup"))
            run(["brew", "cleanup"], check=False)
            run(["brew", "cleanup", "-s", "--prune=all"], check=False)
        else:
            pass


def python_upgrade():
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

    user_choice = input(blue("Upgrade python? [y/N] --> ", ["italic"]))
    if user_choice.lower() == "y":
        print(green("::: Updating python packages"))
        try:
            pip_upgrade_new()
        except Exception as pip_failure:
            print(pip_failure)
            print("::: trying the old method...")
            pip_upgrade_old()
    else:
        pass


def apt_upgrade():
    """Updating apt packages for ubuntu/debian distros."""
    apt_cmds = ["update", "upgrade", "dist-upgrade", "autoremove", "autoclean"]
    for cmd in apt_cmds:
        run(["sudo", "apt-get", cmd], check=False)


def flatpak_upgrade():
    """Updating flatpak packages, if they exist"""
    run(["flatpak", "update"], check=False)


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


def ruby_update():
    """Updating ruby gems. For some reason, MacOS doesn't like it if you don't use sudo."""

    if sys.platform == "darwin":
        run(["sudo", "gem", "update", "-n", "/usr/local/bin/"], check=False)
        run(["sudo", "gem", "update", "-n", "/usr/local/bin/", "--system"], check=False)
        run(["sudo", "gem", "update"], check=False)
        run(["sudo", "gem", "update", "--system"], check=False)


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


def main():
    """Main function for running all the other functions."""
    try:

        cmds = ["brew", "flatpak", "gem", "git"]
        for cmd in cmds:
            handle_cmd_update(cmd)

        if sys.platform == "linux":
            user_choice = input(blue("Update apt? [y/N] --> ", ["italic"]))
            if user_choice.lower() == "y":
                apt_upgrade()

        python_upgrade()

        if sys.platform == "darwin":
            macos_upgrade_choice = input(
                blue("Check for Apple updates? [y/N] --> ", ["italic"])
            )
            if macos_upgrade_choice.lower() == "y":
                run(["softwareupdate", "--list"], check=False)

            appstore_choice = input(
                blue("Check for App Store updates? [y/N] --> ", ["italic"])
            )
            if appstore_choice.lower() == "y":
                run(["mas", "outdated"], check=False)
                run(["mas", "upgrade"], check=False)
    except KeyboardInterrupt:
        print("::: Exiting...")


if __name__ == "__main__":
    main()
