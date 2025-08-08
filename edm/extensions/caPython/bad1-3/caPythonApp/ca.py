# This file was created automatically by SWIG.
# Don't modify this file, modify the SWIG interface instead.
# This file is compatible with both classic and new-style classes.

import _ca

def _swig_setattr(self,class_type,name,value):
    if (name == "this"):
        if isinstance(value, class_type):
            self.__dict__[name] = value.this
            if hasattr(value,"thisown"): self.__dict__["thisown"] = value.thisown
            del value.thisown
            return
    method = class_type.__swig_setmethods__.get(name,None)
    if method: return method(self,value)
    self.__dict__[name] = value

def _swig_getattr(self,class_type,name):
    method = class_type.__swig_getmethods__.get(name,None)
    if method: return method(self)
    raise AttributeError,name

import types
try:
    _object = types.ObjectType
    _newclass = 1
except AttributeError:
    class _object : pass
    _newclass = 0
del types



version = _ca.version

new_chid = _ca.new_chid

free_chid = _ca.free_chid

new_evid = _ca.new_evid

free_evid = _ca.free_evid

clear_channel = _ca.clear_channel

clear_event = _ca.clear_event

field_type = _ca.field_type

element_count = _ca.element_count

name = _ca.name

puser = _ca.puser

state = _ca.state

message = _ca.message

host_name = _ca.host_name

read_access = _ca.read_access

write_access = _ca.write_access

dbr_size_n = _ca.dbr_size_n

dbr_size = _ca.dbr_size

dbr_value_size = _ca.dbr_value_size

valid_db_req = _ca.valid_db_req

invalid_db_req = _ca.invalid_db_req

dbr_text = _ca.dbr_text

dbf_text = _ca.dbf_text

dbf_type_to_DBR = _ca.dbf_type_to_DBR

dbf_type_to_DBR_STS = _ca.dbf_type_to_DBR_STS

dbf_type_to_DBR_TIME = _ca.dbf_type_to_DBR_TIME

dbf_type_to_DBR_GR = _ca.dbf_type_to_DBR_GR

dbf_type_to_DBR_CTRL = _ca.dbf_type_to_DBR_CTRL

dbr_type_is_valid = _ca.dbr_type_is_valid

dbr_type_is_plain = _ca.dbr_type_is_plain

dbr_type_is_STS = _ca.dbr_type_is_STS

dbr_type_is_TIME = _ca.dbr_type_is_TIME

dbr_type_is_GR = _ca.dbr_type_is_GR

dbr_type_is_CTRL = _ca.dbr_type_is_CTRL

alarmSeverityString = _ca.alarmSeverityString

alarmStatusString = _ca.alarmStatusString

fdmgr_start = _ca.fdmgr_start

fdmgr_pend = _ca.fdmgr_pend

task_initialize = _ca.task_initialize

task_exit = _ca.task_exit

search_and_connect = _ca.search_and_connect

search = _ca.search

array_put = _ca.array_put

put = _ca.put

bput = _ca.bput

rput = _ca.rput

array_put_callback = _ca.array_put_callback

put_callback = _ca.put_callback

array_get = _ca.array_get

get = _ca.get

bget = _ca.bget

rget = _ca.rget

get_callback = _ca.get_callback

array_get_callback = _ca.array_get_callback

add_masked_array_event = _ca.add_masked_array_event

add_array_event = _ca.add_array_event

add_event = _ca.add_event

pend_io = _ca.pend_io

test_io = _ca.test_io

pend_event = _ca.pend_event

poll = _ca.poll

flush_io = _ca.flush_io

signal = _ca.signal

SEVCHK = _ca.SEVCHK

test_event = _ca.test_event

add_fd_registration = _ca.add_fd_registration

modify_user_name = _ca.modify_user_name

modify_host_name = _ca.modify_host_name

sg_create = _ca.sg_create

sg_delete = _ca.sg_delete

sg_block = _ca.sg_block

sg_test = _ca.sg_test

sg_reset = _ca.sg_reset

sg_put = _ca.sg_put

sg_get = _ca.sg_get

captrcast = _ca.captrcast

captrvalue = _ca.captrvalue

captrset = _ca.captrset

captrcreate = _ca.captrcreate

captrfree = _ca.captrfree

captradd = _ca.captradd

captrmap = _ca.captrmap

