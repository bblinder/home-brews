#!/bin/bash

# Fixes the intermittent touchscreen issue on my XPS 13 running Debian Jessie.
# Script stored in /opt/touchscreen-fix

/sbin/modprobe -r hid_multitouch && /sbin/modprobe hid_multitouch
