#!/usr/bin/env bash

# makes an arbitrary number of requests (based on file match)
# to test sampling logic in Akamai config

set -euo pipefail
shopt -s nullglob

# Requires httpie
if [[ ! "$(command -v http)" ]]; then
	echo -e "::: httpie not installed."
	echo -e "::: Install via 'pip install httpie' or 'brew install httpie'"
	exit 1
fi

URL='' # Testing URL/Domain. Insert before flight.
Log='/tmp/Sampling_Log.txt'

ORIGINAL='' #insert before flight
NEXT=''     #insert before flight.

if [[ -e "$Log" ]]; then
	rm "$Log"
fi

# Now onto the actual work

if [[ ! ( -n "$URL" || -n "$ORIGINAL" || -n "$NEXT") ]] ; then
	echo "::: [URL], [ORIGINAL], or [NEXT] fields cannot be left blank"
	exit 1
fi

read -rp "::: How many iterations? --> " iter_response
if [[ ! -n "$iter_response" ]]; then
	echo "::: Input can't be blank. Try again."
	exit 1
fi

echo -e "\\nTesting '$iter_response' iterations..\\n\\nStandby..."
sleep 1.5
for ((i=1; i<$iter_response; i++)); do
	http "$URL" "Pragma:akamai-x-cache-on, \
	akamai-x-get-cache-key, akamai-x-check-cacheable, akamai-x-get-true-cache-key, \
    akamai-x-get-request-id, akamai-x-cache-remote-on" --headers
done | tee -a "$Log"

total="$iter_response"
original_hits=$(grep -i $ORIGINAL $Log | wc -l | awk '{$1=$1};1')
next_hits=$(grep -i $NEXT $Log | wc -l | awk '{$1=$1};1')
percent=$(awk "BEGIN { pc=100*${next_hits}/${total}; i=int(pc); print (pc-i<0.5)?i:i+1 }")

print_result() {
	echo -e "::: Log located at $Log\\n\\n"
	echo -e "(Original)\\n'$ORIGINAL'\\nHits: $original_hits\\n"
	echo -e "(Next)\\n'$NEXT'\\nHits: $next_hits\\n"
	echo -e "Total requests: $total"
	echo -e "Sampled requests: $percent%"
}

print_result | tee -a "$Log"
