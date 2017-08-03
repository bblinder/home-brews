#!/bin/bash

set -euo pipefail

# Stolen and modifed from a reddit thread.

username="" # your reddit handle

showerthoughts=$(http 'https://www.reddit.com/r/showerthoughts/top.json?sort=top&t=week&limit=100' | \
python2.7 -c 'import sys, random, json; randnum = random.randint(0,99); response = json.load(sys.stdin)["data"]["children"][randnum]["data"]; print "\n\"" + response["title"] + "\""; print "    -" + response["author"] + "\n";')

echo $showerthoughts | cowsay | lolcat
