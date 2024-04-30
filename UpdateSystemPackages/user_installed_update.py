#!/usr/bin/env python3

"""
A general purpose script for updating various things on a system.
Mainly a pythonic wrapper around various shell commands.
"""

import os
import subprocess
import sys
from pathlib import Path


def bootstrap_venv():
    script_dir = Path(__file__).resolve().parent
    venv_dir = script_dir / "venv"
    venv_python = venv_dir / "bin" / "python"

    if not venv_dir.exists():
        print("No virtual environment found. Setting one up...")
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
        print(f"Virtual environment created at {venv_dir}")

    if sys.executable != str(venv_python):
        print(f"Activating virtual environment at {venv_dir}")
        os.execl(str(venv_python), "python", *sys.argv)

    requirements_path = script_dir / "requirements.txt"
    if requirements_path.exists():
        print("Installing dependencies from requirements.txt...")
        subprocess.run(
            [str(venv_python), "-m", "pip", "install", "-r", str(requirements_path)],
            check=True,
        )
    else:
        print("requirements.txt not found, skipping dependency installation.")


bootstrap_venv()

import argparse
import asyncio
import getpass
import logging
import random
import re
import shutil
from functools import partial
from typing import List

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

    def run_brew_doctor(self) -> None:
        print(yellow("::: Running random brew doctor"))
        subprocess.run(["brew", "doctor"], check=False)

    def update_homebrew(self) -> None:
        print(green("::: Updating Homebrew"))
        subprocess.run(["brew", "update"], check=False)
        subprocess.run(["brew", "upgrade"], check=False)
        subprocess.run(["brew", "upgrade", "--cask", "--greedy"], check=False)

    def cleanup_homebrew(self) -> None:
        print(green("::: Running brew cleanup"))
        subprocess.run(["brew", "cleanup"], check=False)
        subprocess.run(["brew", "cleanup", "-s", "--prune=all"], check=False)

    def homebrew_upgrade(self, args: argparse.Namespace) -> None:
        """Updating homebrew packages."""
        if OS in ["linux", "darwin"] and shutil.which("brew"):
            if random.randint(0, 3) == 1:
                self.run_brew_doctor()

            self.update_homebrew()

            if (
                args.no_input
                or input(blue("Cleanup Homebrew? [y/N] --> ", ["italic"])).lower()
                == "y"
            ):
                self.cleanup_homebrew()

    def pip_upgrade_new(self) -> None:
        subprocess.run(
            ["python3", "-m", "pip_review", "--auto", "--continue-on-fail"],
            check=False,
        )

    def pip_upgrade_old(self) -> None:
        pip_packages = []
        for line in (
            subprocess.run(
                ["python3", "-m", "pip", "list", "--outdated"],
                capture_output=True,
                check=False,
                text=True,
            )
            .stdout.strip()
            .split("\n")
        ):
            # output only the pip package names and not the versions
            if re.search(r"\s\d+\.", line):
                pip_packages.append(line.split(" ")[0])
                subprocess.run(
                    ["python3", "-m", "pip", "install", "--upgrade"],
                    check=False + pip_packages,
                )

    def python_upgrade(self, args: argparse.Namespace) -> None:
        """Providing a couple of ways to update python/pip packages.
        The new method uses the pip-review tool, which is an abstraction around pip.
        The old method uses pip directly."""
        try:
            self.pip_upgrade_new()
        except Exception as pip_failure:
            logging.warning(pip_failure)
            print("::: trying the old method...")
            self.pip_upgrade_old()

    def apt_upgrade(self, password: str) -> None:
        """Updating apt packages for ubuntu/debian distros."""
        apt_cmds = ["update", "upgrade", "dist-upgrade", "autoremove", "autoclean"]
        for cmd in apt_cmds:
            self.run_with_sudo(["apt-get", "-y", cmd], password)

    def ruby_update(self, password: str) -> None:
        """Updating ruby gems. For some reason, MacOS doesn't like it if you don't use sudo."""
        if OS == "darwin":
            print(green("::: Updating ruby gems"))
            self.run_with_sudo(["gem", "update", "-n", "/usr/local/bin/"], password)
            self.run_with_sudo(
                ["gem", "update", "-n", "/usr/local/bin/", "--system"], password
            )
            self.run_with_sudo(["gem", "update"], password)
            self.run_with_sudo(["gem", "update", "--system"], password)

    def apple_upgrade(self) -> None:
        """Updating MacOS software."""
        if OS == "darwin":
            print(green("::: Updating MacOS software"))
            subprocess.run(["softwareupdate", "--list"], check=False)
            print(green("::: Installing all available app store updates"))
            subprocess.run(["mas", "outdated"], check=False)
            subprocess.run(["mas", "upgrade"], check=False)

    def update_git_repo(self, repo: Path) -> None:
        print(blue(f"::: Updating {repo.name}"))
        result = subprocess.run(
            ["git", "remote", "update"],
            cwd=repo,
            check=False,
            text=True,
            capture_output=True,
        )
        if result.returncode == 0:
            print(green(f"  [Remote Update] Success"))
        else:
            print(red(f"  [Remote Update] Error: {result.stderr.strip()}"))
        # Pull and rebase
        result = subprocess.run(
            ["git", "pull", "--rebase"],
            cwd=repo,
            check=False,
            text=True,
            capture_output=True,
        )
        if result.returncode == 0:
            print(green(f"  [Pull & Rebase] Success"))
        else:
            print(red(f"  [Pull & Rebase] Error: {result.stderr.strip()}"))
        # Git garbage collection
        result = subprocess.run(
            ["git", "gc", "--auto"],
            cwd=repo,
            check=False,
            text=True,
            capture_output=True,
        )
        if result.returncode == 0:
            print(green(f"  [Garbage Collection] Success"))
        else:
            print(red(f"  [Garbage Collection] Error: {result.stderr.strip()}"))

    def is_git_repo(self, repo: Path) -> bool:
        return repo.is_dir() and (repo / ".git").exists()

    def bulk_git_update(self) -> None:
        """Updating all git repos in a directory."""
        if self.github_dir.exists():
            print(green("::: Updating git repos in", self.github_dir))
            for repo in self.github_dir.iterdir():
                if self.is_git_repo(repo):
                    self.update_git_repo(repo)
                else:
                    print(yellow(f"::: {repo.name} is not a git repo"))
        else:
            print(red(f"::: {self.github_dir} does not exist, skipping git updates"))

    def handle_cmd_update(self, cmd: str, args: argparse.Namespace) -> None:
        """Handling the update for each respective command."""
        if shutil.which(cmd):
            user_choice = input(blue(f"Update {cmd}? [y/N] --> ", ["italic"]))
            if user_choice.lower() == "y":
                update_function = {
                    "brew": self.homebrew_upgrade,
                    "gem": self.ruby_update,
                    "git": self.bulk_git_update,
                    "apple": self.apple_upgrade,
                }.get(cmd)
                if update_function:
                    if cmd == "brew":
                        update_function(args)
                    elif cmd == "gem":
                        password = getpass.getpass(f"Enter sudo password for {cmd}: ")
                        update_function(password)
                    else:
                        update_function()
                else:
                    print(f"::: Not updating {cmd}")

    def is_sudo_correct(self, password: str) -> bool:
        try:
            subprocess.run(["sudo", "-v"], input=password.encode(), check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def run_with_sudo(self, command: List[str], password: str) -> None:
        try:
            subprocess.run(
                ["sudo", "-S"] + command, input=password.encode(), check=True
            )
        except subprocess.CalledProcessError as e:
            print(red(f"Error running command: {e}"))

    async def run_with_sudo_async(self, command: List[str], password: str) -> None:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, partial(self.run_with_sudo, command, password))

    async def homebrew_upgrade_async(self, args: argparse.Namespace) -> None:
        status_dict["Homebrew"] = ["In Progress"]
        render_table(status_dict)
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, partial(self.homebrew_upgrade, args))
        status_dict["Homebrew"] = ["Done"]
        render_table(status_dict)

    async def python_upgrade_async(self, args: argparse.Namespace) -> None:
        status_dict["Python"] = ["In Progress"]
        render_table(status_dict)
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, partial(self.python_upgrade, args))
        status_dict["Python"] = ["Done"]
        render_table(status_dict)

    async def apt_upgrade_async(self, password: str) -> None:
        status_dict["APT"] = ["In Progress"]
        render_table(status_dict)
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, partial(self.apt_upgrade, password))
        status_dict["APT"] = ["Done"]
        render_table(status_dict)

    async def bulk_git_update_async(self) -> None:
        status_dict["Git"] = ["In Progress"]
        render_table(status_dict)
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.bulk_git_update)
        status_dict["Git"] = ["Done"]
        render_table(status_dict)

    async def ruby_update_async(self, password: str) -> None:
        status_dict["Ruby"] = ["In Progress"]
        render_table(status_dict)
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, partial(self.ruby_update, password))
        status_dict["Ruby"] = ["Done"]
        render_table(status_dict)

    async def apple_upgrade_async(self) -> None:
        status_dict["Apple Updates"] = ["In Progress"]
        render_table(status_dict)
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.apple_upgrade)
        status_dict["Apple Updates"] = ["Done"]
        render_table(status_dict)

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

    def parse_args(self) -> argparse.Namespace:
        """Parsing command line arguments"""
        parser = argparse.ArgumentParser(description="Update various system packages.")
        parser.add_argument(
            "-y",
            "--no-input",
            action="store_true",
            help="Run without user confirmation.",
        )

        return parser.parse_args()


async def check_apple_updates(updater: Updater, args: argparse.Namespace) -> None:
    if OS == "darwin" and not args.no_input:
        print(green("::: Checking for Apple updates"))
        await updater.run_async(["softwareupdate", "--list"], check=False)
        print(green("::: Checking for App Store updates"))
        await updater.run_async(["mas", "outdated"], check=False)
        await updater.run_async(["mas", "upgrade"], check=False)


async def main() -> None:
    github_dir = GITHUB_DIR
    updater = Updater(github_dir)
    args = updater.parse_args()

    with PasswordManager() as password_manager:
        if args.no_input:
            password = password_manager.get_password("Enter sudo password: ")
            while not updater.is_sudo_correct(password):
                print(red("::: Incorrect sudo password. Please try again."))
                password = password_manager.get_password("Enter sudo password: ")

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

            tasks.append(updater.python_upgrade_async(args))

            await asyncio.wait(
                [asyncio.shield(task) for task in tasks],
                return_when=asyncio.ALL_COMPLETED,
            )

        else:
            for cmd in cmds:
                updater.handle_cmd_update(cmd, args)

            if OS == "linux":
                if input(blue("Update apt? [y/N] --> ", ["italic"])).lower() == "y":
                    if not args.no_input:
                        password = password_manager.get_password(
                            "Enter sudo password: "
                        )
                        while not updater.is_sudo_correct(password):
                            print(red("Incorrect sudo password. Please try again."))
                            password = password_manager.get_password(
                                "Enter sudo password: "
                            )
                    await updater.apt_upgrade_async(password)

            if input(blue("Upgrade python? [y/N] --> ", ["italic"])).lower() == "y":
                print(green("::: Updating python packages"))
                await updater.python_upgrade_async(args)

            if OS == "darwin":
                if (
                    input(
                        blue("Check for Apple updates? [y/N] --> ", ["italic"])
                    ).lower()
                    == "y"
                ):
                    await updater.run_async(["softwareupdate", "--list"], check=False)

                if (
                    input(
                        blue("Check for App Store updates? [y/N] --> ", ["italic"])
                    ).lower()
                    == "y"
                ):
                    await updater.run_async(["mas", "outdated"], check=False)
                    await updater.run_async(["mas", "upgrade"], check=False)

    except KeyboardInterrupt:
        print("\n::: Program interrupted by user. Exiting gracefully...")
        sys.exit(1)


if __name__ == "__main__":
    render_table(status_dict)
    asyncio.run(main())
    render_table(status_dict)
