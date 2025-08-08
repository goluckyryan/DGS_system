#! /bin/env python

from CaChannel import *
from Tkinter import *
import sys
import signal
import time
import ca
import time

def ciao():
    print '*** Usage ***'    
    print 'callbacks.py -f <filename1> [<filename2> ....]      or'
    print 'callbacks.py -s <PVname1> [<PVname2> ....]'
    print '************* '
    sys.exit()

    
def vCallBack(eParams, uParams):
    print time.ctime(), ':', uParams[0],'Value=',  eParams['pv_value']
    return

def cCallBack(epics_args, user_args):
    pvname = ca.name(epics_args[0])
    state = epics_args[1]
    if state == ca.CA_OP_CONN_UP:
        s = 'connected'
    elif state == ca.CA_OP_CONN_DOWN:
        s = 'disconnected'
    print '%s : %s : %s' % (time.ctime(), pvname, s)


#******* main program ********

# get the names of the process variables to be monitored

if (len(sys.argv) > 1):

    mylist = []
    
# read from command line
    if (sys.argv[1] == '-s'):                     
        for n in range (2, len(sys.argv)):
            mylist.append (sys.argv[n])
            
# read from file(s)        
    elif (sys.argv[1] == '-f'):                   
        for i in range (2,len(sys.argv)):
                list00 = []
		try:
		    f = open(sys.argv[i])
		    list00 = f.readlines()
		    f.close()        
		    l=len(list00)
		    for j in range (len(list00)):
	                x = len(list00[j])
		        if (list00[j][x-1:x] == '\n'):
	                    list00[j]=list00[j][0:x-1]
                    mylist = mylist + list00
		except:
	            print "Error in opening file: ", sys.argv[i] 
    else:
        ciao()


# check for each element whether it is a true process variable and install
# callback
        
    if (len(mylist)>0):
       PVlist=[]    
       for i in range(len(mylist)):
           success = 1
           try:
               pv = CaChannel(mylist[i])
               pv.search_and_connect(mylist[i], cCallBack)
               pv.pend_event()
               #pv.searchw()
               pv.add_masked_array_event(None, 1, ca.DBE_VALUE,
                             vCallBack,mylist[i])
           except CaChannelException, code:
               print 'Ca error for: ',mylist[i],' ',ca.message(code)
               success = 0
           if (success):
               PVlist.append(pv)
       try:
           while 1:
               ca.poll()
               time.sleep(2.0)
               sys.stdout.flush()
               sys.stderr.flush()
               
       except KeyboardInterrupt:
  
           pp = len(PVlist)
           for i in range(len(PVlist)):
               p = pp-i-1
               del PVlist[p]
           print 'ByeBye!'    
           sys.exit()
      
else:
    ciao() 




