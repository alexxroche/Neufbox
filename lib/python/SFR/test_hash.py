#!/usr/bin/env python3
#rdfa.deps="[python3]"
import os,sys,requests,configparser,hmac
from os.path import dirname
from subprocess import Popen, PIPE
sys.path.append(dirname(__file__))
cpe_ip = '192.168.1.1' #until we move to [ipv6]
from hashlib import sha256

def SFR_hash(*args):
  msg = args[0].rstrip("\n")
  bmsg = bytes("b'" + msg + "'",'utf8')
  key = args[1].rstrip("\n")
  bkey = bytes(key,'utf8')
  hashed_key = bytes("b'" +sha256(bkey).hexdigest()+ "'", 'ascii')
  return hmac.new(bmsg, msg=hashed_key, digestmod=sha256).digest().hex()

def openssl_hash(*args):
  if not len(args) == 2: return None
  data = bytes(args[0],'utf8')
  k = args[1]
  key_cmd =f"printf '{k}'|openssl dgst -sha256|cut -d' ' -f2" #works
  key= Popen(key_cmd, shell=True, stdout=PIPE).stdout.read()
  q = str(key.decode('utf8').rstrip("\n"))
  #cmd = 'echo "' + str(key) + '"|tr -d \'\n\'|openssl dgst -sha256 -hmac "' + str(data) + '"|cut -d" " -f2' #this works
  #print(Popen(cmd, shell=True, stdout=PIPE).stdout.read().decode("utf8").rstrip("\n"))  # with this 
  cmd = 'printf "b\'' + q + '\'"|openssl dgst -sha256 -hmac "' + str(data) + '"|cut -d" " -f2'
  return Popen(cmd, shell=True, stdout=PIPE).stdout.read().decode("utf8").rstrip("\n")

def main():
  TOKEN='OslDHrAw8e-ar9JhhR-oHkJ86-o9JCV7OZCN'
  username = 'admin'
  passwd = 'supersecret'
  secret = 'passphrase is better than passwords'
  print(f'SFR_HASH = openssl_hash({TOKEN}, {username}) + openssl_hash({TOKEN}, {passwd})') # DEBUG
  #hash_from_openssl = str(openssl_hash(TOKEN, username) + openssl_hash(TOKEN, passwd))
  hash_from_openssl = openssl_hash(TOKEN, username) + openssl_hash(TOKEN, passwd)
  #SFR_HASH = str(SFR_hash(TOKEN, username) + SFR_hash(TOKEN, passwd)) #.decode("utf8")
  SFR_HASH         =      SFR_hash(TOKEN, username) +     SFR_hash(TOKEN, passwd) #.decode("utf8")

  print(f"[i] openssl: {hash_from_openssl} ;\n [i] python: {SFR_HASH}")

if __name__ == '__main__':
    main()
