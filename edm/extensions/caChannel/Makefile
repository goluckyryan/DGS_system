#	Makefile for onl_apps Project - ca Directory
#
#	AUTHOR:
#
#	J. Frederick Bartlett
#	D0 Project Department
#	Particle Physics Division
#	Fermilab
#
#	CREATION DATE: 29-Jun-2000

# Variable Definitions

TOP	= ../..

# Scripts that are executed from the command line are placed in bin.
# Scripts that are imported by other scripts are placed in lib.

LFILES	+= CaChannel.py
LFILES	+= ca-gui_example.py
LFILES	+= CaGui.py
LFILES	+= CaFloatGui.py
LFILES	+= CaDisplay.py

BFILES  += ca_cb.py
BFILES  += ca_event.py
BFILES  += ca_io.py
BFILES  += ca_wait.py
BFILES  += chan_info.py

#	Common Variable Definitions

include $(ONL_MAKEFILES_DIR)/src/VarsPythonSrc.mak

# Rule Definitions

#	Common Rule Definitions

include $(ONL_MAKEFILES_DIR)/src/RulesPythonSrc.mak
