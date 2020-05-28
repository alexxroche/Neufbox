#!/usr/bin/env python3
#SFR_ntop.py ver 20200526181839 Copyright 2018 alexx, MIT Licence
#rdfa:deps="['sudo pip3 install ConfigParser']"
import os,sys,re,requests,configparser
from subprocess import Popen, PIPE

"""
  Plan: parse the HTML fragments of 
SFR_html_get.py http://192.168.1.1/state/lan|html2xpath table|grep '>'
  into 08:bd:43:88:38:58 [packet/second] [Signal power in -dB] $guess_at_name [uptime]

"""

strut = ( 'MAC', 'ipv4', 'signal', 'rates', 'uptime', 'idle', 'p_sent', 'fail', 'u_sent','m_sent','t_rate','r_rate' )
"""
MAC address 30:10:b3:5b:54:f5
IP address  192.168.1.67
Signal power    -51 dB
Supported rates [ 1 2 5.5 6 9 11 12 18 24 36 48 54 ] Mbit/s
Connection uptime 35180 seconds
Idle time 0 second
Packets sent  3848639
Packets sent failures 8
Unicast packets sent  1664006
Multicast packets sent  2231
Packet send rate  65000 Kbits/s
Packet receive rate
"""

from datetime import datetime, timedelta, timezone
#start = datetime.now(timezone.utc).strftime('%Y-%m-%d')
start = datetime.now(timezone.utc)

rate = {} #each cycle of request shows the delta for $MAC since $start

def main():
   lan_state = 'SFR_html_get.py http://192.168.1.1/state/lan|html2xpath table|grep ">"'
   data = {}
   html = ''
   try:
    html = Popen(lan_state, shell=True, stdout=PIPE).stdout.read()
   except (KeyboardInterrupt, SystemExit):
    raise
   except Exception as e:
    #print(f'html: {e}')
    #return
    print("[i] Go gett'em champ")
    sys.exit(3) # you probably pressed Ctrl+d
   from bs4 import BeautifulSoup
   from pprint import pprint
   if not html:
    return
   soup = BeautifulSoup(html, 'html.parser')
   #if len(soup) <= 3: return #debug
   if len(soup) <= 3:
    #print(f'{lan_state} := {soup}') #debug NTS we probably need to do the old "API.get.token" trick
    return
   try:
      print('-------------------------------------------------------------------------------')
      for match in soup.find_all('table'):
        row = match.find_all('td')
        if len(row) is 12:
          key = re.sub("\s*",'', row[0].contents[0].rstrip("\n"))
          data[key] = {'MAC': row[0].contents[0]}
          for i, s in enumerate(strut):
            data[key][s] = row[i].contents[0]
          #pprint(f'{data}')
        #else:
      for MAC in data:
        dev = data[MAC]
        packets = int(dev['p_sent']) + int(dev['u_sent']) + int(dev['m_sent'])
        if MAC in rate:
          rate[MAC]['current'] = packets
        else:
          rate[MAC] = {'start': packets}

        dt = datetime.now(timezone.utc)-start  # delta from start
        tis = divmod(dt.total_seconds(), 60)[1] #time in seconds
        if tis <= 0: tis = 1
        #print(f"{MAC}: {packets}\t {int(packets)/tis}")
        pps = int(packets)/tis # packets per second
        print(f"{MAC}: {packets}\t {pps:.0f}")
        #  print(f'{len(row)}')
      #print('-------------------------------------------------------------------------------')
   except Exception as e:
      print(f'try: {e}')
      for match in soup.find_all('table'):
         print(match[0])


if __name__ == '__main__':
  """
  TODO
    rather than printing to the screen we, build the next output,
     then ensure that its been {about} 1 second since we last printed,
      and then clear the previous printed lines and print the new updated screen
  """
  """ imortal
  while True:
    try:
      main()
    except:
      pass
  """
  while True:
    try:
      main()
      reset = "cd /home/alexx/files/github/SFR/SFR/; ./SFR_API.py"
      clear_lock = Popen(reset, shell=True, stdout=PIPE).stdout.read().decode("utf8").rstrip("\n")
      if not "succes" in clear_lock:
        print(f"{clear_lock}")
        sys.exit(1)

    except (KeyboardInterrupt, SystemExit):
      sys.tracebacklimit = 0  # STFU
      #print() # leave ^C on its own line
      sys.stdout.write(' ')
      sys.exit(0)
    except Exception as e:
      sys.tracebacklimit = 0  # STFU
      print(f'main: {e}')
      sys.exit(0)

