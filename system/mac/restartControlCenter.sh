#!/usr/bin/env bash

set -Eeuo pipefail

# check if MacOS
if [ "$(uname)" != "Darwin" ]; then
  echo "::: This script will run on MacOS only"
  exit 1
fi

# run as root
if [ "$EUID" -ne 0 ]
  then echo "::: Please run as root"
  exit 1
fi

restart_control_center() {
  killall ControlCenter
  if [[ $? -eq 0 ]]; then
    echo "::: ControlCenter restarted."
  else
    echo "::: ControlCenter not restarted."
  fi
}

kill_notifications(){
    killall NotificationCenter
    if [[ $? -eq 0 ]]; then
      echo "::: Notification service stopped successfully."
    else
      echo "::: Failed to restart notification service."
    fi
}

restart_control_center
kill_notifications
