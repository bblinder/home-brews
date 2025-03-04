import subprocess
import os
import platform
import sys
import logging
import json
from pathlib import Path
from typing import List, Callable, Optional, Dict, Any

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class BrewManager:
    """Manages Homebrew packages, casks, and related operations."""

    def __init__(self, config_dir: Optional[str] = None):
        """Initialize with optional configuration directory."""
        self.config_dir = config_dir or os.path.join(os.path.dirname(__file__), "config")
        self.config = self._load_configs()

    def _load_configs(self) -> Dict[str, List[str]]:
        """Load configurations from JSON files."""
        config = {
            "taps": [],
            "brews": [],
            "casks": [],
            "app_store": []
        }

        # Create config directory if it doesn't exist
        os.makedirs(self.config_dir, exist_ok=True)

        # Load from files if they exist, otherwise use empty lists
        for key in config.keys():
            file_path = os.path.join(self.config_dir, f"{key}.json")
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as f:
                        config[key] = json.load(f)
                    logger.debug(f"Loaded {len(config[key])} items from {file_path}")
                except Exception as e:
                    logger.error(f"Error loading {file_path}: {e}")
            else:
                logger.debug(f"Config file {file_path} not found. Using empty list.")

        return config

    def save_configs(self) -> None:
        """Save current configurations to JSON files."""
        os.makedirs(self.config_dir, exist_ok=True)

        for key, items in self.config.items():
            file_path = os.path.join(self.config_dir, f"{key}.json")
            try:
                with open(file_path, 'w') as f:
                    json.dump(items, f, indent=2)
                logger.info(f"Saved {len(items)} items to {file_path}")
            except Exception as e:
                logger.error(f"Error saving {file_path}: {e}")

    def run_command(self, command: List[str], continue_on_error: bool = False) -> Optional[str]:
        """Execute shell command with robust error handling."""
        command_str = " ".join(command)
        logger.debug(f"Running: {command_str}")

        try:
            result = subprocess.run(
                command,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            logger.error(f"Error executing: {command_str}")
            logger.error(f"Error output: {e.stderr}")
            if not continue_on_error:
                raise
            return None

    def install_homebrew(self) -> None:
        """Install Homebrew if not already installed."""
        if self._is_homebrew_installed():
            logger.info("Homebrew is already installed.")
            return

        logger.info("Installing Homebrew...")
        try:
            self.run_command([
                "/bin/bash",
                "-c",
                '$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)'
            ])
            logger.info("Homebrew installed successfully.")
        except Exception as e:
            logger.error(f"Failed to install Homebrew: {e}")
            sys.exit(1)

    def _is_homebrew_installed(self) -> bool:
        """Check if Homebrew is installed."""
        try:
            subprocess.run(["brew", "--version"],
                          check=True,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _process_items(self, items: List[str], action: Callable, desc: str) -> None:
        """Process a list of items with a progress indicator."""
        if not items:
            logger.info(f"No {desc} to process.")
            return

        total = len(items)
        logger.info(f"{desc.capitalize()} ({total} items):")

        for i, item in enumerate(items, 1):
            try:
                logger.info(f"[{i}/{total}] Processing {item}...")
                action(item)
            except Exception as e:
                logger.error(f"Failed to process {item}: {e}")

    def install_taps(self) -> None:
        """Install Homebrew taps."""
        def action(tap):
            self.run_command(["brew", "tap", tap], continue_on_error=True)

        self._process_items(self.config["taps"], action, "taps")

    def install_brews(self) -> None:
        """Install Homebrew formulae."""
        def action(brew):
            self.run_command(["brew", "install", brew], continue_on_error=True)

        self._process_items(self.config["brews"], action, "formulae")

    def install_casks(self) -> None:
        """Install Homebrew casks."""
        def action(cask):
            self.run_command(["brew", "install", "--cask", cask], continue_on_error=True)

        self._process_items(self.config["casks"], action, "casks")

    def install_app_store_apps(self) -> None:
        """Install Mac App Store applications."""
        def action(app_id):
            self.run_command(["mas", "install", app_id], continue_on_error=True)

        self._process_items(self.config["app_store"], action, "App Store apps")

    def uninstall_app_store_apps(self) -> None:
        """Uninstall Mac App Store applications."""
        def action(app_id):
            self.run_command(["mas", "uninstall", app_id], continue_on_error=True)

        self._process_items(self.config["app_store"], action, "App Store apps")

    def uninstall_brews(self) -> None:
        """Uninstall Homebrew formulae."""
        def action(brew):
            self.run_command(["brew", "uninstall", brew], continue_on_error=True)

        self._process_items(self.config["brews"], action, "formulae")

    def uninstall_casks(self) -> None:
        """Uninstall Homebrew casks."""
        def action(cask):
            self.run_command(
                ["brew", "uninstall", "--cask", "--zap", "--ignore-dependencies", cask],
                continue_on_error=True,
            )

        self._process_items(self.config["casks"], action, "casks")

    def cleanup(self, deep_clean: bool = False) -> None:
        """Perform Homebrew cleanup."""
        cmd = ["brew", "cleanup"]
        if deep_clean:
            cmd.append("-s")

        logger.info("Cleaning up...")
        self.run_command(cmd, continue_on_error=True)
        logger.info("Cleanup complete.")

    def purge_homebrew(self) -> None:
        """Completely remove Homebrew."""
        logger.info("Purging Homebrew...")
        try:
            self.run_command([
                "/bin/bash",
                "-c",
                '$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/uninstall.sh)'
            ])
            logger.info("Homebrew purged successfully.")
        except Exception as e:
            logger.error(f"Failed to purge Homebrew: {e}")

    def install_all(self) -> None:
        """Install everything: Homebrew, taps, formulae, casks, and App Store apps."""
        self.install_homebrew()
        self.install_taps()
        self.install_brews()
        self.install_casks()
        self.install_app_store_apps()
        self.cleanup()
        logger.info("Installation complete!")

    def uninstall_all(self) -> None:
        """Uninstall everything: App Store apps, formulae, and casks."""
        self.uninstall_app_store_apps()
        self.uninstall_brews()
        self.uninstall_casks()
        self.cleanup(deep_clean=True)
        logger.info("Uninstallation complete!")

    def add_item(self, category: str, item: str) -> None:
        """Add an item to a specific category."""
        if category not in self.config:
            logger.error(f"Unknown category: {category}")
            return

        if item not in self.config[category]:
            self.config[category].append(item)
            logger.info(f"Added {item} to {category}")
        else:
            logger.info(f"{item} is already in {category}")

    def remove_item(self, category: str, item: str) -> None:
        """Remove an item from a specific category."""
        if category not in self.config:
            logger.error(f"Unknown category: {category}")
            return

        if item in self.config[category]:
            self.config[category].remove(item)
            logger.info(f"Removed {item} from {category}")
        else:
            logger.info(f"{item} is not in {category}")


def check_system_compatibility() -> None:
    """Verify system compatibility requirements."""
    # Check for macOS
    if platform.system() != "Darwin":
        logger.error("ERROR: This script only runs on macOS")
        sys.exit(1)

    # Check for Xcode command line tools
    try:
        subprocess.run(["xcode-select", "-p"], check=True,
                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        logger.error("Xcode command line tools not installed")
        logger.error("Install with 'xcode-select --install'")
        sys.exit(1)


def get_user_choice(prompt: str, options: List[str]) -> str:
    """Get a validated choice from the user."""
    while True:
        choice = input(f"{prompt} [{'/'.join(options)}]: ").strip().lower()
        if choice in options:
            return choice
        logger.error(f"Invalid choice. Please choose from: {', '.join(options)}")


def main() -> None:
    """Main execution function."""
    check_system_compatibility()

    # Create brew manager with config directory in the same folder as the script
    brew_manager = BrewManager()

    while True:
        print("\n=== Homebrew Package Manager ===")
        print("1. Install all packages")
        print("2. Uninstall all packages")
        print("3. Manage individual components")
        print("4. Edit package lists")
        print("5. Save configuration")
        print("q. Quit")

        choice = input("\nSelect an option: ").strip().lower()

        if choice == "1":
            brew_manager.install_all()

        elif choice == "2":
            confirmation = get_user_choice("Are you sure you want to uninstall all packages?", ["y", "n"])
            if confirmation == "y":
                brew_manager.uninstall_all()

                purge_choice = get_user_choice("Do you want to purge Homebrew as well?", ["y", "n"])
                if purge_choice == "y":
                    brew_manager.purge_homebrew()

        elif choice == "3":
            while True:
                print("\n=== Manage Components ===")
                print("1. Install/update Homebrew only")
                print("2. Install taps only")
                print("3. Install formulae only")
                print("4. Install casks only")
                print("5. Install App Store apps only")
                print("6. Cleanup Homebrew")
                print("b. Back to main menu")

                component_choice = input("\nSelect an option: ").strip().lower()

                if component_choice == "1":
                    brew_manager.install_homebrew()
                elif component_choice == "2":
                    brew_manager.install_taps()
                elif component_choice == "3":
                    brew_manager.install_brews()
                elif component_choice == "4":
                    brew_manager.install_casks()
                elif component_choice == "5":
                    brew_manager.install_app_store_apps()
                elif component_choice == "6":
                    brew_manager.cleanup(deep_clean=True)
                elif component_choice == "b":
                    break
                else:
                    logger.error("Invalid choice")

        elif choice == "4":
            while True:
                print("\n=== Edit Package Lists ===")
                print("1. Add a tap")
                print("2. Add a brew formula")
                print("3. Add a cask")
                print("4. Add an App Store app")
                print("5. Remove a tap")
                print("6. Remove a brew formula")
                print("7. Remove a cask")
                print("8. Remove an App Store app")
                print("b. Back to main menu")

                edit_choice = input("\nSelect an option: ").strip().lower()

                if edit_choice == "b":
                    break

                categories = {
                    "1": "taps", "2": "brews", "3": "casks", "4": "app_store",
                    "5": "taps", "6": "brews", "7": "casks", "8": "app_store"
                }

                if edit_choice in categories:
                    category = categories[edit_choice]

                    if edit_choice in ["1", "2", "3", "4"]:
                        item = input(f"Enter name of {category[:-1]} to add: ").strip()
                        brew_manager.add_item(category, item)
                    else:
                        # Display current items
                        print(f"\nCurrent {category}:")
                        for i, item in enumerate(brew_manager.config[category], 1):
                            print(f"{i}. {item}")

                        item_idx = input(f"Enter number of {category[:-1]} to remove: ").strip()
                        try:
                            idx = int(item_idx) - 1
                            if 0 <= idx < len(brew_manager.config[category]):
                                item = brew_manager.config[category][idx]
                                brew_manager.remove_item(category, item)
                            else:
                                logger.error("Invalid number")
                        except ValueError:
                            logger.error("Please enter a number")
                else:
                    logger.error("Invalid choice")

                # Auto-save after each edit
                brew_manager.save_configs()

        elif choice == "5":
            brew_manager.save_configs()

        elif choice == "q":
            print("Exiting...")
            break

        else:
            logger.error("Invalid choice")


if __name__ == "__main__":
    main()
