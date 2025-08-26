TOP=../..

include $(TOP)/configure/CONFIG
#----------------------------------------
#  ADD MACRO DEFINITIONS AFTER THIS LINE

#=============================
# Build the IOC support library

LIBRARY_IOC += dgsSoftIOCSupport

# xxxRecord.h will be created from xxxRecord.dbd
DBDINC += xxxRecord
# Install devXxxSoft.dbd into <top>/dbd
DBD += xxxSupport.dbd

# Compile and add the code to the support library
dgsSoftIOCSupport_SRCS += xxxRecord.c
dgsSoftIOCSupport_SRCS += devXxxSoft.c

# Link locally-provided code into the support library,
# rather than directly into the IOC application.
dgsSoftIOCSupport_SRCS += dbSubExample.c

dgsSoftIOCSupport_LIBS += $(EPICS_BASE_IOC_LIBS)

#=============================
# Build the IOC application

PROD_IOC = dgsSoftIOC
# dgsSoftIOC.dbd will be created and installed
DBD += dgsSoftIOC.dbd

# dgsSoftIOC.dbd will be made up from these files:
dgsSoftIOC_DBD += base.dbd
dgsSoftIOC_DBD += xxxSupport.dbd
dgsSoftIOC_DBD += dbSubExample.dbd

# dgsSoftIOC_registerRecordDeviceDriver.cpp derives from dgsSoftIOC.dbd
dgsSoftIOC_SRCS += dgsSoftIOC_registerRecordDeviceDriver.cpp

# Build the main IOC entry point on workstation OSs.
dgsSoftIOC_SRCS_DEFAULT += dgsSoftIOCMain.cpp
dgsSoftIOC_SRCS_vxWorks += -nil-

# Add support from base/src/vxWorks if needed
#dgsSoftIOC_OBJS_vxWorks += $(EPICS_BASE_BIN)/vxComLibrary

# Link in the code from the support library
dgsSoftIOC_LIBS += dgsSoftIOCSupport


# Finally link to the EPICS Base libraries
dgsSoftIOC_LIBS += $(EPICS_BASE_IOC_LIBS)

#=============================

include $(TOP)/configure/RULES
#----------------------------------------
#  ADD RULES AFTER THIS LINE

