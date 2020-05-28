import configparser, os,sys,re

# import string for translate

"""
helper functions
"""

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def is_digit(n):
    try:
        int(n)
        return True
    except ValueError:
        return  False

def warn(*args, **kwargs):
  print(*args, file=sys.stderr, **kwargs)

#warn("fatal error"); sys.exit(3)


def mkdir(path, mode=0o755):
    try:
        #os.mkdir(path, mode=0o755) # fails if ./var/ does not exist
        os.makedirs(path, mode=mode)
        #os.makedirs(path, 0o755) #explicit is better than implicit
        #os.chmod(path, 0o755)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

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
    config.readfp(open(CFG))
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

def dump_conf():
    for w in config.items():
        print("{}".format(w[0]))
    sys.exit(0)

def log(str):
    if ( 'opt' in vars() or 'opt' in globals() ) and 'd' in opt and opt['d'] >= 2:
        print("{}".format(str))

def opt_set(flag):
  if ( 'opt' in vars() or 'opt' in globals() ) and flag in opt and opt[flag] != 0:
    return True

def usage():
  print("pySFR [-h|-K|-v]")
  print("  -K dump conf")
  print("  -h help (this menu)")
  print("  -v verbose (debug stuff)")
  print(" Copyright 2019 isobel, MIT Licence")

  sys.exit(0)

def check_config():
  if 'config' in locals() or 'config' in globals():
    if hasattr(config, 'sections'):
      print("{}".format(config.sections()))
  for s in config.sections():
    if not 'local' in s: continue
    import json
    for pMAC in json.loads(config.get('local','whitelist_mac')): print(pMAC)
    #pMAC = config.get('local','whitelist_mac'); print(pMAC)
    for l in config.items(s):
      print("[cfg] {} = {}".format(l[0],l[1]))
  sys.exit(1)

