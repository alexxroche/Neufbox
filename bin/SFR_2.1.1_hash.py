#!/usr/bin/env python3
#rdfa.deps="[python3]"
import os,sys,hmac
from hashlib import sha256

username="admin"
TOKEN = "43f6168e635b9a90774cc4d3212d5703c11c9302"

def SFR_hash(*args):
  msg = args[0].rstrip("\n")
  bmsg = bytes(msg,'utf8')
  key = args[1].rstrip("\n")
  bkey = bytes(key,'utf8')
  hashed_key = bytes(sha256(bkey).hexdigest(), 'ascii')
  return hmac.new(bmsg, msg=hashed_key, digestmod=sha256).digest().hex()

def SFR_token():
  HASH = SFR_hash(TOKEN, username)
  print("Outdated API auth hash: " + HASH)

if __name__ == '__main__':
  SFR_token()
