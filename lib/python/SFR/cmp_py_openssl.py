#!/usr/bin/env python3
#rdfa.deps="[python3]"
import os,sys,requests,configparser,hmac
from os.path import dirname
from subprocess import Popen, PIPE
sys.path.append(dirname(__file__))
cpe_ip = '192.168.1.1' #until we move to [ipv6]
from hashlib import sha256

def SFR_bhash(*args):
  msg = args[0].rstrip("\n")
  bmsg = bytes("b'" + msg + "'",'utf8')
  key = args[1].rstrip("\n")
  bkey = bytes(key,'utf8')
  hashed_key = bytes("b'" +sha256(bkey).hexdigest()+ "'", 'ascii')
  return hmac.new(bmsg, msg=hashed_key, digestmod=sha256).digest().hex()

def SFR_hash(*args):
  msg = args[0].rstrip("\n")
  bmsg = bytes(msg,'utf8')
  key = args[1].rstrip("\n")
  bkey = bytes(key,'utf8')
  hashed_key = bytes(sha256(bkey).hexdigest(), 'ascii')
  return hmac.new(bmsg, msg=hashed_key, digestmod=sha256).digest().hex()


passwd="pass"
username="admin"
VERBOSE=0


print(SFR_bhash(passwd,username))
print(SFR_hash(passwd,username))

"""
SFR_hash() {
  data="$(echo "$1"|tr -d '\n')"
  key="$(echo "$2"|tr -d '\n'|openssl dgst -sha256|cut -d' ' -f2)"
  echo "$key"|tr -d '\n'|openssl dgst -sha256 -hmac "$data"|cut -d" " -f2
}
"""


