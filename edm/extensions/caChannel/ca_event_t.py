#! /bin/env python
#
# filename: ca_event_t.py
#
# Test for memory leaks when on event notification.
#
# Usage:
#       Start python
#       >>> from ca_event_t import *
#       >>> pid = 1234
#       >>> l = connect_channels(1000)
#       >>> start_events(l)
#       >>> ca.poll()
#       >>> ...
#

from CaChannel import *
from ca_conn_t import *

def eventCb(epics_args, user_args):
    #print 'eventCb'
    pass

# l = list of connected channels
def start_events(l):
    try:
        for c in l:
	    c.add_masked_array_event(None, None, ca.DBE_VALUE|ca.DBE_ALARM, eventCb)
	    c.flush_io()
    except CaChannelException, status: 
	print ca.message(status)

# l = list of connected channels
def stop_events(l):
    try:
        for c in l:
	    c.clear_event()
	    c.pend_io(2.0)
    except CaChannelException, status: 
	print ca.message(status)

