#! /bin/env python
#
# filename: ca_put_t.py
#
# Test for memory leaks when writing to channels.
#
# Usage:
#       Start python
#       >>> from ca_put_t import *
#       >>> pid = 1234
#       >>> l = connect_channels(1000, 'cawave')
#       >>> put(l)
#       >>> put_with_callback(l)
#

from CaChannel import *
from ca_conn_t import *

put_status = None

def putCb(epics_args, user_args):
    global put_status
    put_status = 'done'
    
# l = list of connected channels
def put_with_callback(l):
    global put_status
    try:
        val = 0
        for c in l:
	    c.array_put_callback(val, None, None, putCb)
	    c.flush_io()
	    while put_status == None:
	        ca.poll()
            put_status = None
            val = val + 1
    except CaChannelException, status: 
	print ca.message(status)


# l = list of connected channels
def put(l):
    try:
        val = 0
        for c in l:
	    c.putw(val)
            val = val + 1
    except CaChannelException, status: 
	print ca.message(status)



