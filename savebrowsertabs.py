#!/usr/bin/env python3

"""
Description: A macOS-specific Python utility to save all 
open browser tabs from Safari, Firefox, or Brave Browser
to a text file on the desktop.

Usage: 
    savebrowsertabs.py [options]
"""

import argparse
import os
import platform
import sys
from subprocess import run


def save_browser_tabs(browser):
    """
    Save open browser tabs to a text file on the desktop.

    :param browser: str, name of the browser
    :return: str, path to the saved file
    """
    file_name = f"{browser} tabs.txt"
    script = f"""
    tell application "{browser}"
        set tabURLs to ""
        set windowCount to count windows
        repeat with i from 1 to windowCount
            set tabCount to count tabs of window i
            repeat with j from 1 to tabCount
                set theURL to URL of tab j of window i
                set tabURLs to tabURLs & theURL & linefeed
            end repeat
        end repeat
    end tell

    set fileName to "{file_name}"
    set desktopPath to (path to desktop as text)
    set filePath to desktopPath & fileName
    set fileReference to open for access filePath with write permission
    write tabURLs to fileReference starting at eof
    close access fileReference
    """
    run(["osascript", "-e", script])

    # return the path to the file
    return os.path.join(os.path.expanduser("~/Desktop"), file_name)


def select_browser(browsers):
    """
    Prompt the user to select a browser from the list of supported browsers.
    """
    while True:
        print("Select a browser to open tabs in:")
        for i, browser in enumerate(browsers):
            print(f"{i+1}. {browser}")
        answer = input("> ")

        try:
            selected_browser = browsers[int(answer) - 1]
            return selected_browser
        except (ValueError, IndexError):
            print("Invalid input. Please try again.")


def open_browser_tabs(tabs_file, browser):
    """
    Open browser tabs from a text file in the specified browser.
    """
    with open(tabs_file, "r", encoding="utf-8") as file:
        tabs = file.read().splitlines()

    for tab in tabs:
        run(["open", "-a", browser, tab])


def main():
    """
    Handling command line arguments, checking OS, saving browser tabs,
    and opening saved tabs in the selected browser.
    """
    # check if macOS
    if platform.system() != "Darwin":
        print("This script only works on macOS")
        sys.exit(1)

    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("--safari", action="store_true")
        parser.add_argument("--firefox", action="store_true")
        parser.add_argument("--brave", action="store_true")
        args = parser.parse_args()

        browser_mapping = {
            "safari": "Safari",
            "firefox": "Firefox",
            "brave": "Brave Browser",
        }
        browser = None

        for key, value in browser_mapping.items():
            if getattr(args, key):
                browser = value
                break

        if not browser:
            print("No browser selected")
            sys.exit(1)

        tabs_file = save_browser_tabs(browser)
        # prompt user to open tabs
        print(f"{browser} tabs saved to {tabs_file}")
        answer = input("Open tabs? (y/n) > ")
        if answer.lower() == "y":
            browsers = list(browser_mapping.values())
            selected_browser = select_browser(browsers)
            open_browser_tabs(tabs_file, selected_browser)
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)


if __name__ == "__main__":
    main()
