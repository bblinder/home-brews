#!/bin/bash

# Temporarily disables IPv6. Used with my OpenVPN config on Debian 8.

if [[ $(uname -s) != "Linux" ]] ; then
	echo "ERROR: This script will only run on Linux systems."
	exit 1
else
	sudo sysctl -w net.ipv6.conf.all.disable_ipv6=1 ; sudo sysctl -w net.ipv6.conf.default.disable_ipv6=1 ; sudo sysctl -w net.ipv6.conf.lo.disable_ipv6=1
fi


