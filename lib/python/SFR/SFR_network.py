#!/usr/bin/env python3
#SFR_toggle_MAC_filtering.py ver. 20180211174957 Copyright 2018 alexx, MIT Licence
#toggle SFR NB6-FXC-r2 MAC filtering
#rdfa:deps="['sudo pip3 install ConfigParser']"
import os,sys,requests,configparser
from subprocess import Popen, PIPE

"""
  You may have to set the router password here. 
  By deafult it is the same ass the wifi password,
  so this script tries to extract that from your wifi config
"""
password = ''

"""
  Nothing else should be needed
"""
username = 'admin'
WICD_WIFI_CONF = '/etc/wicd/wireless-settings.conf'

# should read this from wicd pass or $HOME/.config/SFR.conf ?

#https://gist.github.com/davejamesmiller/1965559
# self.escalate_via_sudo
if os.geteuid() != 0:
  os.execvp("sudo", ["sudo"] + sys.argv)

"""
Automatically locates IPv6 address of router, (though can still fall back to old IPv4).
and its MAC address
"""
gw_locate = 'ip route|grep default|head -n1|awk \'{print $3}\''
ip  = os.popen(gw_locate).read().rstrip()
ip_url  = ip
#ip6_gw_query = 'ip -6 r|head -n1|awk \'{print "[" $1}\'|sed \'s/\/.*/1]/\''
ip6_gw_query = 'ip -6 r|head -n1|awk \'{print $1}\'|sed \'s/\/.*/1/\''
ip4_gw_query = 'ip r|head -n1|awk \'{print $3}\''

ip6_gw = Popen(ip6_gw_query, shell=True, stdout=PIPE).stdout.read()
ip6_gw_ping = "ping6 -q -c1 -w1 {} 1>/dev/null 2>/dev/null && echo 0 || echo 1".format(ip6_gw.decode("utf-8").rstrip())
#print('{}'.format(ip6_gw_ping))
ip6_gw_ping = Popen(ip6_gw_ping, shell=True, stdout=PIPE).stdout.read()
#print('ping6 errors: {}'.format(ip6_gw_ping.decode("utf-8").rstrip()))

if len(ip6_gw) >= 3 and ip6_gw_ping.decode("utf-8").rstrip() != 1:
  ip_url = '[' + ip6_gw.decode("utf-8").rstrip() + ']'
  ip = ip6_gw.decode("utf-8").rstrip()
  #print('GW: {}'.format(ip_url))
else:
  if not ip6_gw_ping.decode("utf-8").rstrip() != 1:
    print('ERR: {}'.format(ip6_gw_ping.decode("utf-8").rstrip()))
  print('Using IPv4 gw: {} (maybe you should install nftables and enable IPv6?)'.format(ip))
ip_gw_MAC =  Popen('ip neigh|grep ' + ip + '|head -n1|awk \'{print $5}\'', shell=True, stdout=PIPE).stdout.read().decode("utf-8").rstrip()
MAC_MATCH = ip_gw_MAC.upper()[:-1]
#print('GW MAC: {}'.format(MAC_MATCH))

"""
sudo ini_grep //GW_MAC/key /etc/wicd/wireless-settings.conf
"""
config = configparser.ConfigParser()
config.readfp(open(WICD_WIFI_CONF))
#config.readfp(open('/etc/wicd/wireless-settings.conf'))
#config.read(['site.cfg', os.path.expanduser('~/.myapp.cfg')])
#print(config.get(str(ip_gw_MAC), 'key'))
for s in config.sections():
   if s.startswith(MAC_MATCH) and password == '':
    password = config.get(s, 'key')

#print("INFO: located password guess: {}".format(password))
#sys.exit(1)

#This URL will be the URL that your login form points to with the "action" tag.
LOGIN_URL = 'http://' + ip_url + '/login?page_ref=/state/lan'

#This URL is the page you actually want to pull down with requests.
REQUEST_URL = 'http://' + ip_url + '/state/lan'

payload = {'login': username, 'password': password }

with requests.Session() as session:
  post = session.post(LOGIN_URL, data=payload)
  r = session.get(REQUEST_URL)
  print(r.text)
  """
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(r.text, 'html.parser')
    mac_filtering_on = soup.find(id="mac_filtering_on")
    mac_filtering_off= soup.find(id="mac_filtering_off")
    # sometimes we don't get any data 201803
    if mac_filtering_on and mac_filtering_on.has_attr('checked'):
      print("MAC filtering is currently ON (Enabled) except for:")
    elif mac_filtering_off and mac_filtering_off.has_attr('checked'):
      print("NO MAC filtering at this time")
      #print("IS OFF: {} {}".format(mac_filtering_on, mac_filtering_off))
    else:
      print("ON :{}".format(mac_filtering_on))
      print("OFF:{}".format(mac_filtering_off))
      # We probably timed out on the request, lets try again
      #  File "SFR_toggle_MAC_filtering.py", line 136, in <module>
      #      for row in soup.find('table', id="mac_address_list").find_all('input'):
      #      AttributeError: 'NoneType' object has no attribute 'find_all'
      try:
        rows = soup.find('table', id="mac_address_list").find_all('input')
        print("rows: {}".format(rows))
      except:
        print("2nd request")
        r = session.get(REQUESTURL)

    for row in soup.find('table', id="mac_address_list").find_all('input'):
      #print(row.get('value'))
      if row.get('name') == 'mac_address' and row.get('value') != '':
        print(row.get('value'))
    print("a4:e9:75:82:df:87   192.168.1.70 (iPad) should not be on the list")
   """
