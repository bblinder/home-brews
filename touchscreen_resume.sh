#!/bin/bash

# Fixes the intermittent touchscreen issue on my XPS 13 running Debian Jessie.
# Script stored in /opt/touchscreen-fix

set -euo pipefail

if [[ $(uname -s) != "Linux" ]] ; then
	echo "ERROR: This script will only run on Linux systems."
	exit 1
else
	/sbin/modprobe -r hid_multitouch && /sbin/modprobe hid_multitouch
fi
