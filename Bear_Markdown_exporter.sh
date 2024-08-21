#!/usr/bin/env bash

# uses https://github.com/andymatuschak/Bear-Markdown-Export and saves it
# to my OneDrive folder. This script is run by a cron job every day.

# Define paths
#export_dir=~/OneDrive/Bear/Bear
#backup_dir=~/OneDrive/Bear/Backup
# Default save/export path is ~/Dropbox/BearNotes
script_path=~/Github/Bear-Markdown-Export/bear_export_sync.py

# Check for required directories
if [[ ! -d "$export_dir" || ! -d "$backup_dir" ]]; then
  echo "Error: Required directories do not exist."
  exit 1
fi

# Execute the Python script
if python3 "$script_path" --out "$export_dir" --backup "$backup_dir"; then
  echo "Export successful."
  # print the number of notes exported and path to the export directory
  echo "Exported $(ls -1 "$export_dir" | wc -l) notes to $export_dir"
else
  echo "Error: Export failed."
  exit 1
fi
