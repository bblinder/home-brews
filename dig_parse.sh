#!/usr/bin/env bash

# based on dig-dug
# A mass domain dig to csv tool.

# Usage: ./dig-parse.sh domain_file output_file
# If reading from a list, the 'domains' file should contain one domain per line

# By default, the script uses a 300ms delay.
# Sleep is not necessary, but always a nice option.

set -uo pipefail # bash strict mode
IFS=$'\n\t'

if [[ -z "$1" ]] || [[ -z "$2" ]] ; then
    echo "Usage: ./dig-parse.sh domain_file output_file"
    exit 1
fi

sleep=0.1
master_dig='/tmp/dig_domain.txt'
ns_dig='/tmp/ns_dig.txt'

# Don't read lines with 'for'. Use a 'while' loop and 'read'.
while IFS= read -r domain
do
  sleep "$sleep"
  echo -e "$domain"
  
  # Creating our cached dig output. Using +short to avoid auxiliary information.
  dig "$domain" +short > /tmp/dig_domain.txt

  cname="$(cat $master_dig | awk 'NR==1{print $1}')"
  ipaddress="$(cat $master_dig | awk '{match($0,/[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+/); ip = substr($0,RSTART,RLENGTH); print ip}' | sed '/^$/d' | awk 'NR==1{print $1}')"
  
  # stripping subdomains and getting nameserver data
  TLD_domain="$(echo -e $domain | sed "s/^[^.]*\.//")"
  nameserver="$(dig ns "$TLD_domain" +short | awk 'NR==1{print $1}')"

  # Assumes you've got a shodan API key living at ~/.shodan/api_key
  #provider=$(shodan host $ipaddress | grep "Organization:" | sed "s/.*Organization: *//")
  provider="$(whois $ipaddress | grep "OrgName:" | sed "s/.*OrgName: *//" | tr -d ',')"
  # Using 'tr' to replace new lines with commas, and strip horizontal whitespace.
  # Now with commas as delimiters, software can convert results to spreadsheet.
  #cname_space=$(echo -e "$cname" | tr '\n' ',' | tr -d "[:blank:]")
  nameserver_space="$(echo -e "$nameserver" | tr '\n' ' ' | tr -d "[:blank:]")"
  ipaddr_space="$(echo -e "$ipaddress" | tr '\n' ',' | tr -d "[:blank:]")"
  
  # Outputting to the filename of choice for "$2" (ideally a csv)
  echo -e "$provider,$domain,$nameserver_space,$cname,$ipaddr_space" >> "$2"
done < "$1"
