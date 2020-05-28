#!/bin/sh
#rdfa.deps="[sh curl openssl|hmac256]"

usage(){
        echo "Usage: $(basename $0) <passphrase>"
        exit 1
}

[ "$1" ]|| usage
passwd="$1"
username="admin"

SFR_hash() {
  data="$(echo "$1"|tr -d '\n')"
  key="$(echo "$2"|tr -d '\n'|openssl dgst -sha256|cut -d' ' -f2)"
  echo "$key"|tr -d '\n'|openssl dgst -sha256 -hmac "$data"|cut -d" " -f2
}

TOKEN="$(curl -s -G http://192.168.1.1/api/1.0/?method=auth.getToken|grep token|cut -d'"' -f2)"
HASH="$(SFR_hash "$TOKEN" "$username"|tr -d '\n';SFR_hash "$TOKEN" "$passwd")"
checkToken="$(curl -s http://192.168.1.1/api/1.0/?method=auth.checkToken\&token=$TOKEN\&hash=$HASH)"
if [ ! "$(echo "cT $checkToken"|grep auth)" ];then
	echo "[WARN] failed to check token $TOKEN with hash: $HASH"
fi

#curl -s http://192.168.1.1/api/1.0/?method=lan.getHostsList\&token=$TOKEN|grep host|awk -F'"' '{print $8 ", " $6 ", " $10 ",  " $16 ", " $4}'
curl -s http://192.168.1.1/api/1.0/?method=lan.getHostsList|grep host|awk -F'"' '{print $8 ", " $6 ", " $10 ",  " $16 ", " $4}'
