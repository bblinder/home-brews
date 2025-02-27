#!/usr/bin/env python3

"""
A general purpose script for updating various things on a system.
Mainly a pythonic wrapper around various shell commands.
"""

import os
import subprocess
import sys
from pathlib import Path
import asyncio
import getpass
import logging
import random
import re
import shutil
from functools import partial
from typing import List, Optional

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

    def get_password(self, prompt: str) -> str:
        if not self.password:
            self.password = getpass.getpass(prompt)
        return self.password


async def run_command(command: List[str], password: Optional[str] = None) -> subprocess.CompletedProcess:
    """Run a command with optional sudo."""
    try:
        if password:
            result = await asyncio.create_subprocess_exec(
                *command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, input=password.encode()
            )
        else:
            result = await asyncio.create_subprocess_exec(
                *command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

        stdout, stderr = await result.communicate()

        if result.returncode != 0:
            raise RuntimeError(f"Command {command} failed with {result.returncode} and error: {stderr.decode().strip()}")

        return result

    except Exception as e:
        print(red(f"Error running command: {e}"))
        sys.exit(1)


async def update_homebrew() -> None:
    """Updating Homebrew packages."""
    await run_command(["brew", "doctor"])
    await run_command(["brew", "update"])
    await run_command(["brew", "upgrade"])
    await run_command(["brew", "upgrade", "--cask", "--greedy"])


async def cleanup_homebrew() -> None:
    """Running brew cleanup."""
    await run_command(["brew", "cleanup"])
    await run_command(["brew", "cleanup", "-s", "--prune=all"])


async def update_python(password: str) -> None:
    """Updating python packages using pip-review."""
    await run_command(["python3", "-m", "pip_review", "--auto", "--continue-on-fail"], password=password)


async def update_git_repo(repo: Path) -> None:
    """Updating a git repo."""
    await run_command(["git", "remote", "update"], cwd=repo)
    await run_command(["git", "pull", "--rebase"], cwd=repo)
    await run_command(["git", "gc", "--auto"], cwd=repo)


async def update_apple_updates() -> None:
    """Updating MacOS software."""
    await run_command(["softwareupdate", "--list"])
    await run_command(["mas", "outdated"])
    await run_command(["mas", "upgrade"])


class Updater:
    def __init__(self, github_dir: Path):
        self.github_dir = github_dir

    async def homebrew_upgrade_async(self, args: argparse.Namespace) -> None:
        status_dict["Homebrew"] = ["In Progress"]
        render_table(status_dict)
        await update_homebrew()
        if not args.no_input and input(blue("Cleanup Homebrew? [y/N] --> ", ["italic"])) == "y":
            await cleanup_homebrew()
        status_dict["Homebrew"] = ["Done"]
        render_table(status_dict)

    async def python_upgrade_async(self, args: argparse.Namespace) -> None:
        status_dict["Python"] = ["In Progress"]
        render_table(status_dict)
        password_manager = PasswordManager()
        password = password_manager.get_password("Enter sudo password for Python: ")
        await update_python(password)
        status_dict["Python"] = ["Done"]
        render_table(status_dict)

    async def apt_upgrade_async(self, args: argparse.Namespace) -> None:
        status_dict["APT"] = ["In Progress"]
        render_table(status_dict)
        password_manager = PasswordManager()
        password = password_manager.get_password("Enter sudo password for APT: ")
        await run_command(["sudo", "-S"] + ["apt-get", "-y", "update"], input=password.encode())
        await run_command(["sudo", "-S"] + ["apt-get", "-y", "upgrade"], input=password.encode())
        status_dict["APT"] = ["Done"]
        render_table(status_dict)

    async def bulk_git_update_async(self, args: argparse.Namespace) -> None:
        status_dict["Git"] = ["In Progress"]
        render_table(status_dict)
        if self.github_dir.exists():
            for repo in self.github_dir.iterdir():
                if repo.is_dir() and (repo / ".git").exists():
                    await update_git_repo(repo)
                else:
                    print(yellow(f"{repo.name} is not a git repo"))
        status_dict["Git"] = ["Done"]
        render_table(status_dict)

    async def ruby_update_async(self, args: argparse.Namespace) -> None:
        status_dict["Ruby"] = ["In Progress"]
        render_table(status_dict)
        password_manager = PasswordManager()
        password = password_manager.get_password("Enter sudo password for Ruby: ")
        await run_command(["sudo", "-S"] + ["gem", "update", "-n", "/usr/local/bin/"], input=password.encode())
        await run_command(["sudo", "-S"] + ["gem", "update", "-n", "/usr/local/bin/", "--system"], input=password.encode())
        await run_command(["sudo", "-S"] + ["gem", "update"], input=password.encode())
        await run_command(["sudo", -S] + ["gem", "update", "--system"], input=password.encode())
        status_dict["Ruby"] = ["Done"]
        render_table(status_dict)

    async def apple_upgrade_async(self, args: argparse.Namespace) -> None:
        status_dict["Apple Updates"] = ["In Progress"]
        render_table(status_dict)
        await update_apple_updates()
        status_dict["Apple Updates"] = ["Done"]
        render_table(status_dict)


async def main() -> None:
    lock_file = SCRIPT_DIR / "updater.lock"
    lock = FileLock(lock_file)

    try:
        with lock.acquire(timeout=1):
            github_dir = GITHUB_DIR
            updater = Updater(github_dir)
            args = updater.parse_args()

            password_manager = PasswordManager()
            if not args.no_input:
                password = password_manager.get_password("Enter sudo password: ")
                while not updater.is_sudo_correct(password):
                    print(red("Incorrect sudo password. Please try again."))
                    password = password_manager.get_password("Enter sudo password: ")

            tasks = [
                updater.homebrew_upgrade_async(args),
                updater.python_upgrade_async(args),
                updater.bulk_git_update_async(args),
            ]

            if OS == "linux":
                tasks.append(updater.apt_upgrade_async(args))
            elif OS == "darwin":
                tasks.append(updater.apple_upgrade_async())

            await asyncio.wait([asyncio.shield(task) for task in tasks], return_when=asyncio.ALL_COMPLETED)

    except TimeoutError:
        print(red("Another instance of the script is already running. Exiting..."))
        sys.exit(1)


if __name__ == "__main__":
    render_table(status_dict)
    asyncio.run(main())
    render_table(status_dict)
