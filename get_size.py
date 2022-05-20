#!/usr/bin/env python3

import os
import argparse


def get_filesize(file):
    return os.path.getsize(file)


def get_dir_size(path='.'):
    total_size = 0
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file() and entry.name.startswith('.'):
                total_size += entry.stat().st_size
            elif entry.is_file():
                total_size += entry.stat().st_size
            elif entry.is_dir():
                total_size += get_dir_size(entry.path)
    return total_size


def convert_bytes(bytes_number):
    tags = ["Bytes", "KB", "MB", "GB", "TB"]

    i = 0
    double_bytes = bytes_number

    while i < len(tags) and bytes_number >= 1024:
        double_bytes = bytes_number / 1024.0
        i += 1
        bytes_number = bytes_number / 1024

    return str(round(double_bytes, 2)) + " " + tags[i]


def main():
    parser = argparse.ArgumentParser(description='Get the size of a file or directory')
    parser.add_argument('path', help='The file or directory to get the size of')
    args = parser.parse_args()

    if os.path.isfile(args.path):
        print(convert_bytes(get_filesize(args.path)))
    elif os.path.isdir(args.path):
        print(convert_bytes(get_dir_size(args.path)))

if __name__ == '__main__':
    main()