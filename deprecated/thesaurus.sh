#!/usr/bin/env bash

set -Eeuo pipefail

if [ $# -eq 0 ]; then
  echo "Usage: $0 <word>"
  exit 1
fi

WORD="$1"
URL="https://www.thesaurus.com/browse/$WORD"

# Check for required tools
for cmd in curl grep sed; do
  if ! command -v "$cmd" &> /dev/null; then
    echo "Error: $cmd is not installed. Please install it."
    exit 1
  fi
done

# Fetch the page
HTML=$(curl -s "$URL")

echo "Synonyms for: $WORD"
echo "================="

# Extract synonyms using the class names we found in the HTML
echo "$HTML" |
  grep -o '<a href="http://www.thesaurus.com:80/browse/[^"]*" class="Bf5RRqL5MiAp4gB8wAZa">[^<]*</a>' |
  sed 's/<a href="http:\/\/www.thesaurus.com:80\/browse\/\([^"]*\)" class="Bf5RRqL5MiAp4gB8wAZa">\([^<]*\)<\/a>/\2/' |
  sort | uniq

echo ""
echo "Weak Synonyms:"
echo "$HTML" |
  grep -o '<a href="http://www.thesaurus.com:80/browse/[^"]*" class="u7owlPWJz16NbHjXogfX">[^<]*</a>' |
  sed 's/<a href="http:\/\/www.thesaurus.com:80\/browse\/\([^"]*\)" class="u7owlPWJz16NbHjXogfX">\([^<]*\)<\/a>/\2/' |
  sort | uniq
