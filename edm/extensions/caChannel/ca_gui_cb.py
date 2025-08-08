#
# filename: ca_gui_cb.py
# created : 03/26/01
# author  : Geoff Savage
#
# General gui interface to implement channel access tests.
#
"""
CaGui Help
#
CaGui Overview
"""

from CaChannel import *
from D0Gui import D0Gui
from DevFrame import *
import string

pvnames = ('CTL_PROC_00', 'CTL_PROC_07')
pvattribs = ('CPU', 'MEM', 'FD')

class CaGui(D0Gui):
    def __init__(self):
        self.pvname = []
        D0Gui.__init__(self, 'CaGui', __doc__)
        self.setAboutVersion('X.X')
        self.setAboutContact('Your Name')
        self.setAppName('My Gui')

    def update(self):
        for n in pvnames:
            name = n+'/CPU'
            ch = self.ch_d[name]
            try:
                ch.array_get_callback(ca.dbf_type_to_DBR_STS(ch.field_type()),
                                      ch.element_count(),
                                      self.cpuCallback, self)
            except CaChannelException, status:
	        #print name+':', ca.message(status)
                pass
        ca.pend_event(0.1)
        self.after(10000, self.update)

    def cpuCallback(self, epics_args, user_args):
        if epics_args['status'] == ca.ECA_NORMAL:
            pvname = ca.name(epics_args['chid'])
            pvname_l = string.split(pvname, '/')
            this = user_args[0]
            this.processors[pvname_l[0]].cpuUpdate("%0.2f" % epics_args['pv_value'])
            #print ca.alarmSeverityString(epics_args['pv_severity'])
            #print ca.alarmStatusString(epics_args['pv_status'])
            self.pvname.append(pvname)

    def memCallback(self, epics_args, user_args):
        if epics_args['status'] == ca.ECA_NORMAL:
            pvname = ca.name(epics_args['chid'])
            pvname_l = string.split(pvname, '/')
            this = user_args[0]
            this.processors[pvname_l[0]].memUpdate("%0.2f" % epics_args['pv_value'])
            #print ca.alarmSeverityString(epics_args['pv_severity'])
            #print ca.alarmStatusString(epics_args['pv_status'])
            this.pvname.append(pvname)

    def fdCallback(self, epics_args, user_args):
        if epics_args['status'] == ca.ECA_NORMAL:
            pvname = ca.name(epics_args['chid'])
            pvname_l = string.split(pvname, '/')
            this = user_args[0]
            this.processors[pvname_l[0]].fdUpdate("%0.2f" % epics_args['pv_value'])
            #print ca.alarmSeverityString(epics_args['pv_severity'])
            #print ca.alarmStatusString(epics_args['pv_status'])

    def startInit(self):
        self.ch_d = {}
        channelNames = []
        for n in pvnames:
            for a in pvattribs:
                channelNames.append(n+'/'+a)
        for pv in channelNames:
            #print pv
            self.ch_d[pv] = CaChannel()
            self.ch_d[pv].search_and_connect(pv, self.connectionCallback)        
        ca.pend_event(1.0)

    def connectionCallback(self, epics_args, user_args):
        print ca.name(epics_args[0])

    def createDataArea(self, da):
        self.processors = {}
        pd = ProcessorDisplay(da, 'Procssor Name')
        pd.cpuUpdate('CPU')
        pd.memUpdate('MEM')
        pd.fdUpdate('FD')
        for n in pvnames:
            self.processors[n] = ProcessorDisplay(da, n)

    def poll(self):
        #ca.pend_event(0.1)
        ca.poll()
        self.after(100, self.poll)

    def process(self):
        for n in self.pvname:
            pvname_l = string.split(n, '/')
            name = pvname_l[0]
            attrib = pvname_l[1]
            if attrib == 'CPU':
                ch = self.ch_d[name+'/MEM']
                try:
                    ch.array_get_callback(ca.dbf_type_to_DBR_STS(ch.field_type()),
                                  ch.element_count(),
                                  self.memCallback, self)
                except CaChannelException, status:
                    pass
            elif attrib == 'MEM':
                ch = self.ch_d[name+'/FD']
                try:
                    ch.array_get_callback(ca.dbf_type_to_DBR_STS(ch.field_type()),
                                  ch.element_count(),
                                  self.fdCallback, self)
                except CaChannelException, status:
                    pass
        self.pvname = []
        ca.pend_event(0.1)
        self.after(100, self.process)

class ProcessorDisplay:
    def __init__(self, da, name):
        self.df = DevFrame(da, name)
        val = '0.0'
        self.cpu = self.df.textItemAdd(val)
        self.mem = self.df.textItemAdd(val)
        self.fd = self.df.textItemAdd(val)
        self.df.pack()

    def cpuUpdate(self, val):
        self.df.itemUpdate(self.cpu, str(val))

    def memUpdate(self, val):
        self.df.itemUpdate(self.mem, str(val))

    def fdUpdate(self, val):
        self.df.itemUpdate(self.fd, str(val))


if __name__ == '__main__':
    c = CaGui()
    c.update()
    c.process()
#    c.poll()
    c.mainloop()



