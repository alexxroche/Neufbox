#!/bin/sh

END="$(( $(date +%s) - ( ( $(printf "%.0f" $(date +%M)) % 5 ) * 60 + $(printf "%.0f" $(date +%S)) )  ))"
db="$(basename "$*")"
type="${db%%_*}"
rrdtool="$(which rrdtool)"
RRD_COLS=$( rrdtool info "$1"|grep ^ds|sed 's/.*\[\(.*\)\].*/\1/'|sort -u)
#RRD_TYPES=$( rrdtool info "$1"|grep type|sed 's/.* = "//'|tr -d '"'|tr ' ' '\n')

for period in hour day week month year
do
        #VDEF:${RRD_COLS}_cur=${RRD_COLS}_now,95,PERCENTNAN \
        #CDEF:${RRD_COLS}_now=0,${RRD_COLS},1,-,GT \
        $rrdtool graph network_${period}_${type}.png -s -1$period \
        -t "Network $type the last $period" -z \
        --end $END \
        -c "BACK#FFFFFF" -c "SHADEA#FFFFFF" -c "SHADEB#FFFFFF" \
        -c "MGRID#AAAAAA" -c "GRID#CCCCCC" -c "ARROW#333333" \
        -c "FONT#333333" -c "AXIS#333333" -c "FRAME#333333" \
        -h 134 -w 543 -l 0 -a PNG -v "B/s" \
        --watermark "Last updated $(date +%Y-%m-%d\ %H:%M:%S)" \
        --font WATERMARK:8 \
        "DEF:${RRD_COLS}=$db:${RRD_COLS}:AVERAGE:step=1" \
        CDEF:${RRD_COLS}_now=${RRD_COLS},0.9,GE,0,${RRD_COLS},IF \
        VDEF:${RRD_COLS}_nay=${RRD_COLS}_now,LAST \
        VDEF:${RRD_COLS}_cur=${RRD_COLS}_now,LAST \
        VDEF:${RRD_COLS}_min=${RRD_COLS},MINIMUM \
        VDEF:${RRD_COLS}_max=${RRD_COLS},MAXIMUM \
        VDEF:${RRD_COLS}_avg=${RRD_COLS},AVERAGE \
        VDEF:${RRD_COLS}_lst=${RRD_COLS},LAST \
        VDEF:${RRD_COLS}_tot=${RRD_COLS},TOTAL \
        "COMMENT:               " \
        "COMMENT:Minimum      " \
        "COMMENT:Maximum      " \
        "COMMENT:Average      " \
        "COMMENT:Current      " \
        "COMMENT:Total        \l" \
        "COMMENT:   " \
        "AREA:${RRD_COLS}_lst#EDA36220:${RRD_COLS}  " \
        "LINE0.5:${RRD_COLS}_lst#C4220050" \
        "GPRINT:${RRD_COLS}_min:%5.1lf %sB/s   " \
        "GPRINT:${RRD_COLS}_max:%5.2lf %sB/s   " \
        "GPRINT:${RRD_COLS}_nay:%5.3lf %sB/s   " \
        "GPRINT:${RRD_COLS}_lst:%5.4lf %sB/s   " \
        "GPRINT:${RRD_COLS}_tot:%5.5lf %sB   \l" \
        "AREA:${RRD_COLS}_avg#8f88:${RRD_COLS}_now  " \
        "LINE1:${RRD_COLS}_avg#0808" \
        "GPRINT:${RRD_COLS}_min:%5.1lf %sB/s   " \
        "GPRINT:${RRD_COLS}_max:%5.2lf %sB/s   " \
        "GPRINT:${RRD_COLS}_avg:%5.3lf %sB/s   " \
        "GPRINT:${RRD_COLS}_cur:%5.4lf %sB/s   " \
        "GPRINT:${RRD_COLS}_tot:%5.5lf %sB   \l" \
        "COMMENT:   " \
        > /dev/null
        #"AREA:in#8AD3F168:In   " \
        #"LINE1:in#49AEDF" \
        #"GPRINT:minin:%5.1lf %sB/s   " \
        #"GPRINT:maxin:%5.1lf %sB/s   " \
        #"GPRINT:avgin:%5.1lf %sB/s   " \
        #"GPRINT:lstin:%5.1lf %sB/s   " \
        #"GPRINT:totin:%5.1lf %sB   \l" > /dev/null
        #> /dev/null
done

