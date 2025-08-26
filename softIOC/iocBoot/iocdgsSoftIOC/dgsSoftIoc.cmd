## Boot script for dgsSoftIOC on DFMA
## last edit MBO 20220711

## load variables that translate to various paths
< envPaths

cd ${TOP}

## Register all support components
dbLoadDatabase "dbd/dgsSoftIOC.dbd"

dgsSoftIOC_registerRecordDeviceDriver pdbbase

## Load record instances
dbLoadRecords "db/JustGlobals.db"
dbLoadRecords "db/dgsSupport.db"



cd ${TOP}/iocBoot/${IOC}
iocInit

