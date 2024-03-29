#!/usr/bin/env python3

"""
A general purpose script for updating various things on my system.
Mainly a pythonic wrapper around various shell commands.
"""

import argparse
import asyncio
import getpass
import os
import random
import re
import subprocess
import sys
from functools import partial
from shutil import which
from subprocess import run

import pexpect
from simple_colors import blue, green, red, yellow

script_directory = os.path.dirname(os.path.realpath(__file__))
github_directory = os.path.join(os.environ["HOME"], "Github")

OS = sys.platform


def homebrew_upgrade(args):
    """Updating homebrew packages."""
    if sys.platform in ["linux", "darwin"] and which("brew"):
        if random.randint(0, 3) == 1:
            print(yellow("::: Running random brew doctor"))
            run(["brew", "doctor"], check=False)

        print(green("::: Updating Homebrew"))
        run(["brew", "update"], check=False)
        run(["brew", "upgrade"], check=False)
        run(["brew", "upgrade", "--cask", "--greedy"], check=False)

        if (
            args.no_input
            or input(blue("Cleanup Homebrew? [y/N] --> ", ["italic"])).lower() == "y"
        ):
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

    try:
        pip_upgrade_new()
    except Exception as pip_failure:
        print(pip_failure)
        print("::: trying the old method...")
        pip_upgrade_old()


def apt_upgrade(password):
    """Updating apt packages for ubuntu/debian distros."""
    apt_cmds = ["update", "upgrade", "dist-upgrade", "autoremove", "autoclean"]
    for cmd in apt_cmds:
        run_with_sudo(["apt-get", "-y", cmd], password)


def flatpak_upgrade():
    """Updating flatpak packages, if they exist"""
    if OS == "linux" and which("flatpak"):
        print(green("::: Updating flatpak packages"))
        run(["flatpak", "update", "--appstream"], check=False)


# def bulk_git_update():
#     """Updating all git repos in a directory.
#     I'm hardcoding it as 'Github', but directory can be called anything."""
#     for repo in os.listdir(github_directory):
#         repo_path = os.path.join(github_directory, repo)
#         if os.path.isdir(repo_path) and not repo.startswith("."):
#             print(green(f"Updating {repo}"))
#             run(["git", "remote", "update"], cwd=repo_path, check=False)
#             run(["git", "pull", "--rebase"], cwd=repo_path, check=False)
#             run(["git", "gc", "--auto"], cwd=repo_path, check=False)

def bulk_git_update() -> None:
    """Updating all git repos in a directory."""
    if GITHUB_DIR.exists():
        print(green("::: Updating git repos in", GITHUB_DIR))
        for repo in GITHUB_DIR.iterdir():
            if repo.is_dir() and (repo / ".git").exists():
                print(blue(f"::: Updating {repo.name}"))
                result = subprocess.run(["git", "remote", "update"], cwd=repo, check=False, text=True, capture_output=True)
                if result.returncode == 0:
                    print(green(f"  [Remote Update] Success"))
                else:
                    print(red(f"  [Remote Update] Error: {result.stderr.strip()}"))
                # Pull and rebase
                result = subprocess.run(["git", "pull", "--rebase"], cwd=repo, check=False, text=True, capture_output=True)
                if result.returncode == 0:
                    print(green(f"  [Pull & Rebase] Success"))
                else:
                    print(red(f"  [Pull & Rebase] Error: {result.stderr.strip()}"))
                # Git garbage collection
                result = subprocess.run(["git", "gc", "--auto"], cwd=repo, check=False, text=True, capture_output=True)
                if result.returncode == 0:
                    print(green(f"  [Garbage Collection] Success"))
                else:
                    print(red(f"  [Garbage Collection] Error: {result.stderr.strip()}"))

            else:
                print(yellow(f"::: {repo.name} is not a git repo"))
    else:
        print(red(f"::: {GITHUB_DIR} does not exist, skipping git updates"))


def ruby_update(password):
    """Updating ruby gems. For some reason, MacOS doesn't like it if you don't use sudo."""
    if OS == "darwin":
        print(green("::: Updating ruby gems"))
        run_with_sudo(["gem", "update", "-n", "/usr/local/bin/"], password)
        run_with_sudo(["gem", "update", "-n", "/usr/local/bin/", "--system"], password)
        run_with_sudo(["gem", "update"], password)
        run_with_sudo(["gem", "update", "--system"], password)


def handle_cmd_update(cmd, args=None):
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
                if cmd == "brew":
                    update_function(args)
                else:
                    update_function(password=getpass.getpass())
            else:
                print(f"::: Not updating {cmd}")


def is_sudo_correct(password):
    try:
        sudo_command = ["sudo", "-S", "echo", "correct"]
        child = pexpect.spawn(" ".join(sudo_command), encoding="utf-8")
        child.expect(".*[Pp]assword.*:")
        child.sendline(password)
        child.expect(pexpect.EOF, timeout=10)
        return True
    except pexpect.EOF:
        return False
    except pexpect.exceptions.TIMEOUT:
        return False


def run_with_sudo(command, password):
    sudo_command = ["sudo", "-S"] + command
    process = subprocess.Popen(
        sudo_command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=os.environ.copy(),
    )
    stdout, stderr = process.communicate(password + "\n")
    # print(stdout)
    if stderr:
        print(stderr)


async def run_with_sudo_async(command, password):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, partial(run_with_sudo, command, password))


async def homebrew_upgrade_async(args):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, partial(homebrew_upgrade, args))


async def python_upgrade_async(args):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, partial(python_upgrade, args))


async def apt_upgrade_async(password):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, partial(apt_upgrade, password))


async def flatpak_upgrade_async():
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, flatpak_upgrade)


async def bulk_git_update_async():
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, bulk_git_update)


async def ruby_update_async(password):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, partial(ruby_update, password))


def parse_args():
    """Parsing command line arguments"""
    parser = argparse.ArgumentParser(description="Update various system packages.")
    parser.add_argument(
        "-y",
        "--no-input",
        action="store_true",
        help="Run the script without user confirmation (automatically update all available packages)",
    )
    return parser.parse_args()


async def main():
    args = parse_args()
    if args.no_input:
        password = getpass.getpass("Enter sudo password: ")

        if not is_sudo_correct(password):
            print(red("Incorrect sudo password. Exiting..."))
            sys.exit(1)

    try:
        cmds = ["brew", "flatpak", "gem", "git"]

        if args.no_input:
            tasks = [
                homebrew_upgrade_async(args),
                flatpak_upgrade_async(),
                ruby_update_async(password),
                bulk_git_update_async(),
            ]

            if OS == "linux":
                tasks.append(apt_upgrade_async(password))

            tasks.append(python_upgrade_async(args))

            # await asyncio.gather(*tasks) # debating whether to use this or the one below
            await asyncio.wait(
                [asyncio.shield(task) for task in tasks],
                return_when=asyncio.ALL_COMPLETED,
            )

        else:
            for cmd in cmds:
                handle_cmd_update(cmd, args)

            if OS == "linux":
                if input(blue("Update apt? [y/N] --> ", ["italic"])).lower() == "y":
                    if not args.no_input:
                        password = getpass.getpass("Enter sudo password: ")

                        if not is_sudo_correct(password):
                            print(red("Incorrect sudo password. Exiting..."))
                            sys.exit(1)
                    apt_upgrade(password)

            if input(blue("Upgrade python? [y/N] --> ", ["italic"])).lower() == "y":
                print(green("::: Updating python packages"))
                python_upgrade(args)

            if OS == "darwin":
                if (
                    input(
                        blue("Check for Apple updates? [y/N] --> ", ["italic"])
                    ).lower()
                    == "y"
                ):
                    run(["softwareupdate", "--list"], check=False)

                if (
                    input(
                        blue("Check for App Store updates? [y/N] --> ", ["italic"])
                    ).lower()
                    == "y"
                ):
                    run(["mas", "outdated"], check=False)
                    run(["mas", "upgrade"], check=False)

    except KeyboardInterrupt:
        print("::: Exiting...")


if __name__ == "__main__":
    asyncio.run(main())
