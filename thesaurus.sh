#!/bin/bash

BROWSER="/usr/local/bin/lynx -source"
WEBSITE="http://thesaurus.reference.com/search?q=$1"
HTML2TEXT="/usr/local/bin/html2text -style compact"

if test "$1"; then
	${BROWSER} ${WEBSITE} | ${HTML2TEXT} | ${PAGER}
else
	echo -n "Usage: $0 word"
	exit 1
fi

