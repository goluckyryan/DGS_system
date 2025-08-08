#! /bin/env python
#
# Filename: ca-gui_example.py
#
# Sample gui using D0Gui and DevFrame classes with EPICS channel access.
# 
"""
myGui Documentation
#
myGui Overview
"""
from D0Gui import *
from DevFrame import *
from CaChannel import *

class GuiChannel:
    def __init__(self, pvname):
        self.ch = CaChannel()
        self.ch.searchw(pvname)
        self.val = self.ch.getw()

    def update(self):
        self.val = self.ch.getw()

    def val(self):
        return self.val


# Storage for DevFrame and DevFrame item references
class dfo:
    def __init__(self, parent, pvname):
        self.df = DevFrame(parent, pvname)
        self.chan = GuiChannel(pvname)
        self.item1 = self.df.textItemAdd(str(self.chan.val))
        self.df.pack()

    def update(self):
        self.chan.update()
        self.df.itemUpdate(self.item1, str(self.chan.val))


# New gui class
class myGui(D0Gui):
    def __init__(self, title):
        self.lines = []
        
        # set the window title and help data
        D0Gui.__init__(self, title, __doc__)
        # Data for the about dialog
        # Must come after constructor to over ride values
        # set in constructor.
        self.setAboutVersion('X.X')
        self.setAboutContact('Your Name')
        self.setAppName('My Gui')

    # Add user widgets to the data area
    def createDataArea(self, da):
        self.lines.append(dfo(da, 'CTL_PROC_00/MEM'))

    def update(self):
        for i in (self.lines):
            i.update()
        self.after(1000, self.update)

if __name__ == '__main__':
    g = myGui('myGui')
    g.after(1000, g.update)
    g.mainloop()
