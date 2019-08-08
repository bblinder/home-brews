#!/usr/bin/env bash

# based on dig-dug
# A mass domain dig to csv tool.

# Usage: ./dig-dug.sh domains
# The 'domains' file should contain one domain per line

# By default, the script uses a 300ms delay.
# Sleep is not necessary, but always a nice option.

sleep=0.2

# Saving this for a later iteration.
<<EOF
TLD_list='/tmp/TLD_list.txt'

remove_akamai_domains(){
	grep -Eiv "akamaihd|edgesuite|edgekey"
}

strip_subdomains(){
  awk -F\. '{print $(NF-1) FS $NF}'
}

cat "$1" | strip_subdomains | remove_akamai_domains > "$TLD_list"
EOF

if [[ -z "$1" ]] || [[ -z "$2" ]]
then
    echo "No input files found."
    exit 1
fi

# Don't read lines with 'for'. Use a 'while' loop and 'read'.
while IFS= read -r domain
do
  sleep "$sleep"
  echo "$domain"

  # Using +short to avoid auxiliary information.
  ipaddress=$(dig $domain +short)
  nameserver=$(dig ns $domain +short)

  # Using 'tr' to replace new lines with commas, and strip horizontal whitespace.
  # Now with commas as delimiters, software can convert results to spreadsheet.
  #cname_space=$(echo -e "$cname" | tr '\n' ',' | tr -d "[:blank:]")
  nameserver_space=$(echo -e "$nameserver" | tr '\n' ',' | tr -d "[:blank:]")

  # Outputting to the filename of choice for "$2"
  echo -e "$domain,$nameserver_space" >> "$2"
done < "$1"
