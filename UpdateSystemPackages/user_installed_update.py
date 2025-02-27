#!/usr/bin/env python3

"""
A general purpose script for updating various things on a system.
Mainly a pythonic wrapper around various shell commands.
"""

import os
import subprocess
import sys
import signal
from pathlib import Path


def bootstrap_venv():
    """
    Bootstraps a virtual environment for the script.
    This function checks if a virtual environment exists in the script directory.
    If not, it creates a new one ('venv')
    It then activates the venv and installs dependencies from requirements.txt, if present.
    """
    script_dir = Path(__file__).resolve().parent
    venv_dir = script_dir / "venv"
    venv_python = venv_dir / "bin" / "python"

    if not venv_dir.exists():
        print("No virtual environment found. Setting one up...")
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
        print(f"Virtual environment created at {venv_dir}")
    else:
        print(f"Virtual environment already exists at {venv_dir}")

    if sys.executable != str(venv_python):
        print(f"Activating virtual environment at {venv_dir}")
        os.execv(str(venv_python), [str(venv_python), *sys.argv])

    print(f"Using virtual environment at {venv_dir}")

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
import time
from functools import partial
from typing import Dict, List, Optional, Union
from filelock import FileLock

from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from simple_colors import blue, green, red, yellow

# Configure logging
SCRIPT_DIR = Path(__file__).resolve().parent
LOG_FILE = SCRIPT_DIR / "update.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=LOG_FILE
)

# Constants
GITHUB_DIR = Path(os.environ["HOME"]) / "Github"
OS = sys.platform


def handle_error(command, error, severity="warning"):
    """Centralized error handling for command failures."""
    if isinstance(command, list):
        cmd_str = ' '.join(command)
    else:
        cmd_str = str(command)

    error_msg = f"Error running {cmd_str}: {error}"

    if severity == "critical":
        logging.critical(error_msg)
        print(red(f"CRITICAL: {error_msg}"))
        sys.exit(1)
    elif severity == "error":
        logging.error(error_msg)
        print(red(f"ERROR: {error_msg}"))
    else:
        logging.warning(error_msg)
        print(yellow(f"WARNING: {error_msg}"))


def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown"""
    # We'll use the original system signal handler for terminal signals
    # Instead of trying to manage asyncio loop shutdown
    original_sigint = signal.getsignal(signal.SIGINT)
    original_sigterm = signal.getsignal(signal.SIGTERM)

    def signal_handler(sig, frame):
        print("\n::: Received interrupt signal. Gracefully shutting down...")
        # Call the original handler which will raise the KeyboardInterrupt exception
        if sig == signal.SIGINT and original_sigint != signal.SIG_DFL and original_sigint != signal.SIG_IGN:
            original_sigint(sig, frame)
        if sig == signal.SIGTERM and original_sigterm != signal.SIG_DFL and original_sigterm != signal.SIG_IGN:
            original_sigterm(sig, frame)
        # If we get here, there was no original handler, so just exit
        sys.exit(0)

    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, signal_handler)


class StatusTracker:
    """Class to track and display status of tasks"""

    STATES = {
        "not_started": "⏳ Not Started",
        "in_progress": "🔄 In Progress",
        "done": "✅ Done",
        "failed": "❌ Failed",
        "skipped": "⏭️ Skipped"
    }

    def __init__(self):
        self.tasks = {
            "Homebrew": "not_started",
            "Python": "not_started",
            "APT": "not_started",
            "Ruby": "not_started",
            "Git": "not_started",
            "Apple Updates": "not_started"
        }
        self.console = Console()

    def update(self, task, status):
        """Update the status of a task"""
        if task in self.tasks and status in self.STATES:
            self.tasks[task] = status
            self.render()

    def get_status(self, task):
        """Get the status of a task"""
        return self.tasks.get(task, "not_started")

    def render(self):
        """Render the status table with rich formatting"""
        table = Table(title="System Update Status")
        table.add_column("Task", style="cyan")
        table.add_column("Status")

        for task, status in self.tasks.items():
            status_text = self.STATES[status]

            if status == "done":
                table.add_row(task, Text(status_text, style="green"))
            elif status == "failed":
                table.add_row(task, Text(status_text, style="red bold"))
            elif status == "in_progress":
                table.add_row(task, Text(status_text, style="yellow"))
            elif status == "skipped":
                table.add_row(task, Text(status_text, style="blue"))
            else:  # not_started
                table.add_row(task, Text(status_text))

        self.console.clear()
        self.console.print(table)


class PasswordManager:
    """A class for managing sudo passwords with enhanced security."""

    def __init__(self):
        self._password = None
        self._validated = False
        self._sudo_refresh_task = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Cancel the refresh task if it exists
        if self._sudo_refresh_task:
            self._sudo_refresh_task.cancel()

        # Securely clear the password from memory
        if self._password:
            self._password = '\0' * len(self._password)
            self._password = None
        self._validated = False

    def get_password(self, validate_sudo=True) -> str:
        """Get the sudo password, only prompting once, with validation."""
        if not self._password:
            self._password = getpass.getpass("Enter sudo password: ")

            if validate_sudo and not self._validated:
                # Validate the password
                try:
                    subprocess.run(
                        ["sudo", "-S", "true"],
                        input=self._password.encode(),
                        check=True,
                        stderr=subprocess.PIPE,
                        stdout=subprocess.PIPE
                    )
                    self._validated = True

                    # Start a task to refresh sudo credentials periodically
                    # Only do this if we're inside a running event loop
                    try:
                        loop = asyncio.get_running_loop()
                        if not self._sudo_refresh_task:
                            self._sudo_refresh_task = loop.create_task(self._refresh_sudo_credentials())
                    except RuntimeError:
                        # Not in an event loop, which is fine in some contexts
                        pass

                except subprocess.CalledProcessError:
                    print(red("Invalid sudo password. Please try again."))
                    self._password = None
                    return self.get_password(validate_sudo)

        return self._password

    async def _refresh_sudo_credentials(self):
        """Periodically refresh sudo credentials to prevent timeout"""
        try:
            while True:
                # Refresh sudo every 60 seconds
                await asyncio.sleep(60)
                if self._password:
                    try:
                        subprocess.run(
                            ["sudo", "-S", "-v"],  # -v refreshes the timeout
                            input=self._password.encode(),
                            check=False,  # We don't want to raise an exception
                            stderr=subprocess.PIPE,
                            stdout=subprocess.PIPE
                        )
                    except Exception as e:
                        logging.warning(f"Failed to refresh sudo credentials: {e}")
        except asyncio.CancelledError:
            # Task was cancelled, just exit
            pass


class Updater:
    def __init__(self, github_dir: Path, status_tracker: StatusTracker):
        self.github_dir = github_dir
        self.status_tracker = status_tracker

    def run_with_sudo(self, command: List[str], password: str) -> subprocess.CompletedProcess:
        """Run a command with sudo, with better error handling"""
        try:
            result = subprocess.run(
                ["sudo", "-S"] + command,
                input=password.encode(),
                check=False,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                handle_error(command, result.stderr.strip())

            return result
        except Exception as e:
            handle_error(command, str(e))
            return None

    async def run_with_sudo_async(self, command: List[str], password: str) -> Optional[subprocess.CompletedProcess]:
        """Run a command with sudo asynchronously"""
        try:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None, partial(self.run_with_sudo, command, password)
            )
        except asyncio.CancelledError:
            print(yellow(f"::: Command cancelled: sudo {' '.join(command)}"))
            raise
        except Exception as e:
            handle_error(command, str(e))
            return None

    async def run_async(self, command: List[str], check: bool = False) -> str:
        """Run a command asynchronously and return its output"""
        try:
            process = await asyncio.create_subprocess_exec(
                *command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if check and process.returncode != 0:
                handle_error(command, stderr.decode().strip(), "error")
                return ""

            return stdout.decode().strip()
        except asyncio.CancelledError:
            print(yellow(f"::: Command cancelled: {' '.join(command)}"))
            raise
        except Exception as e:
            handle_error(command, str(e), "error" if check else "warning")
            return ""

    # Homebrew methods
    def run_brew_doctor(self) -> None:
        print(yellow("::: Running brew doctor"))
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

            if args.no_input or input(blue("Cleanup Homebrew? [y/N] --> ", ["italic"])).lower() == "y":
                self.cleanup_homebrew()
        else:
            print(yellow("::: Homebrew not found, skipping"))

    async def homebrew_upgrade_async(self, args: argparse.Namespace) -> None:
        self.status_tracker.update("Homebrew", "in_progress")
        try:
            if OS in ["linux", "darwin"] and shutil.which("brew"):
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, partial(self.homebrew_upgrade, args))
                self.status_tracker.update("Homebrew", "done")
            else:
                self.status_tracker.update("Homebrew", "skipped")
        except asyncio.CancelledError:
            # Just mark it as cancelled and propagate the exception
            self.status_tracker.update("Homebrew", "failed")
            print(yellow("::: Homebrew update cancelled"))
            raise
        except Exception as e:
            handle_error(["brew"], str(e))
            self.status_tracker.update("Homebrew", "failed")

    # Python methods
    def pip_upgrade_new(self) -> None:
        try:
            subprocess.run(
                ["python3", "-m", "pip_review", "--auto", "--continue-on-fail"],
                check=False
            )
        except Exception as e:
            handle_error(["pip_review"], str(e))
            raise

    def pip_upgrade_old(self) -> None:
        try:
            result = subprocess.run(
                ["python3", "-m", "pip", "list", "--outdated"],
                capture_output=True,
                check=False,
                text=True
            )

            if result.returncode != 0:
                handle_error(["pip list"], result.stderr)
                return

            pip_packages = []
            for line in result.stdout.strip().split("\n"):
                # output only the pip package names and not the versions
                if re.search(r"\s\d+\.", line):
                    pip_packages.append(line.split(" ")[0])

            if pip_packages:
                subprocess.run(
                    ["python3", "-m", "pip", "install", "--upgrade"] + pip_packages,
                    check=False
                )
        except Exception as e:
            handle_error(["pip upgrade"], str(e))

    def python_upgrade(self, args: argparse.Namespace) -> None:
        """Providing a couple of ways to update python/pip packages."""
        print(green("::: Updating python packages"))
        try:
            self.pip_upgrade_new()
        except Exception:
            print(yellow("::: Failed with pip-review, trying the old method..."))
            self.pip_upgrade_old()

    async def python_upgrade_async(self, args: argparse.Namespace) -> None:
        self.status_tracker.update("Python", "in_progress")
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, partial(self.python_upgrade, args))
            self.status_tracker.update("Python", "done")
        except asyncio.CancelledError:
            self.status_tracker.update("Python", "failed")
            print(yellow("::: Python update cancelled"))
            raise
        except Exception as e:
            handle_error(["python"], str(e))
            self.status_tracker.update("Python", "failed")

    # APT methods
    def apt_upgrade(self, password: str) -> None:
        """Updating apt packages for ubuntu/debian distros."""
        if OS == "linux" and shutil.which("apt-get"):
            apt_cmds = ["update", "upgrade", "dist-upgrade", "autoremove", "autoclean"]
            for cmd in apt_cmds:
                print(green(f"::: Running apt-get {cmd}"))
                result = self.run_with_sudo(["apt-get", "-y", cmd], password)
                if result and result.returncode != 0:
                    handle_error(["apt-get", cmd], result.stderr)
        else:
            print(yellow("::: apt-get not available on this system, skipping"))

    async def apt_upgrade_async(self, password: str) -> None:
        self.status_tracker.update("APT", "in_progress")
        try:
            if OS == "linux" and shutil.which("apt-get"):
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, partial(self.apt_upgrade, password))
                self.status_tracker.update("APT", "done")
            else:
                self.status_tracker.update("APT", "skipped")
        except asyncio.CancelledError:
            self.status_tracker.update("APT", "failed")
            print(yellow("::: APT update cancelled"))
            raise
        except Exception as e:
            handle_error(["apt"], str(e))
            self.status_tracker.update("APT", "failed")

    # Ruby methods
    def ruby_update(self, password: str) -> None:
        """Updating ruby gems. For some reason, MacOS doesn't like it if you don't use sudo."""
        if OS == "darwin" and shutil.which("gem"):
            print(green("::: Updating ruby gems"))
            commands = [
                ["gem", "update", "-n", "/usr/local/bin/"],
                ["gem", "update", "-n", "/usr/local/bin/", "--system"],
                ["gem", "update"],
                ["gem", "update", "--system"]
            ]

            for cmd in commands:
                result = self.run_with_sudo(cmd, password)
                if result and result.returncode != 0:
                    handle_error(cmd, result.stderr)
        else:
            print(yellow("::: Ruby gems not available on this system, skipping"))

    async def ruby_update_async(self, password: str) -> None:
        self.status_tracker.update("Ruby", "in_progress")
        try:
            if OS == "darwin" and shutil.which("gem"):
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, partial(self.ruby_update, password))
                self.status_tracker.update("Ruby", "done")
            else:
                self.status_tracker.update("Ruby", "skipped")
        except asyncio.CancelledError:
            self.status_tracker.update("Ruby", "failed")
            print(yellow("::: Ruby update cancelled"))
            raise
        except Exception as e:
            handle_error(["gem"], str(e))
            self.status_tracker.update("Ruby", "failed")

    # Apple methods
    def apple_upgrade(self) -> None:
        """Updating MacOS software."""
        if OS == "darwin":
            print(green("::: Checking for MacOS software updates"))
            try:
                # Check for system updates
                subprocess.run(["softwareupdate", "--list"], check=False)

                # Try to install recommended updates if no input required
                if shutil.which("softwareupdate"):
                    print(green("::: Installing recommended updates (may require interactive input)"))
                    subprocess.run(["softwareupdate", "--install", "--recommended"], check=False)

                # Check for App Store updates
                if shutil.which("mas"):
                    print(green("::: Checking for App Store updates"))
                    outdated_result = subprocess.run(
                        ["mas", "outdated"],
                        check=False,
                        capture_output=True,
                        text=True
                    )

                    if outdated_result.returncode == 0 and outdated_result.stdout.strip():
                        print(green("::: Installing App Store updates"))
                        subprocess.run(["mas", "upgrade"], check=False)
                    else:
                        print(green("::: No App Store updates available"))
                else:
                    print(yellow("::: 'mas' command not found, skipping App Store updates"))
            except Exception as e:
                handle_error(["apple-update"], str(e))
        else:
            print(yellow("::: Not running MacOS, skipping Apple updates"))

    # Git methods
    def is_git_repo(self, repo: Path) -> bool:
        """Checking if a directory is a git repo."""
        return repo.is_dir() and (repo / ".git").exists()

    def update_git_repo(self, repo: Path) -> None:
        """Update a single git repository with better error messages."""
        print(blue(f"::: Updating {repo.name}"))

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=Console()
        ) as progress:
            # Remote update
            task = progress.add_task(f"[cyan]Remote Update for {repo.name}", total=None)
            result = subprocess.run(
                ["git", "remote", "update"],
                cwd=repo,
                check=False,
                text=True,
                capture_output=True,
            )

            if result.returncode == 0:
                progress.update(task, description=f"[green]Remote Update for {repo.name} - Success")
            else:
                progress.update(task, description=f"[red]Remote Update for {repo.name} - Failed: {result.stderr.strip()}")

            # Pull and rebase
            task = progress.add_task(f"[cyan]Pull & Rebase for {repo.name}", total=None)
            result = subprocess.run(
                ["git", "pull", "--rebase"],
                cwd=repo,
                check=False,
                text=True,
                capture_output=True,
            )

            if result.returncode == 0:
                progress.update(task, description=f"[green]Pull & Rebase for {repo.name} - Success")
            else:
                progress.update(task, description=f"[red]Pull & Rebase for {repo.name} - Failed: {result.stderr.strip()}")

            # Git garbage collection
            task = progress.add_task(f"[cyan]Garbage Collection for {repo.name}", total=None)
            result = subprocess.run(
                ["git", "gc", "--auto"],
                cwd=repo,
                check=False,
                text=True,
                capture_output=True,
            )

            if result.returncode == 0:
                progress.update(task, description=f"[green]Garbage Collection for {repo.name} - Success")
            else:
                progress.update(task, description=f"[red]Garbage Collection for {repo.name} - Failed: {result.stderr.strip()}")

    def bulk_git_update(self) -> None:
        """Updating all git repos in a directory."""
        if self.github_dir.exists():
            print(green(f"::: Updating git repos in {self.github_dir}"))
            repos = [repo for repo in self.github_dir.iterdir() if self.is_git_repo(repo)]

            if not repos:
                print(yellow(f"::: No git repositories found in {self.github_dir}"))
                return

            for repo in repos:
                try:
                    self.update_git_repo(repo)
                except Exception as e:
                    handle_error(["git", "update", repo.name], str(e))
        else:
            print(yellow(f"::: {self.github_dir} does not exist, skipping git updates"))

    async def bulk_git_update_async(self) -> None:
        self.status_tracker.update("Git", "in_progress")
        try:
            if self.github_dir.exists():
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self.bulk_git_update)
                self.status_tracker.update("Git", "done")
            else:
                self.status_tracker.update("Git", "skipped")
        except asyncio.CancelledError:
            self.status_tracker.update("Git", "failed")
            print(yellow("::: Git update cancelled"))
            raise
        except Exception as e:
            handle_error(["git"], str(e))
            self.status_tracker.update("Git", "failed")

    # Interactive mode methods
    def handle_cmd_update(self, cmd: str, args: argparse.Namespace, password: Optional[str] = None) -> None:
        """Handling the update for each respective command in interactive mode."""
        # Special case for apple since it's not a direct command
        if cmd == "apple" and OS == "darwin":
            user_choice = input(blue("Check for Apple/macOS updates? [y/N] --> ", ["italic"]))
            if user_choice.lower() == "y":
                self.apple_upgrade()
                return
            else:
                print(yellow("::: Skipping Apple updates"))
                return

        # Regular command handling
        if shutil.which(cmd):
            user_choice = input(blue(f"Update {cmd}? [y/N] --> ", ["italic"]))
            if user_choice.lower() == "y":
                if cmd == "brew":
                    self.homebrew_upgrade(args)
                elif cmd == "apt" and OS == "linux":
                    if not password:
                        password = getpass.getpass("Enter sudo password: ")
                    self.apt_upgrade(password)
                elif cmd == "gem" and OS == "darwin":
                    if not password:
                        password = getpass.getpass("Enter sudo password: ")
                    self.ruby_update(password)
                elif cmd == "git":
                    self.bulk_git_update()
                elif cmd == "python":
                    self.python_upgrade(args)
                else:
                    print(yellow(f"::: Not updating {cmd}, no handler available"))
            else:
                print(yellow(f"::: Skipping {cmd} update"))
        else:
            print(yellow(f"::: {cmd} not found, skipping"))
    def parse_args(self) -> argparse.Namespace:
        """Parsing command line arguments"""
        parser = argparse.ArgumentParser(description="Update various system packages.")
        parser.add_argument(
            "-y",
            "--no-input",
            action="store_true",
            help="Run without user confirmation (non-interactive mode).",
        )
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Enable debug logging",
        )
        return parser.parse_args()


async def main() -> int:
    # Setup traditional signal handlers
    setup_signal_handlers()

    # Create status tracker
    status_tracker = StatusTracker()
    status_tracker.render()

    # Setup file lock to prevent multiple instances
    lock_file = SCRIPT_DIR / "updater.lock"

    try:
        lock = FileLock(lock_file, timeout=1)
        with lock:
            github_dir = GITHUB_DIR
            updater = Updater(github_dir, status_tracker)
            args = updater.parse_args()

            # Set logging level based on args
            if args.debug:
                logging.getLogger().setLevel(logging.DEBUG)

            # Setup password manager
            password_manager = PasswordManager()

            try:
                if args.no_input:
                    # Non-interactive mode
                    print(green("::: Running in non-interactive mode"))
                    password = password_manager.get_password()

                    # Create task list based on OS and available commands
                    tasks = []

                    # Check for brew
                    if shutil.which("brew"):
                        tasks.append(updater.homebrew_upgrade_async(args))

                    # Python updates
                    tasks.append(updater.python_upgrade_async(args))

                    # OS-specific tasks
                    if OS == "linux" and shutil.which("apt-get"):
                        tasks.append(updater.apt_upgrade_async(password))

                    if OS == "darwin":
                        # Ruby gems
                        if shutil.which("gem"):
                            tasks.append(updater.ruby_update_async(password))
                        # Apple updates
                        tasks.append(updater.apple_upgrade_async())

                    # Git updates if directory exists
                    if github_dir.exists():
                        tasks.append(updater.bulk_git_update_async())

                    # Run all tasks concurrently with a timeout
                    await asyncio.gather(*tasks, return_exceptions=True)

                else:
                    # Interactive mode
                    print(green("::: Running in interactive mode"))

                    # Ask about each available command
                    cmds = [
                        ("brew", "Homebrew"),
                        ("apt", "APT"),
                        ("gem", "Ruby Gems"),
                        ("git", "Git Repositories"),
                        ("apple", "Apple/macOS Updates"),
                        ("python", "Python Packages")
                    ]

                    # Process commands that need sudo together so we only ask for password once
                    sudo_needed = False
                    for cmd, name in cmds:
                        if cmd in ["apt", "gem"] and shutil.which(cmd):
                            sudo_needed = True
                            break

                    if sudo_needed:
                        password = password_manager.get_password()

                    # Process each command
                    for cmd, name in cmds:
                        if cmd == "apt" and OS != "linux":
                            continue
                        if cmd in ["gem", "apple"] and OS != "darwin":
                            continue

                        status_tracker.update(name, "not_started")
                        status_tracker.render()

                        if cmd == "brew" and shutil.which(cmd):
                            updater.handle_cmd_update(cmd, args)
                            status_tracker.update("Homebrew", "done")
                        elif cmd == "apt" and OS == "linux" and shutil.which("apt-get"):
                            updater.handle_cmd_update(cmd, args, password)
                            status_tracker.update("APT", "done")
                        elif cmd == "gem" and OS == "darwin" and shutil.which(cmd):
                            updater.handle_cmd_update(cmd, args, password)
                            status_tracker.update("Ruby", "done")
                        elif cmd == "git":
                            updater.handle_cmd_update(cmd, args)
                            status_tracker.update("Git", "done")
                        elif cmd == "apple" and OS == "darwin":
                            updater.handle_cmd_update(cmd, args)
                            status_tracker.update("Apple Updates", "done")
                        elif cmd == "python":
                            updater.handle_cmd_update(cmd, args)
                            status_tracker.update("Python", "done")

                print(green("::: All updates completed successfully!"))
                return 0

            except KeyboardInterrupt:
                print("\n::: Program interrupted by user. Exiting gracefully...")
                return 130  # Standard exit code for SIGINT
            except asyncio.CancelledError:
                print("\n::: Tasks cancelled. Exiting gracefully...")
                return 1
            except Exception as e:
                handle_error("main process", str(e), "error")
                return 1

    except TimeoutError:
        print(red("::: Another instance of the script is already running. Exiting..."))
        return 1
    except Exception as e:
        print(red(f"::: Unexpected error: {str(e)}"))
        logging.exception("Unexpected error in main function")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n::: Program interrupted by user. Exiting gracefully...")
        sys.exit(130)  # Standard exit code for SIGINT
