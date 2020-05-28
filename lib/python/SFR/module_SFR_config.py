#!/usr/bin/env python3

import os,sys
PACKAGE_PARENT = '..'
#SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
SCRIPT_DIR = os.path.realpath(os.path.dirname(inspect.getfile(inspect.currentframe())))
#SCRIPT_DIR = os.path.realpath(os.path.dirname(__file__))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
from SFR.SFR_functions import *
try:
  if os.path.isdir('./SFR'):
    import SFR.SFR_functions as SFR_functions
  else:
    from .SFR_functions import get_cfg
except:
  if os.path.isfile('./SFR_functions.py'):
    from .SFR_functions import get_cfg as get_cfg
    print("[info] GOOD NEWS ./SFR_functions.py found!")
  else:
    try:
      from .SFR_functions import *
    except:
      err = "has happened"

tmp_dir=''
script_name = os.path.basename(sys.argv[0])
conf_file='SFR.cfg'
conf_path='./'
if not os.path.isfile(conf_file):
  conf_file='../SFR.cfg'
  conf_path='../'
try:
  config = get_cfg('SFR',conf_file)
except:
  ei = sys.exc_info()[0]
  print("[err] %s" % ei)
  sys.exit(0)
  try:
    config = SFR_functions.get_cfg('SFR',conf_file)
  except:
    e = sys.exc_info()[0]
    print("[err] %s" % e)
    #sys.exit(1)

if hasattr(config, 'get'):
  var = config.get('local','var').strip('"') #in case someone quotes the variable
else:
  print("[err] you do NOT understand module inheridance. (or spelling)")
  var = '../var'
