#! /bin/env python
#
# filename: ca_event_gr.py
#
# Test CaChannel monitors
#	searchw
#	add_masked_array_event
#       ca.poll
#
# Demonstrate how to change variables in the callback and
# use them at a different point in the application.  One 
# option is to use a global variable and another is to pass
# a reference to an object.  Passing a variable will not
# work because Python passes the variable to a function by 
# value.
#
# Once this program is running you must connect to 'catest'
# from a separate program.  Each time you write a new value
# to 'catest' the monitor will execute the callback.
#
# End this program with a control-C.
#

from CaChannel import *
import time
import sys

val = -25

class myclass:
    def __init__(self, x):
        self.x = x

def eventCb(epics_args, user_args):
    global val
    val = epics_args['pv_value']
    y = user_args[0]
    y.x = val
    print 'eventCb: Python callback function'
    print 'callback status =', ca.message(epics_args['status'])
    print 'value =', epics_args['pv_value'], \
          'severity =', ca.alarmSeverityString(epics_args['pv_severity']), \
          'status =',ca.alarmStatusString(epics_args['pv_status'])
    #print epics_args
    print 'HIHI limit =', epics_args['pv_upalarmlim']
    print 'HIGH limit =', epics_args['pv_upwarnlim']
    print ' LOW limit =', epics_args['pv_lowarnlim']
    print 'LOLO limit =', epics_args['pv_loalarmlim']

def main():
    global val

    y = myclass(0)
    try:
	chan = CaChannel('catest')
	chan.searchw()
        chan.putw(val)
        time.sleep(1)
	chan.add_masked_array_event(ca.dbf_type_to_DBR_GR(chan.field_type()),
				None, ca.DBE_VALUE | ca.DBE_ALARM, eventCb, y)
                                
    except CaChannelException, status: 
	print ca.message(status)
        return

    while val < 30:
        ca.poll()
        time.sleep(1)
        val = val + 10
        print 'new value =', y.x
        chan.putw(val)

main()
