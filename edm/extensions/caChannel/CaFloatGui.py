#
# filename: CaFloatGui.py
# created : 05/23/01
# author  : Geoff Savage
#
# Generic display class with data coming from EPICS channel access.
#
"""
CaFloatGui Help
#
CaFloatGui Overview
"""

from CaChannel import *
from D0Gui import D0Gui
import D0GuiDefaults
from DevFrame import *
import string
from types import *
import traceback

# names = sequence containing the device names
# attribs = sequence containing the device attributes
# column_titles = one for the names column and one for each attribute
class CaFloatGui(D0Gui):
    def __init__(self, names, attribs, column_titles, title, doc, sep='/'):
        self.ch_d = {}  # dictionary holding the CaChannel objects
        self.df_d = {}
        self.devNames = names
        self.devAttribs = attribs
        self.columnTitles = column_titles
        self.sep = sep
        D0Gui.__init__(self, title, doc)
        self.setAboutVersion('0.0')
        self.setAboutContact('DZero Controls Group')
        self.setAppName('CaFloatGui')

    # Layout the display.
    def createDataArea(self, da):
        val = '0.0'
        # Insert the column titles
        df = DevFrame(da, self.columnTitles[0])
        for i in range(1, len(self.columnTitles)):
            df.textItemAdd(str(self.columnTitles[i]))
        df.pack()
        for n in self.devNames:
            self.df_d[n] = {}
            self.df_d[n]['df'] = DevFrame(da, n)
            for a in self.devAttribs:
                pvname = n+self.sep+a
                self.df_d[n][a] = self.df_d[n]['df'].floatSevrItemAdd(pvName=pvname)
            self.df_d[n]['df'].pack()

    # Create the EPICS record names from pvnames and pvattribs.
    # Start the connection process.  For any connection change
    # we get a callback.
    def finishInit(self):
        channelNames = []
        # Combine the names and attributes into pv names
        for n in self.devNames:
            for a in self.devAttribs:
                channelNames.append(n+self.sep+a)
        # connect all the pvs
        for pvname in channelNames:
            #print pv
            self.ch_d[pvname] = {}
            self.ch_d[pvname]['chan'] = CaChannel()
            self.ch_d[pvname]['event'] = 'no'
            self.ch_d[pvname]['chan'].search_and_connect(pvname, self.connectionCallback, self.df_d, self.ch_d)
        ca.pend_event(5.0)

    def connectionCallback(self, epics_args, user_args):
        #print 'connectionCallback'
        df_d = user_args[0]
        ch_d = user_args[1]
        pvname = ca.name(epics_args[0])
        state = epics_args[1]
        l = string.split(pvname, self.sep)
        name = l[0]
        attrib = string.join(l[1:], self.sep)
        df = df_d[name]['df']
        item = df_d[name][attrib]
        if state == ca.CA_OP_CONN_UP:
            pass
            #df.update(bg = D0GuiDefaults.d0_white)
            #print 'channel connected'
        elif state == ca.CA_OP_CONN_DOWN:
            df.update(item, 0, bg = D0GuiDefaults.d0_grey)
            #print 'channel disconnected'
        chan = ch_d[pvname]['chan']
        if state == ca.CA_OP_CONN_UP and ch_d[pvname]['event'] == 'no':
            #print 'register monitor'
            field_type = chan.field_type()
            if field_type == ca.DBR_ENUM:
                field_type = ca.DBR_STRING
            chan.add_masked_array_event(
                     ca.dbf_type_to_DBR_STS(field_type),
                     chan.element_count(),
                     ca.DBE_VALUE | ca.DBE_ALARM,
                     self.monitorCallback, df_d)
            ch_d[pvname]['event'] = 'registered'

    def monitorCallback(self, epics_args, user_args):
        df_d = user_args[0]
        pvname = ca.name(epics_args['chid'])
        l = string.split(pvname, self.sep)
        name = l[0]
        attrib = string.join(l[1:], self.sep)
        df = df_d[name]['df']
        item = df_d[name][attrib]
        val = epics_args['pv_value']
        severity = epics_args['pv_severity']
        try:
            df.itemUpdate(item, (val, severity))
        except:
            traceback.print_exc()

    def poll(self):
        ca.poll()
        self.after(100, self.poll)



if __name__ == '__main__':
    pvname_t = ('CTL_PROC_62', 'CTL_PROC_16')
    pvattrib_t = ('CPU', 'MEM', 'FD')
    title_t = ('Device', 'CPU', 'MEM', 'FD')
    c = CaFloatGui(pvname_t, pvattrib_t, title_t, 'MyGui', __doc__)
    c.poll()
    c.mainloop()



