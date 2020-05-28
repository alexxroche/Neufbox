#!/usr/bin/env python3
#rdfa.deps="[python3]"
import os,sys,requests,configparser
from os.path import dirname
from subprocess import Popen, PIPE
sys.path.append(dirname(__file__))

cpe_ip = '192.168.1.1' #until we move to [ipv6]

#  SFR_functions
"""
helper functions
"""

def pwd():
  abspath = os.path.dirname(os.path.abspath(sys.argv[0]))
  if os.path.islink(sys.argv[0]):
      abspath = os.path.dirname(os.path.realpath(sys.argv[0]))
  return abspath

def get_cfg(script_name='SFR', conf_file='SFR.cfg', abspath=pwd()):
  #print("[YOU ARE HERE] " + os.path.isdir(os.path.realpath(conf_file)))
  #sys.exit(1)
  if os.path.isdir(os.path.realpath('~/.config/'+script_name)):
      if os.path.isfile(os.path.realpath('~/.config/'+script_name)+conf_file):
          CFG = os.path.realpath('~/.config/'+script_name)+conf_file
      elif os.path.isfile(os.path.realpath('~/.config/'+script_name)+script_name+conf_file):
          CFG = os.path.realpath('~/.config/'+script_name)+script_name+conf_file
  elif os.path.isdir(os.path.realpath(conf_file)):
    CFG = conf_file
  else:
      CFG = abspath+'/'+conf_file
  if os.path.isfile(CFG):
    config = configparser.ConfigParser(delimiters=('='))
    #config.readfp(open(CFG))
    config.read_file(open(CFG))
    return config
    CFG = abspath+'/'+conf_file
  elif os.path.isfile(abspath+'/.'+conf_file):
    CFG = abspath+'/.'+conf_file
    config = configparser.ConfigParser(delimiters=('='))
    config.readfp(open(CFG))
    #print(CFG)
    return config
  else:
    print("[warn] no configuration file located in {}[/.]{} for {}".format(abspath,conf_file,script_name))

### SFR_config.py

def ip_url():
  ip4_gw  = '192.168.1.1'
  ip  = ip4_gw #hopefully we will be pleasantly surprised and find that we upgrade to IPv6 like its 2001
  ip6_gw_query = 'ip -6 r|grep "/"|head -n1|awk \'{print $1}\'|sed \'s/\/.*/1/\'|tr -d "\n"'
  ip4_gw_query = 'ip r|head -n1|awk \'{print $3}\''
  ip6_gw = Popen(ip6_gw_query, shell=True, stdout=PIPE).stdout.read()
  ip6_gw_ping = "ping6 -q -c1 -w1 {} 1>/dev/null 2>/dev/null && echo 0 || echo 1".format(ip6_gw.decode("utf-8").rstrip())
  ip6_gw_ping = Popen(ip6_gw_ping, shell=True, stdout=PIPE).stdout.read()
  if len(ip6_gw) >= 3 and ip6_gw_ping.decode("utf-8").rstrip() != 1 and not b"fe80::1" in ip6_gw:
    ip = ip6_gw.decode("utf-8").rstrip()
  else:
    if not ip6_gw_ping.decode("utf-8").rstrip() != 1 and not b"fe80::1" in ip6_gw:
      print('ERR: {}'.format(ip6_gw_ping.decode("utf-8").rstrip()))
    print('Using IPv4 gw: {} (maybe you should install nftables and enable IPv6?)'.format(ip))
  return ip

def ip_gw_MAC():
  #ip = ip_url()[0]
  ip = ip_url()
  #print(f"[d] ip neigh|grep {ip} |head -n1|awk " +  "\'{print $5}\'")
  ip_gw_MAC =  Popen('ip neigh|grep ' + ip + '|head -n1|awk \'{print $5}\'', shell=True, stdout=PIPE).stdout.read().decode("utf-8").rstrip()
  #return ip_gw_MAC.upper().rstrip("\n")
  return ip_gw_MAC.upper()[:-1] # we chop (rather than rstrip) because we may have multiple MAC for a CPE (with just the last bit incremented)

DEBUG = 0
tmp_dir=''
script_name = os.path.basename(sys.argv[0])
conf_filename = 'SFR.cfg'
conf_path='./'
conf_file= conf_path + conf_filename
if not os.path.isfile(conf_file):
  conf_path='../'
  conf_file= conf_path + conf_filename

try:
  config = get_cfg('SFR',conf_file)
except:
  ei = sys.exc_info()[0]
  if DEBUG >= 1: print("[err 19] %s" % ei)
  try:
    conf_path='./'
    conf_file= conf_path + conf_filename
    try:
      config = SFR_functions.get_cfg('SFR',conf_file)
    except:
      config = get_cfg('SFR',conf_file)
  except:
    e = sys.exc_info()[0]
    print("[err 24] %s" % e)
    #sys.exit(1)

if hasattr(config, 'get'):
  var = config.get('local','var').strip('"') #in case someone quotes the variable
  if not os.path.isdir(var):
    var = '.' + var
else:
  print("[err] you do NOT understand module inheridance. (or spelling)")
  var = '../var'



###############################
#### / slurped SFR_pass.py ####
###############################

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
    try:
      config = SFR_config.config
    except:
      config = config
    if hasattr(config, 'get'):
      password = config.get('local','password').strip('"') #in case someone quotes the variable
    #print(f'[i] fetch_pass found {password}')

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
      pph_search = Popen('sudo grep -A25 "\[' + MAC_MATCH + '" ' + WICD_WIFI_CONF + '|grep \'key =\'|cut -d= -f2|head -n1', shell=True, stdout=PIPE).stdout.read()
      password = pph_search.decode("utf-8").strip()

  if password:
    return password

###############################
#### / slurped SFR_pass.py ####
###############################

def SFR_hash(*args):
  if not len(args) == 2: return None
  data_cmd='echo "' + str(args[0]) + '"|tr -d \'\n\''
  data= Popen(data_cmd, shell=True, stdout=PIPE).stdout.read()
  key_cmd ='echo "' + str(args[1]) + '"|tr -d \'\n\'|openssl dgst -sha256|cut -d\' \' -f2'
  key= Popen(key_cmd, shell=True, stdout=PIPE).stdout.read()
  cmd = 'echo "' + str(key) + '"|tr -d \'\n\'|openssl dgst -sha256 -hmac "' + str(data) + '"|cut -d" " -f2'
  return Popen(cmd, shell=True, stdout=PIPE).stdout.read().decode("utf8").rstrip("\n")

def SFR_fetch_token():
  TOKEN_cmd='curl -s -G http://' + cpe_ip + '/api/1.0/?method=auth.getToken|grep token|cut -d\'"\' -f2'
  try:
    TOKEN=Popen(TOKEN_cmd, shell=True, stdout=PIPE).stdout.read().decode("utf8").rstrip("\n")
  except:
    TOKEN=Popen(TOKEN_cmd, shell=True, stdout=PIPE).stdout.read().rstrip("\n")
  return TOKEN
  """
    import ssl,requests
    from websocket import create_connection
    KEY = 'your-secret-key'
    url = 'https://api.binance.com/api/v1/userDataStream'
    listen_key = requests.post(url, headers={'X-MBX-APIKEY': KEY})['listenKey']
    connection = create_connection('wss://stream.binance.com:9443/ws/{}'.format(KEY), 
                               sslopt={'cert_reqs': ssl.CERT_NONE})
  """ 

def SFR_token(username, passwd):
  TOKEN=SFR_fetch_token()
  if not TOKEN or TOKEN is None:
    print("[err] failed to receive a token: " + str(TOKEN))
    print(f"[info] try: curl -s -G http://{cpe_ip}/api/1.0/?method=auth.getToken")
    sys.exit(1)
  if not username or username is None:
    print("[err] unable to locate username")
    sys.exit(1)
  if not passwd or passwd is None:
    print("[err] unable to locate passwd")
    sys.exit(1)

  print(f'SFR_HASH = SFR_hash({TOKEN}, {username}) + SFR_hash({TOKEN}, {passwd})') # DEBUG
  #SFR_HASH= str( str(SFR_hash(TOKEN, username)) + str(SFR_hash(TOKEN, passwd)) )#.decode("utf8")
  #user_HASH = SFR_hash(TOKEN, username)
  #pass_HASH = SFR_hash(TOKEN, passwd)
  SFR_HASH = str(SFR_hash(TOKEN, username) + SFR_hash(TOKEN, passwd)) #.decode("utf8")
  print(f'curl -s http://{cpe_ip}/api/1.0/?method=auth.checkToken&token={TOKEN}&hash={SFR_HASH}')
  checkToken_cmd="curl -s http://" + cpe_ip + "/api/1.0/?method=auth.checkToken\&token=" + TOKEN + "\&hash=" + SFR_HASH

  checkToken=Popen(checkToken_cmd, shell=True, stdout=PIPE).stdout.read().decode("utf8")
  #if not checkToken.match("auth"):
  if not "auth" in checkToken:
      print("[WARN] failed to check token " + TOKEN + " with hash: " + SFR_HASH)
      print("[info] its possible that the CPE has locked us out with a cooldown:" + checkToken)
      sys.exit(1)
  return TOKEN

def reset_CPE():
  reset_hack_because_python_sux=Popen("../SFR_reset.sh", shell=True, stdout=PIPE).stdout.read().decode("utf8")
  if not "success" in reset_hack_because_python_sux:
    print("Failed to reset using SFR_reset.sh" + reset_hack_because_python_sux)
    sys.exit(1)
  else:
    print("[i] bash > python auth reset successful")
    sys.exit(0)
  # NTS you are frustrated with python and so using bash as a dirty hack ('cause it works.) 20200527102256

  # the CPE is locking us out after an hour (60ish requests) we are trying to use login (or API auth) to reset it)
  # still need to detect /being locked out/
  try: # properly
    username= SFR_pass.fetch_user()
    passwd= SFR_pass.fetch_pass()
  except: # dirty hack (to make this script portable)
    username= fetch_user()
    passwd= fetch_pass()

  TOKEN = SFR_token(username, passwd)
  """
    Fetching the TOKEN may be enough to convince the CPE that we are still friends, but just to be sure
    lets log in using the web interface as well as the API (NOTE: every API should have a flood reset option)
    # NTS we should check to see if, by using another IPv6 address from our /64 will give us a clean name.
  """
  #PAYLOAD='{"login": "'$username'", "password": "'$passwd'"}'
  DATA='login=' + username + '&password=' + passwd
  #DATA='login='$username'%26password='$passwd  # FAILS!
  CJAR="/tmp/.SFR_reset.cookies"
  DEBUG_LOG="/tmp/SFR_DEBUG.log"
  cmd='curl -L --cookie-jar ' + CJAR + ' -s -o /dev/null -d "' + DATA + '" -w "%{http_code}" \'http://' + cpe_ip +'/login?page_ref=/wifi/macfiltering\''
  reset_houly_flood_detection = Popen(cmd, shell=True, stdout=PIPE).stdout.read()

if __name__ == '__main__':
    reset_CPE()
    #import sys; sys.exit(main(sys.argv[1:])) # this also works
