#!/usr/bin/env python3

"""
A general purpose script for updating various things on a system.
Mainly a pythonic wrapper around various shell commands.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

import argparse
import asyncio
import getpass
import logging
import random
import re
import shutil
from functools import partial
from filelock import FileLock

from rich.console import Console
from rich.table import Table
from simple_colors import blue, green, red, yellow


# Constants
SCRIPT_DIR = Path(__file__).resolve().parent
GITHUB_DIR = Path(os.environ["HOME"]) / "Github"
OS = sys.platform

console = Console()


def render_table(status_dict: dict) -> None:
    """Render a table with the status of each task."""
    table = Table("Asynchronous Package Manager")
    table.add_column("Task", style="cyan", no_wrap=True)

    for task, status in status_dict.items():
        status_str = "".join(status)
        table.add_row(task, status_str)

    console.clear()
    console.print(table)


status_dict = {
    "Homebrew": ("Not Started", ""),
    "Python": ("Not Started", ""),
    "APT": ("Not Started", ""),
    "Ruby": ("Not Started", ""),
    "Git": ("Not Started", ""),
    "Apple Updates": ("Not Started", ""),
}


class PasswordManager:
    """A class for managing sudo passwords."""

    def __init__(self):
        self.password = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.password = None

    def get_password(self, prompt: str) -> str:
        if not self.password:
            self.password = getpass.getpass(prompt)
        return self.password


class Updater:
    def __init__(self, github_dir: Path):
        self.github_dir = github_dir

    async def run_with_sudo_async(self, command: List[str], password: str) -> None:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, partial(subprocess.run, ["sudo", "-S"] + command, input=password.encode(), check=True))

    async def homebrew_upgrade_async(self, args: argparse.Namespace) -> None:
        status_dict["Homebrew"] = ["In Progress"]
        render_table(status_dict)
        await self.run_with_sudo_async(["brew", "update"], "")
        await self.run_with_sudo_async(["brew", "upgrade"], "")
        await self.run_with_sudo_async(["brew", "upgrade", "--cask", "--greedy"], "")
        status_dict["Homebrew"] = ["Done"]
        render_table(status_dict)

    async def python_upgrade_async(self, args: argparse.Namespace) -> None:
        status_dict["Python"] = ["In Progress"]
        render_table(status_dict)
        await self.run_with_sudo_async(["python3", "-m", "pip_review", "--auto", "--continue-on-fail"], "")
        status_dict["Python"] = ["Done"]
        render_table(status_dict)

    async def apt_upgrade_async(self, password: str) -> None:
        status_dict["APT"] = ["In Progress"]
        render_table(status_dict)
        await self.run_with_sudo_async(["apt-get", "-y", "update"], password)
        await self.run_with_sudo_async(["apt-get", "-y", "upgrade"], password)
        await self.run_with_sudo_async(["apt-get", "-y", "dist-upgrade"], password)
        await self.run_with_sudo_async(["apt-get", "-y", "autoremove"], password)
        await self.run_with_sudo_async(["apt-get", "-y", "autoclean"], password)
        status_dict["APT"] = ["Done"]
        render_table(status_dict)

    async def ruby_update_async(self, password: str) -> None:
        status_dict["Ruby"] = ["In Progress"]
        render_table(status_dict)
        await self.run_with_sudo_async(["gem", "update", "-n", "/usr/local/bin/"], password)
        await self.run_with_sudo_async(["gem", "update", "-n", "/usr/local/bin/", "--system"], password)
        await self.run_with_sudo_async(["gem", "update"], password)
        await self.run_with_sudo_async(["gem", "update", "--system"], password)
        status_dict["Ruby"] = ["Done"]
        render_table(status_dict)

    async def apple_upgrade_async(self) -> None:
        status_dict["Apple Updates"] = ["In Progress"]
        render_table(status_dict)
        await self.run_with_sudo_async(["softwareupdate", "--list"], "")
        await self.run_with_sudo_async(["mas", "outdated"], "")
        await self.run_with_sudo_async(["mas", "upgrade"], "")
        status_dict["Apple Updates"] = ["Done"]
        render_table(status_dict)

    async def update_git_repo(self, repo: Path) -> None:
        print(blue(f"::: Updating {repo.name}"))
        result = await self.run_with_sudo_async(["git", "remote", "update"], "")
        if result.returncode == 0:
            print(green(f"  [Remote Update] Success"))
        else:
            print(red(f"  [Remote Update] Error: {result.stderr.strip()}"))
        # Pull and rebase
        result = await self.run_with_sudo_async(["git", "pull", "--rebase"], "")
        if result.returncode == 0:
            print(green(f"  [Pull & Rebase] Success"))
        else:
            print(red(f"  [Pull & Rebase] Error: {result.stderr.strip()}"))
        # Git garbage collection
        await self.run_with_sudo_async(["git", "gc", "--auto"], "")

    async def bulk_git_update_async(self) -> None:
        status_dict["Git"] = ["In Progress"]
        render_table(status_dict)
        if self.github_dir.exists():
            print(green("::: Updating git repos in", self.github_dir))
            for repo in self.github_dir.iterdir():
                if repo.is_dir() and (repo / ".git").exists():
                    await self.update_git_repo(repo)
                else:
                    print(yellow(f"::: {repo.name} is not a git repo"))
        else:
            print(red(f"::: {self.github_dir} does not exist, skipping git updates"))
        status_dict["Git"] = ["Done"]
        render_table(status_dict)

    async def handle_cmd_update(self, cmd: str, args: argparse.Namespace) -> None:
        if shutil.which(cmd):
            user_choice = input(blue(f"Update {cmd}? [y/N] --> ", ["italic"]))
            if user_choice.lower() == "y":
                update_function = {
                    "brew": self.homebrew_upgrade_async,
                    "gem": self.ruby_update_async,
                    "git": self.bulk_git_update_async,
                    "apple": self.apple_upgrade_async,
                }.get(cmd)
                if update_function:
                    await update_function(args)

    async def run_async(self, command: List[str], check: bool = False) -> str:
        process = await asyncio.create_subprocess_exec(
            *command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if check and process.returncode != 0:
            raise RuntimeError(
                f"Command {command} failed with {process.returncode} and error: {stderr.decode().strip()}"
            )

        return stdout.decode().strip()


async def main() -> None:
    lock_file = SCRIPT_DIR / "updater.lock"
    lock = FileLock(lock_file)

    try:
        with lock.acquire(timeout=1):
            github_dir = GITHUB_DIR
            updater = Updater(github_dir)
            args = updater.parse_args()

            with PasswordManager() as password_manager:
                if not args.no_input:
                    password = password_manager.get_password("Enter sudo password: ")
                    while not updater.is_sudo_correct(password):
                        print(red("::: Incorrect sudo password. Please try again."))
                        password = password_manager.get_password(
                            "Enter sudo password: "
                        )

            try:
                cmds = ["brew", "gem", "git"]

                if args.no_input:
                    tasks = [
                        updater.homebrew_upgrade_async(args),
                        updater.python_upgrade_async(args),
                        updater.ruby_update_async(password),
                        updater.bulk_git_update_async(),
                    ]

                    if OS == "linux":
                        tasks.append(updater.apt_upgrade_async(password))
                    elif OS == "darwin":
                        tasks.append(updater.apple_upgrade_async())

                    await asyncio.wait(
                        [asyncio.shield(task) for task in tasks],
                        return_when=asyncio.ALL_COMPLETED,
                    )

                else:
                    for cmd in cmds:
                        updater.handle_cmd_update(cmd, args)

                    if OS == "linux":
                        if (
                            input(blue("Update apt? [y/N] --> ", ["italic"])).lower()
                            == "y"
                        ):
                            if not args.no_input:
                                password = password_manager.get_password(
                                    "Enter sudo password: "
                                )
                                while not updater.is_sudo_correct(password):
                                    print(
                                        red(
                                            "Incorrect sudo password. Please try again."
                                        )
                                    )
                                    password = password_manager.get_password(
                                        "Enter sudo password: "
                                    )
                            await updater.apt_upgrade_async(password)

                    if (
                        input(blue("Upgrade python? [y/N] --> ", ["italic"])).lower()
                        == "y"
                    ):
                        print(green("::: Updating python packages"))
                        await updater.python_upgrade_async(args)

                    if OS == "darwin":
                        if (
                            input(
                                blue("Check for Apple updates? [y/N] --> ", ["italic"])
                            ).lower()
                            == "y"
                        ):
                            await updater.run_async(
                                ["softwareupdate", "--list"], check=False
                            )

                        if (
                            input(
                                blue(
                                    "Check for App Store updates? [y/N] --> ",
                                    ["italic"],
                                )
                            ).lower()
                            == "y"
                        ):
                            await updater.run_async(["mas", "outdated"], check=False)
                            await updater.run_async(["mas", "upgrade"], check=False)

            except KeyboardInterrupt:
                print("\n::: Program interrupted by user. Exiting gracefully...")
                sys.exit(1)

    except TimeoutError:
        print(red("::: Another instance of the script is already running. Exiting..."))
        sys.exit(1)


if __name__ == "__main__":
    render_table(status_dict)
    asyncio.run(main())
    render_table(status_dict)
