TOP=..

include $(TOP)/configure/CONFIG

LOADABLE_LIBRARY_Linux += camodule

camodule_SRCS += ca_wrap.c
USR_INCLUDES=-I$(PYTHON_DIR)/include/python2.2

#SHARED_LIBRARIES=YES

#DOCS += capython.pdf

# Override the standard in CONFIG.Host.UnixCommon so that
# the "lib" is removed from the front of the library name.
# Python doesn't recognize the "lib" prefix.
#LIBNAME = $(LIBRARY:%=%.a)
#SHRLIBNAME = $(LIBRARY)$(SHRLIB_SUFFIX)$(SHRLIB_VERSION:%=.%)

camodule_LIBS  += $(EPICS_BASE_HOST_LIBS)

ifeq ($(OS_CLASS), Linux)
INSTALL_LOADABLE_SHRLIBS += ../../lib/$(T_A)/_ca.so
endif

include $(TOP)/configure/RULES
#----------------------------------------
#  ADD RULES AFTER THIS LINE


../ca.py: ../ca.i ../ca_internal_functions.c ../ca_helper_functions.i ../captr.i
	swig -python  $<

../ca_wrap.c: ../ca.i ../ca_internal_functions.c ../ca_helper_functions.i ../captr.i 
	swig -python  $<

_ca.so : libcamodule.so
	cp $< $@
