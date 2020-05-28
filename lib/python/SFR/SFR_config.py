#!/usr/bin/env python3

import os,sys
DEBUG = 0
#from .SFR_functions import *
import SFR_functions
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
    config = SFR_functions.get_cfg('SFR',conf_file)
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
