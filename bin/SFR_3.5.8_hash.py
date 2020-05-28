#!/usr/bin/env python3
#rdfa.deps="[python3]"
import os,sys,hmac
from hashlib import sha256

passwd="pass"
username="admin"

def SFR_hash(*args):
  msg = args[0].rstrip("\n")
  bmsg = bytes(msg,'utf8')
  key = args[1].rstrip("\n")
  bkey = bytes(key,'utf8')
  hashed_key = bytes(sha256(bkey).hexdigest(), 'ascii')
  return hmac.new(bmsg, msg=hashed_key, digestmod=sha256).digest().hex()

def SFR_token(*args):
  TOKEN = '9bddb258f0e606ff19b58d0236d0c9'
  if len(args[0]) >= 1:
    TOKEN = args[0][0]
  HASH = SFR_hash(TOKEN, username) + SFR_hash(TOKEN, passwd)
  print(f'{TOKEN} {username} {passwd} => {HASH}')

if __name__ == '__main__':
  sys.exit(SFR_token(sys.argv[1:]))

