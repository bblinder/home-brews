#!/usr/bin/env python3

"""
A quick method for getting the size of a file or directory using pathlib and improved algorithms.
"""

import argparse
from pathlib import Path


def get_filesize(file_path: Path) -> int:
    """Calculate the size of a file in bytes."""
    return file_path.stat().st_size


def get_dir_size(path: Path) -> int:
    """Calculate the size of a directory in bytes."""
    total_size = 0
    stack = [path]

    while stack:
        entry = stack.pop()
        if entry.is_file():
            total_size += entry.stat().st_size
        elif entry.is_dir():
            stack.extend(entry.iterdir())
    return total_size


def convert_bytes(bytes_number: int, unit: str = "auto") -> str:
    """Convert a size in bytes to a more readable format."""
    units = ["Bytes", "KB", "MB", "GB", "TB"]
    if unit != "auto":
        unit_index = units.index(unit)
        return f"{bytes_number / (1024 ** unit_index):.2f} {unit}"

    for i, unit in enumerate(units):
        if bytes_number < 1024 ** (i + 1):
            return f"{bytes_number / (1024 ** i):.2f} {unit}"
    return f"{bytes_number:.2f} {units[-1]}"


def main():
    """Parse arguments and print the size of the file or directory."""
    parser = argparse.ArgumentParser(description="Get the size of a file or directory")
    parser.add_argument("path", help="The file or directory to get the size of")
    parser.add_argument(
        "-u",
        "--unit",
        choices=["Bytes", "KB", "MB", "GB", "TB", "auto"],
        default="auto",
        help="Unit for displaying file size",
    )
    args = parser.parse_args()

    path = Path(args.path)
    try:
        if path.is_file():
            print(convert_bytes(get_filesize(path), args.unit))
        elif path.is_dir():
            print(convert_bytes(get_dir_size(path), args.unit))
        else:
            print(f"Path {args.path} is not a valid file or directory.")
    except PermissionError:
        print(f"Permission denied to access {args.path}")
    except FileNotFoundError:
        print(f"File or directory {args.path} not found.")


if __name__ == "__main__":
    main()
