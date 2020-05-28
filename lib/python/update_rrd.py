#!/usr/bin/env python3

#import os,sys
#import SFR
#import SFR.SFR_functions
from SFR.SFR_functions import *
from SFR.SFR_RRD import *
from SFR.SFR_pass import ip_url

tmp_dir=''
script_name = os.path.basename(sys.argv[0])

# should use mktemp
#tmp_dir=$(mktemp -t $(basename $0).XXXXXX) ||
#            { log "unable to create tempfile"; exit 2; }
tmp_dir='/tmp/'+script_name+'/'
if not os.path.exists(tmp_dir):
    os.makedirs("{}".format(tmp_dir))

conf_file='SFR.cfg'
#CFG = os.getcwd()+conf_file
#config = SFR.SFR_functions.get_cfg()
config = get_cfg(conf_file)

"""
getopt (no point in create dependencies for this)
 N.B. flags can override config, (which is why it comes after get_cfg() )
"""
opt = {}
#opt['d'] = 0

if len(sys.argv) > 1:
  for flag in sys.argv:
    if is_digit(flag):
        dgc = int(flag)
        days_ago = dgc # days ago candidate
    elif flag == '-uf':
        unfiltered = 1
    elif flag == '-h':
        opt["usage"]=1
    elif flag == '-v':
        opt["d"]=1
    elif flag == '-K':
        opt["dump_conf"]=1

if opt_set('usage'): usage()
if opt_set('dump_conf'): dump_conf()

#curl -s http://192.168.1.1/api/1.0/?method=lan.getHostsList|grep host|awk -F'"' '{print $8 ", " $6 ", " $10 ",  " $16 ", " $4}'
from urllib.request import urlopen, Request, HTTPError, URLError
from bs4 import BeautifulSoup

try:
  default_gw_url = SFR_pass.ip_url()[1]
except:
  default_ipv6_gw = '[' + os.popen('ip -6 r|grep $(ip r|grep default|awk \'{print $NF}\')|head -n1|cut -d/ -f1').read().rstrip() + '1]' 
  default_gw_url = default_ipv6_gw

if 'default_ipv6_gw' in locals() and ( not default_ipv6_gw or len(default_ipv6_gw) <= 5 ):
  warn("[info] unable to locate IPv6 router; trying IPv4")
  default_ipv4_gw = os.popen('ip route|grep default|head -n1|awk \'{print $3}\'').read().rstrip()
  default_gw_url = default_ipv4_gw
if not default_gw_url or len(default_gw_url) <= 5:
  warn("[err] unable to locate router: " + default_gw_url)
  sys.exit(1)
#else:
#  warn("[info] gw: " + default_gw + " is " + str(len(default_gw_url)) + " in size")

known_dev_url = 'http://' + default_gw_url + '/api/1.0/?method=lan.getHostsList'
req = Request(known_dev_url)
html = urlopen(req).read()
bs = BeautifulSoup(html,'lxml')
hosts = bs.find_all(lambda tag: tag.name=='host' and tag.has_attr('mac'))
#hosts = bs.find_all(lambda tag: tag.name=='host')

def cron_example():
  """
SHELL=/bin/bash
* * * * * cd ~/files/github/SFR/; ./SFR.py 1>/tmp/cron.log 2>/tmp/cron.log
# we only want to graph in the early morning and early evening
*/10 8-10 * * * cd ~/files/github/SFR/var; ./SFR_graph 1>/dev/null 2>/dev/null; ./SFR_export
*/10 16-21 * * * cd ~/files/github/SFR/var; ./SFR_graph 1>/dev/null 2>/dev/null; ./SFR_export
  """

def main():
  #html_state_lan(); sys.exit(0)
  if hosts:
     #  <host type="pc" name="laptop" ip="192.168.1.12" mac="7A:74:FB:C5:99:06" iface="wlan0" probe="2335076" alive="8630904" status="online" />
     for h in hosts:
        #print(h)
        MAC = h.get("mac")
        name = h.get("name")
        ipv4 = h.get("ip")
        iface = h.get("iface")
        status = h.get("status")
        #print("{}, {}, {}, {}, {}".format(MAC,ipv4,iface,status,name))
        var = config.get('local','var').strip('"') #in case someone quotes the variable
        this_var = var + '/' + MAC + '/'
        #if os.path.isdir(this_var) and ( 'verbose' in locals() and verbose >= 1 ) or ( 'debug' in locals() and debug >= 1):
        #  print("UPDATE {}, {}, {}, {}, {}".format(MAC,ipv4,iface,status,name))
        #elif not os.path.isdir(this_var):
        if not os.path.isdir(this_var):
          print("create {}".format(this_var))
          mkdir(this_var)

     # and then `update` data into it the DB
     update_RRD()

if __name__ == '__main__':
    main()

# NTS we still aren't storing the ./SFR_html_state_wifi.py|grep -E '[t|r]xbyte' ;# txbyte = 768063512 \n rxbyte = 3708870080
# NTS we plan for SFR.cfg to let us indicate flows that should be combined into a single graph (for a user with multiple devices)
# NTS also the ability for SFR_export to place individual graphs in specific location via [ftp,scp,rsync]
