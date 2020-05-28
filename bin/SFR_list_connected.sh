#!/bin/sh
#SFR_list_connected.sh ver 20181008174711 Copyright 2018 $(whoami), MIT Licence
#rdfa:deps="[sh wget python3 echo stat awk sed tr grep html2xpath html2txt]"
TMP_INDEX=/tmp/192168001001

expand_ipv6(){
 for i in $(echo "$*"|sed 's/:/\n:\n/g'); do 
	if echo "$i"|grep -q ':'; then 
		echo ''|tr -d '\n'; 
	else 
	  if echo $i|grep -qP '^[a-fA-F0-9]{1,3}$'; then
		while [ $(echo $i|wc -c) -lt 5 ];do 
			i="0$i";
		done
	  fi
	fi 
	echo "$i"|tr -d '\n' ; 
 done
}

crude_list(){
wget -q http://192.168.1.1/ -O $TMP_INDEX
DEVICES="$(echo "$(for i in `seq 21 2 30`; do html2xpath $TMP_INDEX table tr td $i; done)"|grep -v 'class='|grep .|sed 's/<.\{2,3\}> *//g')"

for d in "$DEVICES"; do
 if [ "$d" ]; then
	IP=$(ping -c1 -w2 -W1 "$d")
	IP_ADDR=$(echo $IP|sed 's/.*(//;s/).*//')
	#echo "$d $(echo $IP|sed 's/.*(//;s/).*//')"
	IP_FOUND=$(echo $IP_ADDR|grep -q '192.168' && echo 1)
	if [ "$IP_FOUND" ]&&[ "$IP_FOUDN" -eq 1 ]; then
		echo "$d $(echo $IP|sed 's/.*(//;s/).*//')"
	else
		echo "$d [IP missing]"
	fi
 fi
done
rm $TMP_INDEX || \
wget -q http://admin:admin@192.168.1.1/wifi -O /tmp/box_wifi.html
}

timefudge(){
  THEN='20000101'
  if [ -e "$1" ]; then
      touch -mt ${THEN}0000 $1 2>/dev/null 1>/dev/null
      dt_now=$(date +'%Y%m%d %H:%M:%S')
      sudo date --set="$THEN" 2>/dev/null 1>/dev/null
      touch -at ${THEN}0000 $1 2>/dev/null 1>/dev/null
      sudo date --set="$dt_now" 2>/dev/null 1>/dev/null
  fi
}

if [ ! -f "/tmp/box_wifi.html" ]; then
   touch "/tmp/box_wifi.html" || echo $(crude_list)
   timefudge "/tmp/box_wifi.html"
fi

if [ -f "/tmp/box_wifi.html" ]; then
 if [ "$1" ]||[ "$(echo $(( $(date +%s) - $(stat -c%Z /tmp/box_wifi.html) )))" -gt 300 ]; then
	#echo "\033[0;31mLIES!\033[0m this is $(echo $(( $(date +%s) - $(stat -c%Z /tmp/box_wifi.html) ))) seconds out of date" >&2
	echo "\033[0;31m Updating list!\033[0;34m as the last one was $(echo $(( $(date +%s) - $(stat -c%Z /tmp/box_wifi.html) ))) seconds old \033[0m" >&2
	#echo "\033[1;34mUpdating list!\033[0m as the last one was $(echo $(( $(date +%s) - $(stat -c%Z /tmp/box_wifi.html) ))) seconds old" >&2
	~/bin/SFR_html_get.py > /tmp/box_wifi.html
 fi
	#html2xpath /tmp/box_wifi.html table id="wifi_assoc"|html2xpath tr td
	echo "$(
	html2xpath /tmp/box_wifi.html table id="wifi_assoc"| \
	~/bin/html2xpath tr td| \
	html2txt -| \
	awk 'FNR%2'| \
	sed 's/^\(.\)$/NEW_LINE \1/'| \
	tr '\n' '\t'| \
	sed 's/NEW_LINE/\n/g'| \
	grep .| \
	awk '{print $1 " \033[1;34m" $2 "\033[0;33m " $4 " \033[0;31m" $5 "\033[0;36m " $3 "\033[0m"}'
	#awk '{print $1 " \033[0;34m" $2 "\033[0;33m " $4 " \033[0;31m" $5 "\033[0;36m " $3 "\033[0m"}'
	)"|while read r;do

			echo "$(echo "$r"|tr ' ' '\n'|while read b;do
				# looks like IPv6 and is NOT a MAC address
				if echo $b|grep -qP '[a-fA-F0-9]{1,3}:' && echo $b|grep -qvP '([a-f0-9]{2}:){5}[a-f0-9]{2}'; then
					#echo $(~/bin/expand_ipv6.sh "$b")
					echo $(expand_ipv6 "$b")
				else
					echo $b
				fi
			done)"| column -tx|tr '\n' ' '
			#echo "$r"|column -tx|tr '\n' '\t'
			if [ "$2" ]&& echo "$2"|grep -vq '\-v'; then echo "$r"|wc -c|tr -d '\n' ; fi
			if [ $(echo "$r"|wc -c) -lt 111 ]; then
				echo "\t\t\t  "|tr -d '\n'
			elif [ $(echo "$r"|wc -c) -lt 128 ]; then
				echo "\t\t  "|tr -d '\n'
			fi
		# this should be from a list
		if echo "$r"|grep -q 'iDiot'; then
			echo "[iPad]"
		elif echo "$r"|grep -q 'android'; then
			echo "[phone]"
		elif echo "$r"|grep -iq 'jones' && echo "$r"|grep -q '7c:19:84:77:8c:b1'; then
			echo "\t[guest laptop]"
		else
			echo ""
		fi
	done
fi

