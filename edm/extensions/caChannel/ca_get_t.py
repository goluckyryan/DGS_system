#! /bin/env python
#
# filename: ca_get_t.py
#
# Test for memory leaks when reading to channels.
#
# Usage:
#       Start python
#       >>> from ca_get_t import *
#       >>> pid = 1234
#       >>> l = connect_channels(1000)
#       >>> get(l)
#       >>> get_with_callback(l)
#

from CaChannel import *
from ca_conn_t import *

get_status = None

def getCb(epics_args, user_args):
    global get_status
    get_status = 'done'
    
# l = list of connected channels
def get_with_callback(l):
    global get_status
    try:
        for c in l:
	    c.array_get_callback(None, None, getCb)
	    c.flush_io()
	    while get_status == None:
	        ca.poll()
            get_status = None
    except CaChannelException, status: 
	print ca.message(status)


# l = list of connected channels
def get_type_with_callback(l, type):
    global get_status
    try:
        for c in l:
	    c.array_get_callback(type(c.field_type()), None, getCb)
	    c.flush_io()
	    while get_status == None:
	        ca.poll()
            get_status = None
    except CaChannelException, status: 
	print ca.message(status)

# l = list of connected channels
def get(l):
    try:
        for c in l:
	    c.getw()
    except CaChannelException, status: 
	print ca.message(status)

def get_status_with_callback(l):
    get_type_with_callback(l, ca.dbf_type_to_DBR_STS)

def get_time_with_callback(l):
    get_type_with_callback(l, ca.dbf_type_to_DBR_TIME)

def get_graphics_with_callback(l):
    get_type_with_callback(l, ca.dbf_type_to_DBR_GR)

def get_control_with_callback(l):
    get_type_with_callback(l, ca.dbf_type_to_DBR_CTRL)

