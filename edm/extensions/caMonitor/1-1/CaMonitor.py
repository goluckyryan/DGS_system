from CaChannel import CaChannel
from CaChannel import CaChannelException
import ca
import threading

class baseEvent:
   def callback(self): pass

nullEvent = baseEvent()

def connectCb(epics_args, user_args):
   """
   this gets called if a channel connects or disconnects.  
   """
   CaConnect.connLock.acquire()
   saved_count = CaConnect.connect_count
   if user_args[0].weareConn != epics_args[1]:	# not duplicate 
      user_args[0].weareConn = epics_args[1]
      if epics_args[1] == ca.CA_OP_CONN_UP:
          print 'connected'
          CaConnect.connect_count += 1
      else:
          CaConnect.connect_count -= 1
      user_args[0].connectEvent.callback()	
   CaConnect.connLock.release()

class CaConnect(CaChannel):
   """
   This enhancement of CaChannel class adds connection handling suitable for 
   state machine use.
   """
   channel_count = 0
   connect_count = 0
   channel_dict = {}
   connLock = threading.Lock()

   def __init__(self, pvName, connectevt = nullEvent):
      CaChannel.__init__(self)
      CaConnect.channel_count += 1
      self.weareConn = ca.CA_OP_CONN_DOWN
      try:
         self.search_and_connect(pvName,connectCb,self)
         self.pend_io()
      except CaChannelException, status:
         print "CaConnect search", ca.message(status)
      self.connectEvent = connectevt

   def caConnected(self):
      """
      return true if all channels are connected
      """
      if CaConnect.channel_count == CaConnect.connect_count:	# could be zero
         return True
      else:
         return False
   
   caConnected = classmethod(caConnected)


def eventCb(epics_args, user_args):
   """
   This is what gets called when a monitor returns
   """
   user_args[0].writeSem.acquire()
   if not user_args[0].cacheInited:
      user_args[0].cacheInited = 1
   user_args[0].monCache = epics_args.copy()
   user_args[0].writeSem.release()
   user_args[0].changeEvent.callback()
   

class CaMonitor(CaConnect):
   """
   This enhancement of the CaConnect class adds monitoring 
   """

   NoValueYetException = "No value returned yet"

   def __init__(self, pvName, DBF_type, changeEvent = nullEvent, 
                                          connectEvent = nullEvent):
       CaConnect.__init__(self, pvName, connectEvent)

       self.changeEvent = changeEvent
       self.monCache = {}
       self.cacheInited = 0
       self.writeSem = threading.Lock()

       try:
          self.add_masked_array_event(
              ca.dbf_type_to_DBR_STS(DBF_type), None, 
              ca.DBE_VALUE | ca.DBE_ALARM, eventCb, self)
       except CaChannelException, status:
          print "CaMonitor connect", ca.message(status)


   def getCache(self, key = 'pv_value'):
      """
      get latest info (optionally other than value by key) from monitored PV
      """
      self.writeSem.acquire()
      if not self.cacheInited:
          self.writeSem.release()
          raise CaMonitor.NoValueYetException
      retval = self.monCache[key]
      self.writeSem.release()
      return retval

   def getStrCache(self):
      """
      for getting strings from waveform records in change callbacks
      """
      self.writeSem.acquire()
      if not self.cacheInited:
          self.writeSem.release()
          raise CaMonitor.NoValueYetException
      tempval = self.monCache['pv_value']
      self.writeSem.release()
      retval = ""
      for c in tempval:
         if c == 0:
            break
         retval += chr(c)
      return retval

