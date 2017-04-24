#!/bin/bash

if [[ -e /usr/bin/openssl || -e /usr/local/bin/openssl ]] ; then
	if test "$1" ; then
		openssl s_client -connect "$1":443 | openssl x509 -text -noout
	else
		echo "Usage: $0 your-webite"
		exit 1
	fi
fi

