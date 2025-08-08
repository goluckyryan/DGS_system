#! /bin/env python
#-------------------------------------------------------------------
#
#  File:     CaDemo.py
#  Purpose:  Python program demo for EPICS synchronous channel access
#  Created:  June 2, 2000
#  Author:   J. Frederick Bartlett
#
#  Modified:
#-------------------------------------------------------------------
# This Python script reads the CPU utilization (%) from node d0olctl11
# every 2 seconds and displays the result as a floating value. To run
# the program, execute the following commands on node d0ola:
#
#          setup d0python
#          CaDemo.py
#
# Note that the file Demo.py must have the execute property and that
# may be set with the following command:
#
#          chmod a+x Demo.py

from CaChannel import *
import time

updatePeriod = 2.0
deviceName = 'CTL_PROC_11/CPU'

device = CaChannel()
device.searchw(deviceName)
while 1:
  value = device.getw()
  print 'CPU utilization: %4.1f%%' % value
  time.sleep(updatePeriod)
  
