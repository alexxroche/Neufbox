#!/bin/sh
#rdfa.deps="[sh curl openssl|hmac256]"

usage(){
        echo "Usage: $(basename $0) <passphrase>"
        exit 1
}

[ "$1" ]|| usage
passwd="$1"
username="admin"
VERBOSE=0

SFR_hash() {
  data="$(echo "$1"|tr -d '\n')"
  key="$(echo "$2"|tr -d '\n'|openssl dgst -sha256|cut -d' ' -f2)"
  echo "$key"|tr -d '\n'|openssl dgst -sha256 -hmac "$data"|cut -d" " -f2
}

SFR_fetch_token(){
  TOKEN="$(curl -s -G http://192.168.1.1/api/1.0/?method=auth.getToken|grep token|cut -d'"' -f2)"
  echo "$TOKEN"
}
SFR_token(){
  TOKEN="$(SFR_fetch_token)"
  if [ ! "$TOKEN" ]; then
    echo "[err] failed to receive a token: $TOKEN"
    echo "[info] try: curl -s -G http://192.168.1.1/api/1.0/?method=auth.getToken"
    exit 1
  fi
  HASH="$(SFR_hash "$TOKEN" "$username"|tr -d '\n';SFR_hash "$TOKEN" "$passwd")"
  checkToken="$(curl -s http://192.168.1.1/api/1.0/?method=auth.checkToken\&token=$TOKEN\&hash=$HASH)"
  if [ ! "$(echo "cT $checkToken"|grep auth)" ];then
      echo "[WARN] failed to check token $TOKEN with hash: $HASH"
      echo "[info] its possible that the CPE has locked us out with a cooldown $checkToken"
      exit 1
  fi
}
PAYLOAD='{"login": "'$username'", "password": "'$passwd'"}'
DATA='login='$username'&password='$passwd
#DATA='login='$username'%26password='$passwd  # FAILS!
#echo "$PAYLOAD"; exit 0
CJAR="/tmp/.SFR_reset.cookies"
DEBUG_LOG="/tmp/SFR_DEBUG.log"
#curl --cookie-jar $CJAR -d "login=${username}%26password=${passwd}" --dump-header $DEBUG_LOG http://192.168.1.1/login?page_ref=/wifi/macfiltering
#curl --cookie-jar $CJAR -d $PAYLOAD http://192.168.1.1/login?page_ref=/wifi/macfiltering
LOGIN_STATE="$(
curl -L --cookie-jar $CJAR -s -o /dev/null -d "$DATA" -w "%{http_code}" 'http://192.168.1.1/login?page_ref=/wifi/macfiltering'; echo -n ' ' #WORKS
)"
if [ "$LOGIN_STATE" -ne 200 ]; then
  echo "[err] failed to login"
  exit 1
fi
#curl -L -c /tmp/.SFR_reset.cookies -s -o /dev/null -d "$DATA" -w "%{http_code}" http://192.168.1.1/login?page_ref=/wifi/macfiltering  #WORKS!
#curl -L -b $DEBUG_LOG http://http://192.168.1.1/wifi/macfiltering
##echo "$PAYLOAD"| curl --cookie-jar $CJAR --dump-header $DEBUG_LOG -d @- http://192.168.1.1/login?page_ref=/wifi/macfiltering # FAIL
#curl -s http://http://192.168.1.1/wifi/macfiltering?token=$TOKEN
#curl -L -s -o /dev/null --cookie-jar $CJAR -d $DATA -w "%{http_code}" http://192.168.1.1/wifi/macfiltering ; echo ' '|tr -d '\n' # WORKS!
READ_CHECK="$(
curl -Lso /dev/null -c $CJAR -d $DATA -w "%{http_code}" http://192.168.1.1/wifi/macfiltering ; echo ' '|tr -d '\n' # WORKS!
)"
if [ "$READ_CHECK" -ne 200 ]; then
  echo "[err] failed to reset"
  exit 1
else
  echo "[info] CPE reset success"
fi

echo "$VERBOSE"|grep -q "noise" && \
curl -Lsc $CJAR -d $DATA http://192.168.1.1/wifi/macfiltering

# this works!
# echo '{"text": "Hello **world**!"}' | curl -d @- https://api.github.com/markdown
# echo "$message" | curl -H "Content-Type: application/json" -d @- "$url" 

