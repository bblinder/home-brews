#!/usr/bin/env bash

###########
## WARNING:
## Depending on the size of the log file, this script is extremely
## process-intensive and time-consuming.
## Proceed with caution.
###########

set -euo pipefail
shopt -s nullglob

RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' #no color

set -- *-origintest-* # Change this line depending on the naming convention of the log files.
if [[ ! "$#" -gt 0 ]] ; then
  echo "No logs found. Please ensure they're present in this directory."
else
  echo -e "${YELLOW}Parsing logs..." ; sleep 1
  echo -e "Standby...${NC}\r\n" ; sleep 1
  
  for file in *-origintest-* ; do
    echo -e "${RED}File:${NC} $file" # file name
    echo -e "${RED}Total Requests:${NC} $(grep -c nginx "$file")" # Total Requests

    # MEASURES CACHE-MISSES AT THE EDGE
    echo -e "${RED}Edge Miss:${NC} $(awk -v RS='' '/X-Cache:/ || /X-Cache-Remote/' \
    "$file" | grep -v "X-Cache:" | grep -c "X-Cache-Remote: TCP_HIT")"

    # MEASURES CACHES-MISSES AT THE PARENT (CHECKS FOR TCP_MISS IN BOTH X-CACHE
    # AND X-CACHE-REMOTE HEADERS)
    echo -e "${RED}Parent Miss:${NC} $(awk -v RS='' '/TCP_MISS/' \
    "$file" | grep -v TCP_HIT | grep -c nginx) (requests to origin)\r\n"
  done
  echo -e "${YELLOW}Done!${NC} "
fi
