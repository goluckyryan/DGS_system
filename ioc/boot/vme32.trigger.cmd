
## generated startup command file for %%TITLE 

cd "/DGS_system/ioc/boot"

< cdCommands

cd topbin

ld < gretDet.munch

cd top

dbLoadDatabase("dbd/gretDet.dbd",0,0)
gretDet_registerRecordDeviceDriver(pdbbase)

cd top

########## Load record instances ##################

##=============== Load Register Templates
dbLoadRecords("db/MTrigRegisters.template","CRATE=32,BOARD=MTRG")
dbLoadRecords("db/RTrigRegisters.template","CRATE=32,BOARD=RTR1")

##=============== Load Users Templates
dbLoadRecords("db/MTrigUser.template","CRATE=32,BOARD=MTRG")
dbLoadRecords("db/RTrigUser.template","CRATE=32,BOARD=RTR1")
 
##=============== Load Crate PVs used by inLoop, outLoop, and miniSender
dbLoadRecords("db/daqCrate.template","CRATE=32")

##=============== Load pre-slot readout PV
dbLoadRecords("db/daqSegment2.template","CRATE=32,BOARD=MTRG")

InitializeDaqBoardStructure()

####### Now initialize Triggers #####################
# Need to give (PortName,Card#,Slot#)
asynTrigMasterConfig1("MTRG",0,3)
asynTrigRouterConfig1("RTR1",1,4)

asynDebugConfig("DBG",0)

cd startup

asSetFilename("../db/RunProtect.asf")

##################### Run the dreaded iocInit()
iocInit()

dumpFIFO = 0

setupFIFOReader()

dbpf "VME32:MTRG:USER_PACKAGE_DATA","99"

seq &inLoop,"CRATE=32,B0=MTRG,B1=X,B2=X,B3=X,B4=X,B5=X,B6=X"  
taskDelay(100)  
seq &outLoop,"CRATE=32"
taskDelay(100)  
seq &MiniSender,"CRATE=32" 

