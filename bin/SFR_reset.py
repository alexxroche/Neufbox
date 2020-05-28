#!/usr/bin/env python3
#rdfa.deps="[python3]"
import os,sys,ssl,requests,hmac
from hashlib import sha256
from bs4 import BeautifulSoup as bs

cpe_ip = '192.168.1.1' #until we move to [ipv6]
username="admin"

def SFR_hash(*args):
  msg = args[0].rstrip("\n")
  bmsg = bytes(msg,'utf8')
  key = args[1].rstrip("\n")
  bkey = bytes(key,'utf8')
  hashed_key = bytes(sha256(bkey).hexdigest(), 'ascii')
  return hmac.new(bmsg, msg=hashed_key, digestmod=sha256).digest().hex()

def SFR_fetch_token():
  url_token = "http://" + cpe_ip + "/api/1.0/?method=auth.getToken"
  xml = requests.get(url_token).text
  #soup = bs(xml, 'html.parser')
  soup = bs(xml, 'lxml')
  TOKEN = soup.find('auth').attrs['token']
  return TOKEN

def SFR_token(*args):
  #print(f'{args}')
  a = args[0]
  passwd = a[0]
  global username, cpe_ip
  if len(a) == 2:
    username = a[1]
  if len(a) == 3:
    cpe_ip = a[2]
  TOKEN = SFR_fetch_token()
  if not TOKEN:
    print("[err] failed to receive a token: " + TOKEN)
    print("[info] try: curl -s -G http://" + cpe_ip + "/api/1.0/?method=auth.getToken")
    sys.exit(1)
  
  HASH = SFR_hash(TOKEN, username) + SFR_hash(TOKEN, passwd)
  if not HASH:
    print("[e] need some crypto" + HASH)
    sys.exit(7)
  #else: print(f"[i] t: {TOKEN}\n h: {HASH}]")
  url_check="http://" + cpe_ip + "/api/1.0/?method=auth.checkToken&token=" + TOKEN + "&hash=" + HASH
  checkToken = requests.get(url_check).text
  if not "auth" in checkToken:
      print("[WARN] failed to check token " + url_check)
      print("[w] " + checkToken)
      print("[info] its possible that the CPE has locked us out with a cooldown $checkToken")
      sys.exit(2)
  else:
      print("Authed: " + TOKEN)

if __name__ == '__main__':
  if len(sys.argv) >= 2:
    SFR_token(sys.argv[1:])
  else:
    print('Usage: SFR_reset.py <passphrase> [username] [router IP address] # the one used to log into the router')
