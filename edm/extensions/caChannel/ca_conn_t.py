#! /bin/env python
#
# filename: ca_conn_t.py
#
# Test for memory leaks when connecting channels.
#
# Usage:
#       Start python
#       >>> from ca_conn_t import *
#       >>> pid = 1234
#       >>> l = connect_with_callback(1000)
#       >>> del l
#       >>> l = connect_channels(1000, 'cawave')
#       >>> del l
#

from CaChannel import *
import time
import sys
import os

print 'pid =', os.getpid()

connect_status = None

def connectCb(epics_args, user_args):
    global connect_status
    connect_status = 'done'
    
# n = number of channels
def connect_with_callback(n):
    global connect_status
    l = []
    for i in range(n):
        l.append(CaChannel())

#    s = '0123456789012345678901234567890123456789'
    try:
        for c in l:
	    c.search_and_connect('cawave', connectCb)
#	    c.search_and_connect('cawave', connectCb, s)
	    c.flush_io()
	    while connect_status == None:
	        ca.poll()
            connect_status = None
    except CaChannelException, status: 
	print ca.message(status)

    return l

# n = number of channels
def connect_channels(n, pvname):
    global status
    l = []
    for i in range(n):
        l.append(CaChannel())

    try:
        for c in l:
	    c.searchw(pvname)
    except CaChannelException, status: 
	print ca.message(status)

    return l

