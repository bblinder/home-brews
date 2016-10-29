#!/bin/bash

# Temporarily disables IPv6. Used with my OpenVPN config on Debian 8.

sudo sysctl -w net.ipv6.conf.all.disable_ipv6=1 ; sudo sysctl -w net.ipv6.conf.default.disable_ipv6=1 ; sudo sysctl -w net.ipv6.conf.lo.disable_ipv6=1
