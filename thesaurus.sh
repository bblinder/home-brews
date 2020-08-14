#!/usr/bin/env bash

# Not my work, just keeping it here as a handy reference. Needs lynx and html2text to work.

BROWSER="/usr/local/bin/lynx -source"
WEBSITE="http://thesaurus.com/browse/$1"
HTML2TEXT="/usr/local/bin/html2text"

if test "$1"; then
	${BROWSER} ${WEBSITE} | ${HTML2TEXT} | ${PAGER}
else
	echo "Usage: $0 your-word"
	exit 1
fi

