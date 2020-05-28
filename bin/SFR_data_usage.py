#!/usr/bin/env python3
#SFR_data_usage.py ver.  20181128135355 Copyright 2018 alexx, MIT Licence
#report how much data is being used by a connected device
#rdfa:deps="['sudo pip3 install ConfigParser']"
import os,sys,requests,configparser
from subprocess import Popen, PIPE

"""
  Defaults to wifi connected devices, but can report
   WAN: http://192.168.1.1/state/wan/extra
   LAN: http://192.168.1.1/state/lan
      Port => [Bytes sent, Bytes received, Collisions, FCS errors]
      MAC address => [IP address, Connection uptime, Packets sent, Unicast packets sent, Multicast packets sent,    
   
   data is stored in [DB: sqlite|Riak|MongoDB|Memcached|CouchDB|Cassandra|...]
   # ? https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.DownloadingAndRunning.html
   graphed using rrdtool
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

ip  = '192.168.1.1'
ip_url  = '192.168.1.1'
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
config.read_file(open(WICD_WIFI_CONF))
#config.readfp(open('/etc/wicd/wireless-settings.conf'))
#config.read(['site.cfg', os.path.expanduser('~/.myapp.cfg')])
#print(config.get(str(ip_gw_MAC), 'key'))
for s in config.sections():
   if s.startswith(MAC_MATCH) and password == '':
    password = config.get(s, 'key')

#print("INFO: located password guess: {}".format(password))
#sys.exit(1)

#This URL will be the URL that your login form points to with the "action" tag.
URI_PATH = '/state/lan'
POSTLOGINURL = 'http://' + ip_url + '/login?page_ref=' + URI_PATH

#This URL is the page you actually want to pull down with requests.
REQUESTURL = 'http://' + ip_url + URI_PATH

payload = {'login': username, 'password': password }
toggle_on = {'mac_filtering': 'on' }
toggle_off= {'mac_filtering': 'off','show_add_my_workstation': ''}

"""
wget http://192.168.1.1/state/lan | \
html2xpath table wlanhost_stats | \
grep $MAC
"""


with requests.Session() as session:
  try:
    post = session.post(POSTLOGINURL, data=payload)
  except Exception as err:
    pass
  r = session.get(REQUESTURL)
  if len(sys.argv) == 2 and sys.argv[1] == '-h':
    print("Usage: SFR_data_usage.py [-h|-port|<MAC_address>]\n\t defaults to /state/wan/extra |grep [SF:   (30577366) 518974; RS: (3118891344) 3351998]")
  elif len(sys.argv) == 2 and sys.argv[1] == '-d':
    print("Here is a dump of that page")
    print(r.text)
  elif len(sys.argv) == 3 and sys.argv[1] == '-port':
    print("Going to get the stats for port \"Port [Fibre|LAN [1..4]]\" {}".format(sys.argv[1]))
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(r.text, 'html.parser')
    port_find = soup.findAll("table", {"class": "pcports_stats"})
    for table in port_find:
        for row in table.findAll("tr"):
            for col in row.findAll("td"):
                print(col.getText())

    #toggle = session.post(REQUESTURL, data=toggle_on)
  elif len(sys.argv) == 2:
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(r.text, 'html.parser')
    mac_find = soup.findAll("table", {"class": "wlanhost_stats"})
    #  try:
    #    rows = soup.find('table', id="mac_address_list").find_all('input')
    #    print("rows: {}".format(rows))
    #  except:
    #    print("2nd request")
    #    r = session.get(REQUESTURL)

    try: #python3
        import urllib.parse as ul
    except ImportError: #python2
        import urllib as ul

    for table in mac_find:
        # unquote_plus(string, encoding='utf-8', errors='replace')
        try:
            print(ul.unquote_plus(str(table.findAll("tr")[0].findAll("td")[0])), encoding='utf-8', errors='replace')
        except Exception as e:
            print("MAC: [{}]".format(table.findAll("tr")[0].findAll("td")[0].text.strip()))
        if not sys.argv[1] == table.findAll("tr")[0].findAll("td")[0].text.strip(): continue
        print("IPv4: [{}]".format(table.findAll("tr")[1].findAll("td")[0].text.strip()))
        print("Uptime: [{}]".format(table.findAll("tr")[4].findAll("td")[0].text.strip()))
        print("Packets sent: [{}]".format(table.findAll("tr")[6].findAll("td")[0].text.strip()))
        print("Packets sent failures: [{}]".format(table.findAll("tr")[7].findAll("td")[0].text.strip()))
        print("Unicast packets sent: [{}]".format(table.findAll("tr")[8].findAll("td")[0].text.strip()))
        print("Multicast packets sent: [{}]".format(table.findAll("tr")[9].findAll("td")[0].text.strip()))
        print("Multicast packets sent: [{}]".format(table.findAll("tr")[9].findAll("td")[0].text.strip()))
        #for row in table.findAll("tr"):
        #    for col in row.findAll("td"):
        #        pass#print(col.getText())

    #for row in soup.find('table', id="mac_address_list").find_all('input'):
    #  #print(row.get('value'))
    #  if row.get('name') == 'mac_address' and row.get('value') != '':
    #    print(row.get('value'))
    #print("a4:e9:75:82:df:87   192.168.1.70 (iPad) should not be on the list")
  else:
    EXTRA_URL = 'http://' + ip_url + '/state/wan/extra'
    #post = session.post(POSTLOGINURL, data=payload)
    r = session.get(EXTRA_URL)
    from bs4 import BeautifulSoup
    import re
    #print(r.text)
    #sys.exit(0)
    soup = BeautifulSoup(r.text, 'html.parser')
    netstats_find = soup.findAll("div", {"class": "content"})
    #test_string = str(r.text) # is this faster?
    test_string = str(netstats_find)
    sf_pattern = 'SF:\s*(?P<sent>\d*)'
    rs_pattern = 'RS:\s*(\d+)\s*\d*'

    #result = re.compile(pattern, re.IGNORECASE).search(r.text)
    sf = re.compile(sf_pattern).search(r.text)
    rs = re.compile(rs_pattern).search(r.text)
    print("Trying for {}".format(EXTRA_URL))
    if sf or rs:
        print(sf)
        #print(result, result[match)
        try:
           print('[Sent]: {}'.format(sf.group('sent')))
           print('[Rcvd]: {}'.format(rs.group(1)))
        except Exception as e:
           print('unable to print SF/RF: {}'.format(e))
    else:
        print(r.text)

   #print("Usage: SFR_data_usage.py [-h|-port|<MAC_address>]\n\t defaults to /state/wan/extra |grep [SF:   (30577366) 518974; RS: (3118891344) 3351998]")

"""__END__"""

"""
   test_string = str(sys.argv[1])
   pattern = '(go(o)+d (?P<timeframe>(morning|day)))'
   result = re.compile(pattern, re.IGNORECASE).search(test_string)
   if result:
       print(result)
       #print(result, result[match)
       try:
          print('and a very good {} to you, as well'.format(result.group('timeframe')))

"""
