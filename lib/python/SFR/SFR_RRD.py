#!/usr/bin/env python3
#rdfa.deps="[python3-rrdtool]"
import os,sys
from os.path import dirname
sys.path.append(dirname(__file__))
try:
#	#import SFR_config
#	#from .SFR_functions import *
	import SFR_functions
	import SFR_config
	import SFR_pass
except:
	from .SFR_config import *
	from .SFR_pass import *
#  conf_file='SFR.cfg'
#  conf_path='./'
#  if not os.path.isfile(conf_file):
#    conf_file='../SFR.cfg'
#    conf_path='../'
#  config = get_cfg('SFR',conf_file)
#  #config = SFR_functions.get_cfg('SFR',conf_file)
#  if hasattr(config, 'get'):
#    var = config.get('local','var').strip('"') #in case someone quotes the variable
#var = '../var'

import rrdtool
from subprocess import Popen, PIPE
def calculate_RRD_RRA_from_step(step):
  """
  given an RRD type { GAUGE | COUNTER | DERIVE | DCOUNTER | DDERIVE | ABSOLUTE}
     a step (60 or 300)
  return a sensible RRA:AVERAGE for each of [range in ranges[hour, day, week, month, year, bienial, demi-decade, decade, century]
    (this should use the minimum amount of space)
  """

def validate_rrd_value(value):
  if value == None:
    return ":U"
  else:
    return ":{}".format(value)

def create_wifi_client_rrd_counter(*args, **kwargs):
  this_MAC = args[0]
  #this_pkts = args[1]
  #this_uptm = args[2]
  this_pkts = ''.join(c for c in args[1] if c.isdigit() or c == '.' or c == '-')
  this_uptm = ''.join(c for c in args[2] if c.isdigit() or c == '.' or c == '-')
  #rrd_db_fn = 'wifi_client_rrd_counter.rrd'
  #import inspect; #rrd_db_fn =  '{}.rrd'.format(inspect.stack()[0][3])
  # discover db_fn from the function name
  rrd_db_fn =  '{}.rrd'.format(sys._getframe().f_code.co_name)[7:]

  if kwargs is not None:
    var = kwargs['var'] + '/' + this_MAC
  else:
    var = './var_missing/'

  #if not os.path.isfile('{}/wifi_client_rrd_counter.rrd'.format( var + this_MAC)):
  uptm_db_fn = '{}/uptime_{}'.format(var,rrd_db_fn)
  if not os.path.isfile(uptm_db_fn):
    step = "300"
    #print("[WARN] missing  counter RRD for {}".format(var + this_MAC))
    print("[WARN] missing  counter RRD for {}".format(uptm_db_fn))
    # we check uptime every 60 seconds
    data_sources=[ 'DS:uptime:COUNTER:{}:0:12500000'.format(step) ]
    rrdtool.create( uptm_db_fn,
       '--step', step,
       '--start', 'now',
       data_sources,
       'RRA:AVERAGE:0.5:1:576',
       'RRA:AVERAGE:0.5:6:672',
       'RRA:AVERAGE:0.5:24:732',
       'RRA:AVERAGE:0.5:144:1460')
  pkts_db_fn = '{}/packets_{}'.format(var,rrd_db_fn)
  if not os.path.isfile(pkts_db_fn):
    #step = "300" #N.B. must be a str
    step = "60" #N.B. must be a str
    data_sources=[ 'DS:pkts:COUNTER:{}:0:12500000'.format(step) ]
    rrdtool.create( pkts_db_fn,
       '--step', step,
       '--start', 'now',
       data_sources,
       'RRA:AVERAGE:0.5:1:576',
       'RRA:AVERAGE:0.5:6:672',
       'RRA:AVERAGE:0.5:24:732',
       'RRA:AVERAGE:0.5:144:1460')
  
  #update
  if os.path.isfile(uptm_db_fn):
    value = "N" + validate_rrd_value(this_uptm)
    done = rrdtool.update(uptm_db_fn, str(value)) #should work
    #done = Popen('/usr/bin/rrdupdate {} {}'.format(uptm_db_fn, value), shell=True, stdout=PIPE).stdout.read()
    #rrdtool.update(uptm_db_fn, "-t", "uptime", '{}'.format(value)) # also works, but we seem to be having the wrong vales (slightly low)
    #done = Popen('/usr/bin/rrdupdate {} {}'.format(uptm_db_fn, value), shell=True, stdout=PIPE).stdout.read()
    rrdtool.update(uptm_db_fn, "-t", "uptime", "%s" % value) # also works, but we seem to be having the wrong vales (slightly low)
    if sys.stdout.isatty(): print("[info] updated {} with {} [{}]".format(uptm_db_fn, value, done))
  if os.path.isfile(pkts_db_fn):
    value = "N" + validate_rrd_value(this_pkts)
    #value = "N:" + this_pkts
    #done = rrdtool.update(pkts_db_fn, "N:4321") #no works
    done = rrdtool.update(pkts_db_fn, str(value)) #finally working! (with step = 300)
    #done = Popen('/usr/bin/rrdupdate {} {}'.format(pkts_db_fn, value), shell=True, stdout=PIPE).stdout.read()
    #rrdtool.update(pkts_db_fn, "-t", "pkts", "%s" % value) # also works, but we seem to be having the wrong vales (slightly low)  OR ZERO!
    if sys.stdout.isatty(): print("[info] updated {} with {} [{}]".format(pkts_db_fn, value, done))


#END = os.popen('echo $(( $(date +%s) - ( ( $(printf "%.0f" $(date +%M)) % 5 ) * 60 + $(printf "%.0f" $(date +%S)) )  ))').read().rstrip()

def check_db_is_updating(*args):
  cmd='find $var -name "*.rrd" -exec rrdtool dump {} \; |grep \'<row\'|grep -v NaN|grep -v \'0.0000000000e+00\''
  # see if we have current values


def create_wifi_client_rrd_gauge(*args, **kwargs):
  """ (The pretty red and black one)
  also "~/lib/rrd/rrd/RTT/{create,ping,ping-graph}.sh "
  also "~/files/github/SFR/rrd_wlan.pl" create http://localhost/rrdtool/wlan0.html
        ~/files/github/AIF/ISP/servers/monitor/rrd/create.sh
  http://localhost:8181/rrds/index.html 

 N.B. "~/lib/rrd/rrd/RTT/ping-graph.sh"   is the nicest!
  """
  this_MAC = args[0]
  this_pkts = ''.join(c for c in args[1] if c.isdigit() or c == '.' or c == '-')
  this_uptm = ''.join(c for c in args[2] if c.isdigit() or c == '.' or c == '-')
  rrd_db_fn =  '{}.rrd'.format(sys._getframe().f_code.co_name)[7:]
  if kwargs is not None:
    var = kwargs['var'] + '/' + this_MAC
  else:
    var = './var_missing/'
  # uptime
  uptm_db_fn = '{}/uptime_{}'.format(var,rrd_db_fn)
  if not os.path.isfile(uptm_db_fn):
    step = 60
    print("[WARN] missing  counter RRD for {}".format(uptm_db_fn))
    data_sources=[ 'DS:uptime:GAUGE:{}:0:12500000'.format(step * 2) ]
    rrdtool.create( uptm_db_fn,
       '--step', str(step),
       '--start', 'now',
       data_sources,
       'RRA:AVERAGE:0.5:1:2880',
       'RRA:AVERAGE:0.5:6:672',
       'RRA:AVERAGE:0.5:24:732',
       'RRA:AVERAGE:0.5:144:1460')
  # packets
  pkts_db_fn = '{}/packets_{}'.format(var,rrd_db_fn)
  if not os.path.isfile(pkts_db_fn):
    step = 60
    print("[WARN] missing counter RRD for {}".format(pkts_db_fn))
    data_sources=[ 'DS:packets:GAUGE:{}:0:12500000'.format(step * 2) ]
    rrdtool.create( pkts_db_fn,
       '--step', str(step),
       '--start', 'now',
       data_sources,
       'RRA:AVERAGE:0.5:1:2880',
       'RRA:AVERAGE:0.5:6:672',
       'RRA:AVERAGE:0.5:24:732',
       'RRA:AVERAGE:0.5:144:1460')
  #update
  if os.path.isfile(uptm_db_fn):
    value = "N" + validate_rrd_value(this_uptm)
    done = rrdtool.update(uptm_db_fn, str(value)) #should work
    rrdtool.update(uptm_db_fn, "-t", "uptime", "%s" % value) # also works, but we seem to be having the wrong vales (slightly low)
    if sys.stdout.isatty(): print("[info] updated {} with {} [{}]".format(uptm_db_fn, value, done))
  if os.path.isfile(pkts_db_fn):
    value = "N" + validate_rrd_value(this_pkts)
    done = rrdtool.update(pkts_db_fn, str(value)) #finally working! (with step = 300)
    if sys.stdout.isatty(): print("[info] updated {} with {} [{}]".format(pkts_db_fn, value, done))

  """

# ~/files/github/AIF/ISP/servers/monitor/rrd/graph.sh
$RRDTOOL graph ${OUTPUT%ping.png}hour_ping.png \
        -t "Hourly WAN Ping" -v "Time in ms" \
        --start="now-1h" \
        --end="now" \
        --height="120" \
         --width="440" \
        -c "BACK#000000" \
        -c "SHADEA#000000" \
        -c "SHADEB#000000" \
        -c "FONT#DDDDDD" \
        -c "CANVAS#202020" \
        -c "GRID#666666" \
        -c "MGRID#AAAAAA" \
        -c "FRAME#202020" \
        -c "ARROW#FFFFFF" \
        "DEF:ping_time=$FILE:ping:AVERAGE" \
        "CDEF:shading2=ping_time,0.98,*" "AREA:shading2#F90000:$HOST" \
        "GPRINT:ping_time:LAST:Last\: %5.2lf ms" \
        "GPRINT:ping_time:MIN:Min\: %5.2lf ms" \
        "GPRINT:ping_time:MAX:Max\: %5.2lf ms" \
        "GPRINT:ping_time:AVERAGE:Avg\: %5.2lf ms" \
        "CDEF:shading10=ping_time,0.90,*" "AREA:shading10#E10000" \
        "CDEF:shading15=ping_time,0.85,*" "AREA:shading15#D20000" \
        "CDEF:shading20=ping_time,0.80,*" "AREA:shading20#C30000" \
        "CDEF:shading25=ping_time,0.75,*" "AREA:shading25#B40000" \
        "CDEF:shading30=ping_time,0.70,*" "AREA:shading30#A50000" \
        "CDEF:shading35=ping_time,0.65,*" "AREA:shading35#960000" \
        "CDEF:shading40=ping_time,0.60,*" "AREA:shading40#870000" \
        "CDEF:shading45=ping_time,0.55,*" "AREA:shading45#780000" \
        "CDEF:shading50=ping_time,0.50,*" "AREA:shading50#690000" \
        "CDEF:shading55=ping_time,0.45,*" "AREA:shading55#5A0000" \
        "CDEF:shading60=ping_time,0.40,*" "AREA:shading60#4B0000" \
        "CDEF:shading65=ping_time,0.35,*" "AREA:shading65#3C0000" \
        "CDEF:shading70=ping_time,0.30,*" "AREA:shading70#2D0000" \
        "CDEF:shading75=ping_time,0.25,*" "AREA:shading75#180000" \
        "CDEF:shading80=ping_time,0.20,*" "AREA:shading80#0F0000" \
        "CDEF:shading85=ping_time,0.15,*" "AREA:shading85#000000" >/dev/null


 """

def create_wifi_client_rrd_derive(*args, **kwargs):
  """ 
  /var/www/temp/network.sh http://localhost/temp/net.html
  http://localhost:8181/
  """
  this_MAC = args[0]
  this_pkts = ''.join(c for c in args[1] if c.isdigit() or c == '.' or c == '-')
  this_uptm = ''.join(c for c in args[2] if c.isdigit() or c == '.' or c == '-')
  rrd_db_fn =  '{}.rrd'.format(sys._getframe().f_code.co_name)[7:]
  if kwargs is not None:  
    var = kwargs['var'] + '/' + this_MAC
  else:
    var = './var_missing/'
  # uptime
  uptm_db_fn = '{}/uptime_{}'.format(var,rrd_db_fn)
  if not os.path.isfile(uptm_db_fn):
    step = 60
    print("[WARN] missing  counter RRD for {}".format(uptm_db_fn))
    data_sources=[ 'DS:uptime:DERIVE:{}:0:12500000'.format(step * 10) ]
    rrdtool.create( uptm_db_fn,
       data_sources,
       'RRA:AVERAGE:0.5:1:576',
       'RRA:AVERAGE:0.5:6:672',
       'RRA:AVERAGE:0.5:24:732',
       'RRA:AVERAGE:0.5:144:1460')
  # packets
  pkts_db_fn = '{}/packets_{}'.format(var,rrd_db_fn)
  if not os.path.isfile(pkts_db_fn):
    step = 60
    print("[info] creating missing counter RRD for {}".format(pkts_db_fn))
    data_sources=[ 'DS:packets:DERIVE:{}:0:12500000'.format(step * 10) ]
    rrdtool.create( pkts_db_fn,
       data_sources,
       'RRA:AVERAGE:0.5:1:576',
       'RRA:AVERAGE:0.5:6:672',
       'RRA:AVERAGE:0.5:24:732',
       'RRA:AVERAGE:0.5:144:1460')
  #update
  if os.path.isfile(uptm_db_fn):
    value = "N" + validate_rrd_value(this_uptm)
    done = rrdtool.update(uptm_db_fn, str(value)) #should work
    rrdtool.update(uptm_db_fn, "-t", "uptime", "%s" % value) # also works, but we seem to be having the wrong vales (slightly low)
    if sys.stdout.isatty(): print("[info] updated {} with {} [{}]".format(uptm_db_fn, value, done))
  if os.path.isfile(pkts_db_fn):
    value = "N" + validate_rrd_value(this_pkts)
    done = rrdtool.update(pkts_db_fn, str(value)) #finally working! (with step = 300)
    if sys.stdout.isatty(): print("[info] updated {} with {} [{}]".format(pkts_db_fn, value, done))

  """
        $rrdtool create $db \
        DS:in:DERIVE:600:0:12500000 \
        DS:out:DERIVE:600:0:12500000 \
        RRA:AVERAGE:0.5:1:576 \
        RRA:AVERAGE:0.5:6:672 \
        RRA:AVERAGE:0.5:24:732 \
        RRA:AVERAGE:0.5:144:1460

        $rrdtool graph $img/network-$period.png -s -1$period \
        -t "Network traffic the last $period" -z \
        --end $END \
        -c "BACK#FFFFFF" -c "SHADEA#FFFFFF" -c "SHADEB#FFFFFF" \
        -c "MGRID#AAAAAA" -c "GRID#CCCCCC" -c "ARROW#333333" \
        -c "FONT#333333" -c "AXIS#333333" -c "FRAME#333333" \
        -h 134 -w 543 -l 0 -a PNG -v "B/s" \
        --watermark "Last updated $(date +%Y-%m-%d\ %H:%M:%S)" \
        --font WATERMARK:8 \
        DEF:in=$db:in:AVERAGE \
        DEF:out=$db:out:AVERAGE \
        VDEF:minin=in,MINIMUM \
        VDEF:minout=out,MINIMUM \
        VDEF:maxin=in,MAXIMUM \
        VDEF:maxout=out,MAXIMUM \
        VDEF:avgin=in,AVERAGE \
        VDEF:avgout=out,AVERAGE \
        VDEF:lstin=in,LAST \
        VDEF:lstout=out,LAST \
        VDEF:totin=in,TOTAL \
        VDEF:totout=out,TOTAL \
        "COMMENT:               " \
        "COMMENT:Minimum      " \
        "COMMENT:Maximum      " \
        "COMMENT:Average      " \
        "COMMENT:Current      " \
        "COMMENT:Total        \l" \
        "COMMENT:   " \
        "AREA:out#EDA36299:Out  " \
        "LINE1:out#C42200" \
        "GPRINT:minout:%5.1lf %sB/s   " \
        "GPRINT:maxout:%5.1lf %sB/s   " \
        "GPRINT:avgout:%5.1lf %sB/s   " \

      # we only have to check every 5 minutes (as we will only be checking connected devices)
        $rrdtool create MAC_packets.rrd --step 300\
        DS:ps:DERIVE:300:0:12500000 \
        DS:ups:DERIVE:300:0:12500000 \
        #DS:perc95:COMPUTE:ps,ups,+,95,PERCENT \
        RRA:AVERAGE:0.5:0.1:40320 \
        RRA:AVERAGE:0.5:0.2:43800 \
        RRA:AVERAGE:0.5:1:52560 \
        RRA:AVERAGE:0.5:2:52596 \
        RRA:AVERAGE:0.5:3:175320 \
        #RRA:MAX:0.5:0.1:40320 \
        #RRA:MAX:0.5:0.2:43800 \
        #RRA:MAX:0.5:1:52560 \
        #RRA:MAX:0.5:2:52596 \
        #RRA:MAX:0.5:3:175320 \
        #RRA:MIN:0.5:0.1:40320 \
        #RRA:MIN:0.5:0.2:43800 \
        #RRA:MIN:0.5:1:52560 \
        #RRA:MIN:0.5:2:52596 \
        #RRA:MIN:0.5:3:175320 \

  """
def create_wifi_client_rrd_absolute(*args, **kwargs):
  this_MAC = args[0]
  this_pkts = ''.join(c for c in args[1] if c.isdigit() or c == '.' or c == '-')
  this_uptm = ''.join(c for c in args[2] if c.isdigit() or c == '.' or c == '-')
  rrd_db_fn =  '{}.rrd'.format(sys._getframe().f_code.co_name)[7:]
  if kwargs is not None:
    var = kwargs['var'] + '/' + this_MAC
  else:
    var = './var_missing/'
  # uptime
  uptm_db_fn = '{}/uptime_{}'.format(var,rrd_db_fn)
  if not os.path.isfile(uptm_db_fn):
    step = 60
    points_per_sample = 3
    xpoints = 540
    rows = xpoints / points_per_sample
    realrows = int( rows * 1.1 )
    day_steps = int( 3600 * 24 / (step * rows ))
    week_steps = day_steps * 7
    month_steps = week_steps * 5
    year_steps = month_steps * 12
    print("[WARN] missing  counter RRD for {}".format(uptm_db_fn))
    data_sources=[ 
      'DS:uptime:ABSOLUTE:{}:0:U'.format(step * 2),
      'RRA:AVERAGE:0.5:{}:{}'.format(day_steps,realrows),
      'RRA:AVERAGE:0.5:{}:{}'.format(week_steps,realrows),
      'RRA:AVERAGE:0.5:{}:{}'.format(month_steps,realrows),
      'RRA:AVERAGE:0.5:{}:{}'.format(year_steps,realrows),
      "RRA:MIN:0.5:{}:{}".format(day_steps,realrows),
      "RRA:MIN:0.5:{}:{}".format(week_steps,realrows),
      "RRA:MIN:0.5:{}:{}".format(month_steps,realrows),
      "RRA:MIN:0.5:{}:{}".format(year_steps,realrows),
      "RRA:MAX:0.5:{}:{}".format(day_steps,realrows),
      "RRA:MAX:0.5:{}:{}".format(week_steps,realrows),
      "RRA:MAX:0.5:{}:{}".format(month_steps,realrows),
      "RRA:MAX:0.5:{}:{}".format(year_steps,realrows)
    ]
    rrdtool.create( uptm_db_fn,
       '--step', str(step),
       '--start', 'now',
       data_sources )
  # packets
  pkts_db_fn = '{}/packets_{}'.format(var,rrd_db_fn)
  if not os.path.isfile(pkts_db_fn):
    step = 60
    print("[WARN] missing counter RRD for {}".format(pkts_db_fn))
    data_sources=[ 
   'DS:packets:ABSOLUTE:{}:0:U'.format(step * 2),
     'RRA:AVERAGE:0.5:{}:{}'.format(day_steps,realrows),
     'RRA:AVERAGE:0.5:{}:{}'.format(week_steps,realrows),
     'RRA:AVERAGE:0.5:{}:{}'.format(month_steps,realrows),
     'RRA:AVERAGE:0.5:{}:{}'.format(year_steps,realrows),
     "RRA:MIN:0.5:{}:{}".format(day_steps,realrows),
     "RRA:MIN:0.5:{}:{}".format(week_steps,realrows),
     "RRA:MIN:0.5:{}:{}".format(month_steps,realrows),
     "RRA:MIN:0.5:{}:{}".format(year_steps,realrows),
     "RRA:MAX:0.5:{}:{}".format(day_steps,realrows),
     "RRA:MAX:0.5:{}:{}".format(week_steps,realrows),
     "RRA:MAX:0.5:{}:{}".format(month_steps,realrows),
     "RRA:MAX:0.5:{}:{}".format(year_steps,realrows)
  ]
    rrdtool.create( pkts_db_fn,
       '--step', str(step),
       '--start', 'now',
       data_sources )
  #update
  if os.path.isfile(uptm_db_fn):
    value = "N" + validate_rrd_value(this_uptm)
    done = rrdtool.update(uptm_db_fn, str(value)) #should work
    rrdtool.update(uptm_db_fn, "-t", "uptime", "%s" % value) # also works, but we seem to be having the wrong vales (slightly low)
    if sys.stdout.isatty(): print("[info] updated {} with {} [{}]".format(uptm_db_fn, value, done))
  if os.path.isfile(pkts_db_fn):
    value = "N" + validate_rrd_value(this_pkts)
    done = rrdtool.update(pkts_db_fn, str(value)) #finally working! (with step = 300)
    if sys.stdout.isatty(): print("[info] updated {} with {} [{}]".format(pkts_db_fn, value, done))

  """
 my $m = shift;
        my $xpoints = 540;
        my $points_per_sample = 3;
 my $rows = $xpoints/$points_per_sample;
 my $realrows = int($rows*1.1); # ensure that the full range is covered
 my $day_steps = int(3600*24 / ($rrdstep*$rows));
 # use multiples, otherwise rrdtool could choose the wrong RRA
 my $week_steps = $day_steps*7;
 my $month_steps = $week_steps*5;
 my $year_steps = $month_steps*12;
 my $rrdstep = 60;

 # mail rrd
 if(! -f $rrd and ! $opt{'only-virus-rrd'}) {
  RRDs::create($rrd, '--start', $m, '--step', $rrdstep,
    'DS:sent:ABSOLUTE:'.($rrdstep*2).':0:U',
    'DS:recv:ABSOLUTE:'.($rrdstep*2).':0:U',
    'DS:bounced:ABSOLUTE:'.($rrdstep*2).':0:U',
    'DS:rejected:ABSOLUTE:'.($rrdstep*2).':0:U',
    "RRA:AVERAGE:0.5:$day_steps:$realrows",   # day
    "RRA:AVERAGE:0.5:$week_steps:$realrows",  # week
    "RRA:AVERAGE:0.5:$month_steps:$realrows", # month
    "RRA:AVERAGE:0.5:$year_steps:$realrows",  # year
    "RRA:MAX:0.5:$day_steps:$realrows",   # day
    "RRA:MAX:0.5:$week_steps:$realrows",  # week
    "RRA:MAX:0.5:$month_steps:$realrows", # month
    "RRA:MAX:0.5:$year_steps:$realrows",  # year
    );
  $this_minute = $m;
 }
 elsif(-f $rrd) {
  $this_minute = RRDs::last($rrd) + $rrdstep;
 }

 # virus rrd
 if(! -f $rrd_virus and ! $opt{'only-mail-rrd'}) {
  RRDs::create($rrd_virus, '--start', $m, '--step', $rrdstep,
    'DS:virus:ABSOLUTE:'.($rrdstep*2).':0:U',
    'DS:spam:ABSOLUTE:'.($rrdstep*2).':0:U',
    "RRA:AVERAGE:0.5:$day_steps:$realrows",   # day
    "RRA:AVERAGE:0.5:$week_steps:$realrows",  # week
    "RRA:AVERAGE:0.5:$month_steps:$realrows", # month
    "RRA:AVERAGE:0.5:$year_steps:$realrows",  # year
    "RRA:MAX:0.5:$day_steps:$realrows",   # day
    "RRA:MAX:0.5:$week_steps:$realrows",  # week
    "RRA:MAX:0.5:$month_steps:$realrows", # month
    "RRA:MAX:0.5:$year_steps:$realrows",  # year
    );
 }
DRAW: src/mailgraph-1.14/mailgraph.cgi 
  """

def create_wifi_client_rrd():
  """
    here we take a list of required RRD types
    and create each of them

  create_wifi_client_rrd_absolute():
  create_wifi_client_rrd_derive():
  create_wifi_client_rrd_gauge():
  create_wifi_client_rrd_counter():

  """

def update_wifi_client_rrd(*args):
  """
    here we expect to be given data for an RRD.
    we first check that the RRD files exist
      if not we create each of them
    then we update them with the values
  """

def fetch_CPE_tx_rx():
  CPE_tx_rx = os.popen('./SFR_html_state_wifi.py|grep -E \'[t|r]xbyte\'').read().rstrip()
  if CPE_tx_rx:
    #print(CPE_tx_rx)
    for d in CPE_tx_rx.split('\n'):
      #print(d)
      name,value = d.split('=')
      print("{} is currently {} for the CPE".format(name, value))

def report_fetch_client_data():
  if os.path.isfile('./SFR_html_state_lan.py'):
    tmp_html =  os.popen('./SFR_html_state_lan.py').read().rstrip()
  elif os.path.isfile('../SFR_html_state_lan.py'):
    tmp_html =  os.popen('../SFR_html_state_lan.py').read().rstrip()
  else:
    tmp_html = html_state_lan()
  from bs4 import BeautifulSoup
  import re
  bs = BeautifulSoup(tmp_html,'lxml')
  #hosts = bs.find_all(lambda tag: tag.name=='table' and tag.class('wlanhost_stats'))
  hosts = bs.find_all(lambda tag: tag.name=='table', attrs={'class':'wlanhost_stats'})

  #hosts = bs.find_all(lambda tag: tag.name=='host')
  #html2txt $TMP_FILE|grep -v 'nbsp'|grep -A2 -E 'MAC address|Connection uptime|Packets sent$'|grep -E ':|[[:digit:]]'|while read r;do
  if hosts:
    for h in hosts:
      #print(h)
      #MAC = h.find('th',text="MAC address")
      #MAC = h.find('th',text=re.compile(r'MAC address'))
      MAC_anchor = h.find('th',text=re.compile(r'MAC address'))
      if MAC_anchor:
        MAC = MAC_anchor.findNext('td').contents[0].strip()
        cl_uptime = h.find('th',text=re.compile(r'Connection uptime')).findNext('td').contents[0].strip()
        cl_packets = h.find('th',text=re.compile(r'Packets sent')).findNext('td').contents[0].strip()
        print('MAC: ' + MAC + ' Uptime: ' + cl_uptime + ' Packets: ' + cl_packets)

def fetch_client_data():
  # trying to be ./fetch_SFR.sh
  tmp_html = html_state_lan()
  from bs4 import BeautifulSoup
  import re
  bs = BeautifulSoup(tmp_html,'lxml')
  hosts = bs.find_all(lambda tag: tag.name=='table', attrs={'class':'wlanhost_stats'})
  #print("We found [{}] hosts in ".format(len(hosts)))
  client_data = {}
  if hosts:
    for h in hosts:
      MAC_anchor = h.find('th',text=re.compile(r'MAC address'))
      if MAC_anchor:
        MAC = MAC_anchor.findNext('td').contents[0].strip()
        client_data[MAC] = {}
        cl_uptime = h.find('th',text=re.compile(r'Connection uptime')).findNext('td').contents[0].strip()
        cl_packets = h.find('th',text=re.compile(r'Packets sent')).findNext('td').contents[0].strip()
      client_data[MAC]['uptime'] = cl_uptime
      client_data[MAC]['packets'] = cl_packets
    return client_data
  else:
    # looks like the CPE is locking us out. Maybe we can rest by logging in?
    fix_cmd_1 = '~/bin/SFR_list_connected.sh fix'
    fix_cmd_2 = '~/bin/SFR_html_get.py'
    is_it_corrected_1 = Popen(fix_cmd_1, shell=True, stdout=PIPE).stdout.read()
    is_it_corrected_2 = Popen(fix_cmd_2, shell=True, stdout=PIPE).stdout.read()

  return None

def SFR_hash(*args):
  if not len(args) == 2: return None
  data_cmd='echo "' + str(args[0]) + '"|tr -d \'\n\''
  data= Popen(data_cmd, shell=True, stdout=PIPE).stdout.read()
  key_cmd ='echo "' + str(args[1]) + '"|tr -d \'\n\'|openssl dgst -sha256|cut -d\' \' -f2'
  key= Popen(key_cmd, shell=True, stdout=PIPE).stdout.read()
  cmd = 'echo "' + str(key) + '"|tr -d \'\n\'|openssl dgst -sha256 -hmac "' + str(data) + '"|cut -d" " -f2'
  return Popen(cmd, shell=True, stdout=PIPE).stdout.read()

def SFR_fetch_token():
  TOKEN_cmd='curl -s -G http://192.168.1.1/api/1.0/?method=auth.getToken|grep token|cut -d\'"\' -f2'
  TOKEN=Popen(TOKEN_cmd, shell=True, stdout=PIPE).stdout.read()
  return TOKEN

def SFR_token(username, passwd):
  TOKEN=SFR_fetch_token()
  if not TOKEN or TOKEN is None:
    print("[err] failed to receive a token: " + str(TOKEN))
    print("[info] try: curl -s -G http://192.168.1.1/api/1.0/?method=auth.getToken")
    sys.exit(1)
  if not username or username is None:
    print("[err] unable to locate username")
    sys.exit(1)
  if not passwd or passwd is None:
    print("[err] unable to locate passwd")
    sys.exit(1)

  SFR_HASH= SFR_hash(TOKEN, username) + SFR_hash(TOKEN, passwd)
  checkToken_cmd="curl -s http://192.168.1.1/api/1.0/?method=auth.checkToken\&token=" + TOKEN + "\&hash=" + SFR_HASH
  checkToken=Popen(checkToken_cmd, shell=True, stdout=PIPE).stdout.read()
  if not checkToken.match("auth"):
      print("[WARN] failed to check token " + TOKEN + " with hash: " + SFR_HASH)
      print("[info] its possible that the CPE has locked us out with a cooldown")
      sys.exit(1)
  return TOKEN

def reset_CPE():
  # the CPE is locking us out after an hour (60ish requests) we are trying to use login (or API auth) to reset it)
  # still need to detect /being locked out/
  username= SFR_pass.fetch_user()
  passwd= SFR_pass.fetch_pass()
  # refactor SFR_get_pass out of html_state_lan()

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
  cmd='curl -L --cookie-jar ' + CJAR + ' -s -o /dev/null -d "' + DATA + '" -w "%{http_code}" \'http://192.168.1.1/login?page_ref=/wifi/macfiltering\''
  reset_houly_flood_detection = Popen(cmd, shell=True, stdout=PIPE).stdout.read()

  """
  LOGIN_STATE="$(
  curl -L --cookie-jar $CJAR -s -o /dev/null -d "$DATA" -w "%{http_code}" 'http://192.168.1.1/login?page_ref=/wifi/macfiltering'; echo -n ' ' #WORKS
  )"
  if [ "$LOGIN_STATE" -ne 200 ]; then
    echo "[err] failed to login"
    exit 1
  fi
  READ_CHECK="$(
  curl -Lso /dev/null -c $CJAR -d $DATA -w "%{http_code}" http://192.168.1.1/wifi/macfiltering ; echo ' '|tr -d '\n' # WORKS!
  )"
  if [ "$READ_CHECK" -ne 200 ]; then
    echo "[err] failed to reset"
    exit 1
  else
    echo "[info] CPE reset success"
  fi
  echo "$VERBOSE"|grep -q "noise" && \
  curl -Lsc $CJAR -d $DATA http://192.168.1.1/wifi/macfiltering
  """

def html_state_lan():
  # fetch http://192.168.1.1/state/lan
  # we try to automate CPE ip address location and passphrase extraction
  # we also default to IPv6 and only fall back to IPv4 if we have to
  #rdfa:deps="['sudo python-configparser']"
  #import os,sys,requests,configparser
  import requests
  password = SFR_pass.fetch_pass()
  username = SFR_pass.fetch_user()
  ip_url = SFR_pass.ip_url()[1]

  LOGIN_URL = 'http://' + ip_url + '/login?page_ref=/state/lan'
  REQUEST_URL = 'http://' + ip_url + '/state/lan'
  payload = {'login': username, 'password': password }

  with requests.Session() as session:
    post = session.post(LOGIN_URL, data=payload)
    r = session.get(REQUEST_URL)
    if r is not None:
        return r.text
    else:
        reset_cmd='curl -s -G http://192.168.1.1/api/1.0/?method=auth.getToken'
        try_reset = Popen(reset_cmd, shell=True, stdout=PIPE).stdout.read()
        #do we REALLY want to set up a potential infinite loop?
        #if try_reset is not None:
        #  html_state_lan()
        # not on my watch

def dump(obj):
   for attr in dir(obj):
       if hasattr( obj, attr ):
           print( "obj.%s = %s" % (attr, getattr(obj, attr)))


def update_RRD(*args):
  if len(args) >=2:
    path = args[0]
  else:
    path = 'this'
  """
    ./fetch_SFR.sh
    ./SFR_html_state_wifi.py|grep -E '[t|r]xbyte' 
    txbyte = 768063512
    rxbyte = 3708870080
  """
  #print("check that each RRD exists, (create if missing) and update each DB for {}".format(path))
  var = SFR_config.conf_path + SFR_config.var
  # gather data
  #current_client_packets = os.popen('./fetch_SFR.sh').read().rstrip()
  DEBUG = 0
  import pickle
  DEBUG_DATA_FILE = 'DEBUG.data'
  if DEBUG >= 1 and os.path.isfile(DEBUG_DATA_FILE):
    fh = open(DEBUG_DATA_FILE, 'rb')
    current_client_packets = pickle.load(fh)
    fh.close()
  else:
    current_client_packets = fetch_client_data()
    if DEBUG >= 1:
      fh = open(DEBUG_DATA_FILE, 'wb')
      pickle.dump(current_client_packets, fh)
      fh.close()
  #import pprint
  #pp = pprint.PrettyPrinter(indent=4)
  #pp.pprint(current_client_packets)
  #pprint(current_client_packets)


  # HERE we are TRYING to reset the CPE when it locks us out
  if current_client_packets is None:
    print('[debug] resetting CPE')
    reset_CPE()
    current_client_packets = fetch_client_data()
    if current_client_packets is None:
      print('[err] reset FAILED')
      sys.exit(5)
  all_func = [
"absolute",
"derive",
"gauge",
"counter"]
  try:
    for row in current_client_packets:
      if 'packets' in current_client_packets[row]:
        #print("MACaddr: {}, Packets: {}, Uptime: {}".format(row, current_client_packets[row]['packets'], current_client_packets[row]['uptime']))
        # check for location to store RRD for this MAC address
        if not os.path.isdir('{}/{}'.format(var, row)):
           SFR_functions.mkdir('{}/{}'.format(var, row))
        if not os.path.isdir('{}/{}'.format(var, row)):
          print("[warn] we should have created {}/{}".format(var, row))
        for f in all_func:
          method_name = 'create_wifi_client_rrd_{}'.format(f)
          possibles = globals().copy()
          method = possibles.get(method_name)
          if method:
            method(row, current_client_packets[row]['packets'], current_client_packets[row]['uptime'], var=var)
            #print("updating {}: Packets: {}, Uptime: {}".format(row, current_client_packets[row]['packets'], current_client_packets[row]['uptime']))
      #else:
      #  print("Mc: {}".format(row))
    #print(current_client_packets)
  except NameError as e:
    print("[err 656] " + e.message.split("'")[1])
  except:
    e = str(sys.exc_info()[0])
    print("[err 659] " + e)
    print(current_client_packets)

def main(*args):
  update_RRD()

def test_function_from_list(*args):
  print("in main")
  all_func = [
"absolute",
"derive",
"gauge",
"counter"]

  for f in all_func:
        method_name = 'create_wifi_client_rrd_{}'.format(f)
        #possibles = locals().copy()   
        possibles = globals().copy()   
        #possibles.update(locals())  # locals() == lupus "its never lupus"
        method = possibles.get(method_name)
        #method = globals()[method_name]()
        if not method:
          print("{} not found".format(method_name))
          globals()[method_name]()
          continue #raise NotImplementedError("Method %s not implemented" % method_name)
        else:
          print("Calling {}".format(method_name))
          method()
  print("done with main")

if __name__ == '__main__':
    main()
    #import sys; sys.exit(main(sys.argv[1:])) # this also works

