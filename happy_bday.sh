#!/usr/bin/env sh

# adapted from a coworker's script

awk -v s="$(/bin/sh -c 'echo $$')" 'BEGIN{
  srand(s);X="\xF0\x9F";C=X "\x8E\x82";F=X "\xA7\xA8";R=X "\x8E\x86";B=X "\x8E\x87"
  for(;;) {
    n = int(rand() * 100) % 50 + 10
    for(i=4; i<n; i++) {
      printf "\r\033[K" "%s  %" i "s", C, F
      "sleep 0.05"|getline; close("sleep 0.05")
    }
    printf "\r\033[K" "%s  %" n "s", C, R
    "sleep 0.3"|getline; close("sleep 0.3")
    printf "\r\033[K" "%s  %" n "s", C, B R B
    "sleep 1"|getline; close("sleep 1")
  }
}'
