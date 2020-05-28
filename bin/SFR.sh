#!/bin/sh
#SFR.sh combine the utilities into a parents script

usage(){
	echo "Usage: $(basename "$0") [-h|-l [-v]|-t [-on|-off]|-g]
  -h help
  -l list connected devices
  -t toggle MAC filtering
  -f filter MAC filtering (when you forget the flag is -t)
  -on turn filtering on
  -off turn filtering off
  -g get html page
"
	exit 1
}

[ "$1" ]|| usage

if echo "$*"|grep -q '\-h'; then usage;
elif echo "$*"|grep -q '\-t'    || \
echo "$*"|grep -q '\-f'         || \
echo "$*"|grep -q '\-on'        || \
echo "$*"|grep -q '\-off'       || \
echo "$*"|grep -q 'del'         || \
echo "$*"|grep -q '\-d'         || \
echo "$*"|grep -q 'add'         || \
echo "$*"|grep -q '\-a' 
then
  if echo "$*"|grep -q '\-on'; then
    SFR_toggle_MAC_filtering.py -on
  elif echo "$*"|grep -q '\-off'; then
    SFR_toggle_MAC_filtering.py -off
  elif echo "$*"|grep -q 'on'; then
    SFR_toggle_MAC_filtering.py -on
  elif echo "$*"|grep -q 'off'; then
    SFR_toggle_MAC_filtering.py -off
  elif [ "$2" ] && ( echo "$1"|grep -q '-a' || echo "$1"|grep -q 'add' ); then
    SFR_toggle_MAC_filtering.py -add $2
  elif [ "$2" ] && ( echo "$1"|grep -q '-d' || echo "$1"|grep -q 'del' ); then
    SFR_toggle_MAC_filtering.py -del $2
  else
    SFR_toggle_MAC_filtering.py 
  fi
elif echo "$*"|grep -q '\-g'; then
  echo "This hasn't been finished - its meant to understand which page from the router is wanted and get it."
  SFR_html_get.py $*
elif echo "$*"|tr ' ' '\n'|grep -v '^\-l' && echo "$*"|grep -q '\-'; then
  SFR_list_connected.sh $* || SFR_list_connected.sh --force_update
elif echo "$*"|grep -q '\-l'; then 
  SFR_list_connected.sh
fi

# grab http://192.168.1.1/state/lan for graph
# http://192.168.1.1/state/lan/extra

