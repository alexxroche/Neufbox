#!/usr/bin/env python3
import os,sys,requests,configparser
from os.path import dirname
from subprocess import Popen, PIPE
sys.path.append(dirname(__file__))
try:
	import SFR_config
except:
	from .SFR_config import *

def ip_url():

  # this tries to determin the MAC address of the CPE (which
  #  we use in fetch_pass() to search WICD_WIFI_CONF )
  gw_locate = 'ip route|grep default|head -n1|awk \'{print $3}\''
  ip  = os.popen(gw_locate).read().rstrip()
  ip_url  = ip
  ip6_gw_query = 'ip -6 r|head -n1|awk \'{print $1}\'|sed \'s/\/.*/1/\'|grep -v \'fe80::\''
  ip4_gw_query = 'ip r|head -n1|awk \'{print $3}\''
  ip6_gw = Popen(ip6_gw_query, shell=True, stdout=PIPE).stdout.read()
  ip6_gw_ping = "ping6 -q -c1 -w1 {} 1>/dev/null 2>/dev/null && echo 0 || echo 1".format(ip6_gw.decode("utf-8").rstrip())
  ip6_gw_ping = Popen(ip6_gw_ping, shell=True, stdout=PIPE).stdout.read()
  #print('ping6 errors: {}'.format(ip6_gw_ping.decode("utf-8").rstrip()))

  if len(ip6_gw) >= 3 and ip6_gw_ping.decode("utf-8").rstrip() != 1:
    ip_url = '[' + ip6_gw.decode("utf-8").rstrip() + ']'
    ip = ip6_gw.decode("utf-8").rstrip()
    #print('GW: {}'.format(ip_url))
  else:
    if not ip6_gw_ping.decode("utf-8").rstrip() != 1:
      print('ERR: {}'.format(ip6_gw_ping.decode("utf-8").rstrip()))
    #print('Using IPv4 gw: {} (maybe you should install nftables and enable IPv6?)'.format(ip)) # this should be a debug option and only if interacting with user on the command line
  return [ ip, ip_url ]

def ip_gw_MAC():
  ip = ip_url()[0]
  ip_gw_MAC =  Popen('ip neigh|grep ' + ip + '|head -n1|awk \'{print $5}\'', shell=True, stdout=PIPE).stdout.read().decode("utf-8").rstrip()
  #MAC_MATCH = ip_gw_MAC.upper()[:-1] #We strip the last char because [EX:AM:PL:AA:AA:01] was stored as [EX:AM:PL:AA:AA:04]
  return ip_gw_MAC.upper()[:-1] #why do we strip the last char?

  #print(MAC_MATCH); sys.exit(1)

def fetch_user():
  username = None
  try: # the default is to read it from ../SFR.cfg
    config = SFR_config.config
    if hasattr(config, 'get'):
      username = config.get('local','username').strip('"') #in case someone quotes the variable
  except: # otherwise we use the default
    username = 'admin'
  return username

def fetch_pass():
  password = None
  try: # the default is to read it from ../SFR.cfg
    config = SFR_config.config
    if hasattr(config, 'get'):
      password = config.get('local','password').strip('"') #in case someone quotes the variable

  except: # otherwise we try to collect it from the WICD config
    sudo = ''
    WICD_WIFI_CONF = '/etc/wicd/wireless-settings.conf'
    if os.geteuid() != 0:
      #  os.execvp("sudo", ["sudo"] + sys.argv)
      sudo = 'sudo'
    MAC_MATCH = ip_gw_MAC()
    WICD_config = configparser.ConfigParser()

    try:
      WICD_config.readfp(open(WICD_WIFI_CONF))
      for s in WICD_config.sections():
        if s.startswith(MAC_MATCH) and password == '':
          password = WICD_config.get(s, 'key')
          print("[info] found pass in WICD conf: {}".format(password))
           
    except: #very dirty hack
      e = str(sys.exc_info()[0])
      #print('[warn] there was an error: {} ;(so we are falling back to Popen('sudo ...')) '.format(e))
      #print('[info] trying sudo grep: {}'.format('sudo grep -A25 "\[' + MAC_MATCH + '" ' + WICD_WIFI_CONF + '|grep \'key =\'|cut -d= -f2'))
      pph_search = Popen('sudo grep -A25 "\[' + MAC_MATCH + '" ' + WICD_WIFI_CONF + '|grep \'key =\'|cut -d= -f2', shell=True, stdout=PIPE).stdout.read()
      password = pph_search.decode("utf-8").strip()

  if password:
    return password

if __name__ == '__main__':
    print(fetch_user()) #unittest
    print(fetch_pass()) #unittest
