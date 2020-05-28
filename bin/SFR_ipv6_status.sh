#!/bin/sh
# 2019-11-07 SFR network is no longer asigning an IPv6 allocation to the router
# 2020-05-22 after 6 months, (after a power outage) IPv6 seems to be back?
SFR_html_get.py http://192.168.1.1/networkv6/wan|grep -A2 -E 'Statut|Servic'|sed 's/<.th>//;s/.*>//'|tr -d '\n'
echo ""
