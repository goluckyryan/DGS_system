#!/usr/bin/env python
#
# filename: chan_info.py
# created : 04/17/01
# author  : Geoff Savage
#
# Dump information on a PV or a PV field.
#
from CaChannel import *
import sys
import string

def get_value(pvname):
    try:
        pv = CaChannel(pvname)
        pv.searchw()
        return pv.getw()
    except CaChannelException, status:
        print '%s error status: %s' % (pvname, ca.message(status))
        return None

def get_string(pvname):
    try:
        pv = CaChannel(pvname)
        pv.searchw()
        return pv.getw(ca.DBR_STRING)
    except CaChannelException, status:
        print '%s error status: %s' % (pvname, ca.message(status))
        return None

def main ():
    if len (sys.argv) != 2:
        print "Usage: %s <pvname>" % sys.argv[0]
        return 1
    else:
        pvname = sys.argv[1]

    # If there is a period ('.') in the name then a specific field
    # of a record is being accessed.
    if pvname.find('.') > -1:
        try:
            pv = CaChannel(pvname)
            pv.searchw()
            print 'pvname     =', pv.name()
            print 'value      =', pv.getw()
            ft = pv.field_type()
            print 'field type = %s (%d)' % (ca.dbr_text(ft), ft)
            print 'count      =', pv.element_count()
            print 'host       =', pv.host_name()
        except CaChannelException, status:
	    print ca.message(status)
            return 1
        return 1

    desc = get_value(pvname+'.DESC')
    dtyp = get_string(pvname+'.DTYP')
    flnk = get_string(pvname+'.FLNK')
    stat = get_string(pvname+'.STAT')
    sevr = get_string(pvname+'.SEVR')
    scan = get_string(pvname+'.SCAN')

    rtyp = get_value(pvname+'.RTYP')
    #print 'rtyp = ', rtyp

    limit_records = ('ai', 'ao', 'longin', 'longout')
    input_records = ('ai', 'longin', 'bi', 'mbbi', 'mbbiDirect', 'waveform')
    output_records= ('ao', 'longout', 'bo', 'mbbo', 'mbboDirect')

    if rtyp in limit_records:
       print 'rtyp =', rtyp

    try:
        pv = CaChannel(pvname)
        pv.searchw()
        print 'pvname     =', pv.name()
        print 'value      =', pv.getw()
        ft = pv.field_type()
        print 'field type = %s (%d)' % (ca.dbr_text(ft), ft)
        print 'count      =', pv.element_count()
        print 'host       =', pv.host_name()
    except CaChannelException, status:
        print '%s error status: %s' % (pvname, ca.message(status))
        return 1
    
    print 'desc =', desc
    print 'scan =', scan
    print 'stat =', stat
    print 'sevr =', sevr
    print 'rtyp =', rtyp
    print 'dtyp =', dtyp

    if rtyp in input_records:
        inp = get_value(pvname+'.INP')
        print 'inp  =', inp

    if rtyp in output_records:
        out = get_value(pvname+'.OUT')
        print 'out  =', out

    if rtyp in limit_records:
        egu = get_value(pvname+'.EGU')
        hhsv = get_string(pvname+'.HHSV')
        hsv = get_string(pvname+'.HSV')
        lsv = get_string(pvname+'.LSV')
        llsv = get_string(pvname+'.LLSV')
        hihi = get_value(pvname+'.HIHI')
        high = get_value(pvname+'.HIGH')
        low = get_value(pvname+'.LOW')
        lolo = get_value(pvname+'.LOLO')

        print 'hihi =', hihi, ', hhsv =', hhsv
        print 'high =', high, ', hsv  =', hsv
        print 'low  =', low, ', lsv  =', lsv
        print 'lolo =', lolo, ', llsv =', llsv

    print 'flnk =', flnk

main ()
