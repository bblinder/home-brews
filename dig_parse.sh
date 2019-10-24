#!/usr/bin/env bash

# based on dig-dug
# A mass domain dig to csv tool.

# Usage: ./dig-dug.sh domains
# The 'domains' file should contain one domain per line

# By default, the script uses a 300ms delay.
# Sleep is not necessary, but always a nice option.

if [[ -z "$1" ]] || [[ -z "$2" ]]
then
    echo "No input files found."
    exit 1
fi


# Don't read lines with 'for'. Use a 'while' loop and 'read'.
while IFS= read -r domain
do
  #sleep "$sleep"
  echo -e "$domain"

  # Using +short to avoid auxiliary information.
  ipaddress="$(dig $domain +short)"
  # stripping subdomains and getting NS info
  TLD_domain="$(echo -e $domain | awk -F\. '{print $(NF-1) FS $NF}')"
  nameserver="$(dig ns $TLD_domain +short)"

  # Using 'tr' to replace new lines with commas, and strip horizontal whitespace.
  # Now with commas as delimiters, software can convert results to spreadsheet.
  #cname_space=$(echo -e "$cname" | tr '\n' ',' | tr -d "[:blank:]")
  nameserver_space="$(echo -e $nameserver | tr '\n' ',' | tr -d "[:blank:]")"

  # Outputting to the filename of choice for "$2"
  echo -e $domain,$nameserver_space >> "$2"
done < "$1"