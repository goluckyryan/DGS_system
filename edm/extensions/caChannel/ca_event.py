#! /bin/env python
#
# filename: ca_event.py
#
# Test CaChannel monitors
#	searchw
#	add_masked_array_event
#       ca.poll
#
# Demonstrate how to change variables in the callback and
# use them at a different point in the application.
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

def eventCb(epics_args, user_args):
    print 'eventCb: Python callback function'
    print type(epics_args)
    print epics_args
    print 'status =', ca.message(epics_args['status'])
    print 'new value =', epics_args['pv_value']
    print 'severity =', ca.alarmSeverityString(epics_args['pv_severity'])
    print 'status =',ca.alarmStatusString(epics_args['pv_status'])

def main():
    try:
	chan = CaChannel('catest')
	chan.searchw()
	chan.add_masked_array_event(ca.dbf_type_to_DBR_STS(chan.field_type()),
				None, ca.DBE_VALUE | ca.DBE_ALARM, eventCb)
                                
    except CaChannelException, status: 
	print ca.message(status)
        return

    while 1:
        ca.poll()
        time.sleep(1)

main()
