#!/usr/bin/env python
#
# filename: chan_monitor.py
# created : 10/24/03
# author  : Geoff Savage
#
# Monitor a channel from the command line.
#
from CaChannel import *
import sys
import time

def callback(epics_args, user_args):
    print epics_args
    print user_args

def main ():
    if len (sys.argv) != 2:
        print "Usage: %s <pvname>" % sys.argv[0]
        return 1
    else:
        pvname = sys.argv[1]

    try:
        pv = CaChannel(pvname)
        pv.searchw()
        pv.add_masked_array_event(None, None, ca.DBE_VALUE, callback)
        pv.pend_event()
    except CaChannelException, status:
	print ca.message(status)
        return 1

    while 1:
        ca.poll()
        time.sleep(.1)

main ()
