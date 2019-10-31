#!/usr/bin/env bash

IFS=$'\n\t'

if [[ -z "$1" ]] ; then
  echo "No input found"
  exit 1
fi

urlencode() {
    # urlencode <string>
    old_lc_collate=$LC_COLLATE
    LC_COLLATE=C

    local length="${#1}"
    for (( i = 0; i < length; i++ )); do
        local c="${1:i:1}"
        case $c in
            [a-zA-Z0-9.~_-]) printf "$c" ;;
            *) printf '%%%02X' "'$c" ;;
        esac
    done

    LC_COLLATE=$old_lc_collate
}

urldecode() {
    # urldecode <string>

    local url_encoded="${1//+/ }"
    printf '%b' "${url_encoded//%/\\x}"
}

read -rp "Encode (1) or Decode (2) URL? --> " URL_CHOICE
case "$URL_CHOICE" in
  1)
    urlencode $1
    ;;
  2)
    urldecode $1
    ;;

  *)
    echo -e "No choice selected"
    exit 0
    ;;
esac
