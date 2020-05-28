#!/bin/sh
passwd="pass"
username="admin"
VERBOSE=0


SFR_hash() {
  data="$(echo "$1"|tr -d '\n')"
  key="$(echo "$2"|tr -d '\n'|openssl dgst -sha256|cut -d' ' -f2)"
  echo "$key"|tr -d '\n'|openssl dgst -sha256 -hmac "$data"|cut -d" " -f2
}

echo "$(SFR_hash $passwd $username )"
echo "$(./cmp_py_openssl.py)"

