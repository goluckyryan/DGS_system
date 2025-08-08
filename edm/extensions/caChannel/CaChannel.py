#
# filename: CaChannel.py
# created : 07/25/99
# author  : Geoff Savage
#
# Wrapper class for EPICS channel access.
#
# 04/29/04 Geoff Savage
# The state method will now return ca.cs_never_search if one of the search
# methods has not been called.  Periodically we see segmentation faults when
# checking on the state of the channel because the search method initializes
# the underlying C data structure.
#
# 01/28/04 - Fritz Bartlett
# Changed CaChannelException to return ca.message string from __str__ method 
# 01/22/04 - Geoff Savage
# Changed CaChannelException to inherit from the built-in Exception object.
#
# 08/10/01 - Geoff Savage
# Modified how type DBR_CHAR is handled.  For channels with an
# element count of 1 it is treated as an int.  For channels with
# an element count greater than one it is treated as a sequence
# of characters.  This supports using a waveform record to pass
# a string to function that it calls.
#
# 09/10/99 - Geoff Savage: Minimized interface.
# Instead of wrapping each caPython call, wrap the most generic calls.
# Implement more specific calls in Python as needed.
#

# Get the wrapped raw channel access calls
import ca
import time
import types
import sys

ca.cs_never_search = 4

# Exception string.  CaChannelException is thrown on errors along
# with an extra parameter, the CA status of the offending action.
#CaChannelException = "CaChannelException"
class CaChannelException(Exception):
    def __init__(self, *args):
        Exception.__init__(self, *args)
        self.status = args[0]

    def __int__(self):
        return int(self.status)

    def __str__(self):
        return ca.message(self.status)

class CaChannel:
# class timeout
    ca_timeout = 1.0	# in seconds

# Conversion dictionary.  A class variable. 
    dbr_d = {}

# Initialize conversion dictionary.  This is done once on import.
#	'c_type' = used with SWIG pointer library to allocate C space
#	'convert' = used to convert Python values to match the DBR_XXXX type
# Use the C type in the SWIG pointer library:
#	CaChannel.dbr_d[dbrType]['c_type']
# Use the converter to convert Python types
#	newValue = CaChannel.dbr_d[dbrType]['convert'](value)
    dbr_d[ca.DBR_SHORT] = \
		{'c_type' : "short",	# dbr_short_t
		 'convert' : int}
    dbr_d[ca.DBR_INT] = \
		{'c_type' : "short",		# dbr_int_t = dbr_short_t
		 'convert' : int}
    dbr_d[ca.DBR_LONG] = \
		{'c_type' : "int",		# dbr_long_t
		 'convert' : int}
    dbr_d[ca.DBR_FLOAT] = \
		{'c_type': "float",		# dbr_float_t
		 'convert' : float}
    dbr_d[ca.DBR_DOUBLE] = \
		{'c_type': "double",		# dbr_double_t
		 'convert' : float}
    dbr_d[ca.DBR_CHAR] = \
		{'c_type': "char",             # treat as an 8-bit field
		 'convert' : str}
    dbr_d[ca.DBR_STRING] = \
		{'c_type': "char",
		 'convert' : str}
    dbr_d[ca.DBR_ENUM] = \
		{'c_type': "short",
		 'convert' : int}
    def __init__(self, pvname=None):
        self.pvname = pvname
	# Un-initialized channel id structure
	self.__chid = ca.new_chid()
	# Monitor event id
	self.__evid = None
	self.__timeout = None  # override g (class timeout)
        self.__conn_state = None 

    def __del__(self):
        if self.__conn_state == 'search':
            # Clear events
            if (None != self.__evid):
                self.clear_event()
                self.pend_io()
            # Clear the channel
            if (ca.state(self.__chid) == ca.cs_conn):
                ca.clear_channel(self.__chid)
                self.pend_io()
        ca.free_chid(self.__chid)

    def version(self):
        print "CaChannel, version v00-02-02"
#
# Class helper methods
#
    # Set the default timeout value.
    # Used by default if no timeout is specified where needed.
    def setTimeout(self, timeout):
	if ((timeout >= 0) or (timeout == None)):
	    self.__timeout = timeout
	else:
	    raise ValueError

    # Retrieve the default timeout value
    def getTimeout(self):
	return self.__timeout

    # Build and initialize a C array using the SWIG pointer library.
    # If EPICS array is longer than nitems the values at the
    # end will not be overwritten.
    def __build_array(self, items, nitems, req_type):
	pvals = ca.ptrcreate(CaChannel.dbr_d[req_type]['c_type'], 0, nitems)
	i = 0
	for item in items:
	    ca.ptrset(pvals, CaChannel.dbr_d[req_type]['convert'](item), i)
	    i = i + 1
	return pvals
	
    # Build and initialize a Python list from a SWIG pointer to a C array.
    def __build_list(self, pvals, nitems):
        l = []
	if(ca.DBR_CHAR == self.field_type()):
            l = ca.ptrvalue(pvals)
        else:
	    for i in range(0, nitems):
	        l.append(ca.ptrvalue(pvals, i))
	return l

    # Use the swig pointer library to allocate and initialize
    # C variables to hold the value to be written.
    def __setup_put(self, value, req_type):
        count = self.element_count()
	if(ca.DBR_STRING == req_type):
	    length = len(str(value)) + 1  # space for string terminator
 	    pval = ca.captrcreate('char', value, length)
	elif(ca.DBR_CHAR == req_type):
            # Send the value in the format you expect
            if ((isinstance(value, types.IntType)) or (isinstance(value,types.FloatType))):
                value = int(value)
                count = 1
                pval = ca.ptrcreate('int', value, count)
            else:
                if len(value) < self.element_count():
                    count = len(value)
	        length = count + 1  # space for string terminator
 	        pval = ca.ptrcreate('char', value, length)
	else:
	    if (1 == count):
		pval = ca.ptrcreate(CaChannel.dbr_d[req_type]['c_type'],
				    CaChannel.dbr_d[req_type]['convert'](value),
				    count)
	    else:
                # send a single value to an array
                if ((isinstance(value, types.IntType)) or (isinstance(value,types.FloatType))):
                    count = 1
                    val_t = (value, )
                else:
                    val_t = value
	            count = len(val_t)
		pval = self.__build_array(val_t, count, req_type)
	return count, pval

    # Use the swig pointer library to allocate C variables
    # to hold the data read.
    def __setup_get(self, req_type):
	count = self.element_count()
	if(ca.DBR_STRING == req_type):
	    pval = ca.ptrcreate('char', ' ', 1024)
	elif(ca.DBR_CHAR == req_type):
            if count == 1:
                pval = ca.ptrcreate('int', 0, count)
            else:
	        pval = ca.ptrcreate('char', ' ', count+1)
	else:
	    pval = ca.ptrcreate(CaChannel.dbr_d[req_type]['c_type'], 0, count)
	return count, pval


#
# *************** Channel access methods ***************
#

#
# Connection methods
#	search_and_connect
#	search
#	clear_channel
#

    def search_and_connect(self, pvName, callback, *user_args):
        if pvName == None:
            pvName = self.pvname
        # Need to keep a reference
        self.__connection_args = (callback, user_args)   # user_args is a tuple
    	status = ca.search_and_connect(pvName, self.__chid, 0, self.__connection_args)
	if (ca.ECA_NORMAL != status):
	    raise CaChannelException, status
        self.__conn_state = 'search'

    def search(self, pvName=None):
        if pvName == None:
            pvName = self.pvname
    	status = ca.search(pvName, self.__chid)
	if (ca.ECA_NORMAL != status):
	    raise CaChannelException, status
        self.__conn_state = 'search'

    def clear_channel(self):
	status = ca.clear_channel(self.__chid)
	if (ca.ECA_NORMAL != status):
	    raise CaChannelException, status

#
# Write methods
#	array_put
#	array_put_callback
#

    def array_put(self, value, req_type=None, count=None):
	if(None == req_type):
	    req_type = self.field_type()
	if(None == count):
	    count, pval = self.__setup_put(value, req_type) # determine count
	else:
	    dummy, pval = self.__setup_put(value, req_type) # user count
	status = ca.array_put(req_type, count, self.__chid, pval)
	ca.ptrfree(pval)
	if (ca.ECA_NORMAL != status):
	    raise CaChannelException, status

    def array_put_callback(self, value, req_type, count, callback, *user_args):
	if(None == req_type):
	    req_type = self.field_type()
	if(None == count):
	    count, pval = self.__setup_put(value, req_type) # determine count
	else:
	    dummy, pval = self.__setup_put(value, req_type) # user count
        args = (callback, user_args)
	status = ca.array_put_callback(req_type, count, self.__chid, pval, 0, args)
	ca.ptrfree(pval)
	if (ca.ECA_NORMAL != status):
	    raise CaChannelException, status

#
# Read methods
#	getValue
#	array_get
#	array_get_callback
#

    # Obtain read value after ECA_NORMAL is returned on an array_get().
    def getValue(self):
	try:
	    if(1 == self.getCount):
		retVal = ca.ptrvalue(self.getVal)
	    else:
		retVal = self.__build_list(self.getVal, self.getCount)
	    ca.ptrfree(self.getVal)
	    del self.getVal
	    del self.getCount
	    return retVal
	except NameError:
	    return None	

    # Value(s) read are placed in C variables and should not be accessed until
    # ECA_NORMAL is recived from pend_event().  Once this occurs use getValue()
    # to retrive the value(s) read.
    # SWIG pointers to the C variables are created here and used to retrieve
    # the value(s) in getValue().
    def array_get(self, req_type=None, count=None):
	if(None == req_type):
	    req_type = self.field_type()
	if(None == count):
	    self.getCount, self.getVal = self.__setup_get(req_type) # determine count
	else:
	    dummy, self.getVal = self.__setup_get(req_type) # user count
	    self.getCount = count
	status = ca.array_get(req_type, self.getCount, self.__chid, self.getVal)
	if (ca.ECA_NORMAL != status):
	    ca.ptrfree(self.getVal)
	    raise CaChannelException, status

    def array_get_callback(self, req_type, count, callback, *user_args):
	if(None == req_type):
	    req_type = self.field_type()
	if(None == count):
	    count = self.element_count()
        args = (callback, user_args)
	status = ca.array_get_callback(req_type, count, self.__chid, 0, args)
	if (ca.ECA_NORMAL != status):
	    raise CaChannelException, status

#
# Event methods
#	add_masked_array_event
#	clear_event
#

    # Creates a new event id and stores it on self.__evid.  Only one event registered
    # per CaChannel object.  If an event is already registered the event is cleared
    # before registering a new event.
    def add_masked_array_event(self, req_type, count, mask, callback, *user_args):
	if(None == req_type):
	    req_type = self.field_type()
	if(None == count):
	    count = self.element_count()
	if(None != self.__evid):
	    self.clear_event()
	    self.pend_io()
 	self.__evid = ca.new_evid()
        self.__event_args = (callback, user_args)
	status = ca.add_masked_array_event(req_type, count, self.__chid,
				0, self.__event_args, 0,0,0, self.__evid, mask)
	if (ca.ECA_NORMAL != status):
	    raise CaChannelException, status

    def clear_event(self):
	status = ca.clear_event(self.__evid)
	if (ca.ECA_NORMAL != status):
	    raise CaChannelException, status
	ca.free_evid(self.__evid)
	self.__evid = None

#
# Execute methods
#	pend_io
#	test_io
#	pend_event
#	poll
#	flush_io
#

    def pend_io(self, timeout=None):
	if timeout is None:
	    if self.__timeout is None:
		timeout = CaChannel.ca_timeout
	    else:
		timeout = self.__timeout
	status = ca.pend_io(timeout)
	if (ca.ECA_NORMAL != status):
	    raise CaChannelException, status


    def pend_event(self, timeout=None):
	if timeout is None:
	    timeout = 0.1
	status = ca.pend_event(timeout)
	return status

    def poll(self):
	status = ca.poll()
	if (ca.ECA_NORMAL != status):
	    raise CaChannelException, status

    def flush_io(self):
	status = ca.flush_io()
	if (ca.ECA_NORMAL != status):
	    raise CaChannelException, status

#
# Channel Access Macros
# Only macros that require the channel id as an argument.
#	field_type
#	element_count
#	name
#	state
#	host_name
#	read_access
#	write_access
#
    def field_type(self):
	fieldType = ca.field_type(self.__chid)
        if ca.invalid_db_req(fieldType):
            raise CaChannelException, ca.ECA_BADTYPE
        else:
            return fieldType

    def element_count(self):
        return ca.element_count(self.__chid)

    def name(self):
        return ca.name(self.__chid)

    def state(self):
        """Returns the connection state.
        
        ca.cs_never_conn = 0
        ca.cs_prev_conn = 1
        ca.cs_conn = 2
        ca.cs_closed = 3
        ca.cs_never_search = 4
        """
        if self.__conn_state == None:
            return ca.cs_never_search
        else:
            return ca.state(self.__chid)

    def host_name(self):
	return ca.host_name(self.__chid)

    def read_access(self):
	return ca.read_access(self.__chid)

    def write_access(self):
	return ca.write_access(self.__chid)

#
# Wait functions
#
# These functions wait for completion of the requested action.
#
    def searchw(self, pvName=None):
        if pvName == None:
            pvName = self.pvname
    	status = ca.search(pvName, self.__chid)
	if (ca.ECA_NORMAL != status):
	    raise CaChannelException, status
        self.__conn_state = 'search'
	if self.__timeout is None:
	    timeout = CaChannel.ca_timeout
	else:
	    timeout = self.__timeout
	status = ca.pend_io(timeout)
	if (ca.ECA_NORMAL != status):
	    raise CaChannelException, status

    def putw(self, value, req_type=None):
	if(None == req_type):
	    req_type = self.field_type()
	# strings - null terminated array of char
	# chars - null terminated char
	# values - one of a type or an array of types
        count, pval = self.__setup_put(value, req_type)
	status = ca.array_put(req_type, count, self.__chid, pval)
	if (ca.ECA_NORMAL != status):
	    ca.ptrfree(pval)
	    raise CaChannelException, status
	if self.__timeout is None:
	    timeout = CaChannel.ca_timeout
	else:
	    timeout = self.__timeout
	status = ca.pend_io(timeout)
	if (ca.ECA_NORMAL != status):
	    ca.ptrfree(pval)
	    raise CaChannelException, status
	ca.ptrfree(pval)

    def getw(self, req_type=None, count=None):
	if(None == req_type):
	    req_type = self.field_type()
	if(None == count):
	    count, pval = self.__setup_get(req_type) # determine count
	else:
	    dummy, pval = self.__setup_get(req_type) # user count
	status = ca.array_get(req_type, count, self.__chid, pval)
	if (ca.ECA_NORMAL != status):
	    ca.ptrfree(pval)
	    raise CaChannelException, status
	if self.__timeout is None:
	    timeout = CaChannel.ca_timeout
	else:
	    timeout = self.__timeout
	status = ca.pend_io(timeout)
	if (ca.ECA_NORMAL != status):
	    ca.ptrfree(pval)
	    raise CaChannelException, status
	if(1 == count):
	    value = ca.ptrvalue(pval)
	else:
	    value = self.__build_list(pval, count)
	ca.ptrfree(pval)
	return value






