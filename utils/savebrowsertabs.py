#!/usr/bin/env python3

"""
Description: A macOS-specific Python utility to save all
open browser tabs from Safari, Firefox, Edge or Brave
to a text file on the desktop.

Usage:
    savebrowsertabs.py [options]
"""

import argparse
import platform
import sys
from pathlib import Path
from subprocess import run
import re

# Constants
DESKTOP_PATH = Path.home() / "Desktop"
URL_REGEX = re.compile(r"^https?://")
BROWSER_MAPPING = {
    "safari": "Safari",
    "firefox": "Firefox",
    "brave": "Brave Browser",
    "edge": "Microsoft Edge",
}


def save_browser_tabs(browser: str) -> Path:
    """
    Save open browser tabs to a text file on the desktop.

    :param browser: name of the browser
    :return: path to the saved file
    """
    file_path = DESKTOP_PATH / f"{browser} tabs.txt"
    script = f"""
    tell application "{browser}"
        set tabURLs to ""
        repeat with w in windows
            repeat with t in tabs of w
                set tabURLs to tabURLs & URL of t & linefeed
            end repeat
        end repeat
    end tell
    do shell script "echo " & quoted form of tabURLs & " > " & quoted form of "{file_path}"
    """
    run(["osascript", "-e", script], check=True)
    return file_path


def validate_tabs_file(file_path: Path) -> bool:
    """
    Validates if the tabs file was correctly created.

    :param file_path: path to the saved file
    :return: True if the file is valid, False otherwise
    """
    if not file_path.exists():
        print(f"File {file_path} does not exist")
        return False

    with file_path.open("r", encoding="utf-8") as file:
        content = file.read().strip()

    if not content:
        print(f"File {file_path} is empty")
        return False

    invalid_urls = [line for line in content.splitlines() if not URL_REGEX.match(line)]
    if invalid_urls:
        print(f"Invalid URLs in {file_path}:")
        for url in invalid_urls:
            print(f"  {url}")
        return False

    return True


def select_browser(browsers: list) -> str:
    """
    Prompt the user to select a browser from the list of supported browsers.
    """
    while True:
        print("Select a browser to open tabs in:")
        for i, browser in enumerate(browsers, 1):
            print(f"{i}. {browser}")
        try:
            choice = int(input("> "))
            return browsers[choice - 1]
        except (ValueError, IndexError):
            print("Invalid input. Please try again.")


def open_browser_tabs(tabs_file: Path, browser: str):
    """
    Open browser tabs from a text file in the specified browser.
    """
    with tabs_file.open("r", encoding="utf-8") as file:
        tabs = [line.strip() for line in file if URL_REGEX.match(line.strip())]

    print(f"Opening {len(tabs)} tabs in {browser}...")
    for tab in tabs:
        run(["open", "-a", browser, tab], check=True)


def main():
    """
    Handling command line arguments, checking OS, saving browser tabs,
    and opening saved tabs in the selected browser.
    """
    if platform.system() != "Darwin":
        print("This script only works on macOS")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Save and open browser tabs.")
    browser_group = parser.add_mutually_exclusive_group()
    for key in BROWSER_MAPPING:
        browser_group.add_argument(
            f"--{key}", action="store_true", help=f"Use {BROWSER_MAPPING[key]}"
        )
    parser.add_argument(
        "--tabs-file", type=Path, help="Path to an existing text file with URLs to open"
    )
    args = parser.parse_args()

    try:
        if args.tabs_file:
            if not validate_tabs_file(args.tabs_file):
                print("Provided tabs file is not valid. Exiting...")
                sys.exit(1)
            selected_browser = select_browser(list(BROWSER_MAPPING.values()))
            open_browser_tabs(args.tabs_file, selected_browser)
        else:
            selected_browser = next(
                (BROWSER_MAPPING[key] for key in BROWSER_MAPPING if getattr(args, key)),
                None,
            )
            if not selected_browser:
                print("No browser selected. Use --help for usage information.")
                sys.exit(1)

            tabs_file = save_browser_tabs(selected_browser)
            if not validate_tabs_file(tabs_file):
                print("Generated tabs file is not valid. Exiting...")
                sys.exit(1)

            print(f"{selected_browser} tabs saved to {tabs_file}")
            if input("Open tabs? (y/n) > ").lower() == "y":
                target_browser = select_browser(list(BROWSER_MAPPING.values()))
                open_browser_tabs(tabs_file, target_browser)

    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
