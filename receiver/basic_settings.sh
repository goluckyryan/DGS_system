trigger=SumX #todo, NIM or RAM
mode=CFD
CH=7

#====== make sure 
caput Online_CS_StartStop Stop
caput Online_CS_SaveData Save

#====== MTRG settings
caput VME99:MTRG:IMP_SYNC 1
caput VME99:MTRG:IMP_SYNC 0


caput VME99:MTRG:SOFTWARE_VETO on
caput VME99:MTRG:ENBL_MON7_VETO on

caput VME99:MTRG:reg_SUM_OF_Y_THRESH 0
caput VME99:MTRG:reg_SUM_OF_X_THRESH 0

caput VME99:MTRG:EN_NIM1_DELAY N
caput VME99:MTRG:EN_SUM_X on

caput VME99:MTRG:CS_Ena Enable  #enable readout of Trigger
caput VME99:MTRG:FifoNum MAIN DATA FIFO

caput VME99:MTRG:SYSMON_ENABLE ON

caput VME99:MTRG:TRIG_MON_SEL ${trigger}

caput VME99:MTRG:reg_FIFO_RESETS 64
caput VME99:MTRG:reg_FIFO_RESETS 0

#====== digi settings

caput VME99:MDIG1:master_logic_enable Reset

if [ ${mode} == "LED" ]; then
echo "======== LED"
caput VME99:MDIG1:p1_window${CH} 0.07
caput VME99:MDIG1:p2_window${CH} 0.05
caput VME99:MDIG1:m_window${CH}  2.5
caput VME99:MDIG1:k0_window${CH} 0.5
caput VME99:MDIG1:k_window${CH}  0.5
caput VME99:MDIG1:d_window${CH}  0.16
fi

if [ ${mode} == "CFD" ]; then
echo "======== CFD"
caput VME99:MDIG1:p1_window${CH} 0.07
caput VME99:MDIG1:p2_window${CH} 0.05
caput VME99:MDIG1:m_window${CH}  2.5
caput VME99:MDIG1:k0_window${CH} 0.56
caput VME99:MDIG1:k_window${CH}  0.16  #fixed
caput VME99:MDIG1:d_window${CH}  0.1   #fixed
caput VME99:MDIG1:CFD_fraction${CH} 50
fi

caput VME99:MDIG1:trigger_polarity${CH} RiseEdge
caput VME99:MDIG1:led_threshold${CH} 30

caput VME99:MDIG1:raw_data_delay${CH} 0.5 # us
caput VME99:MDIG1:raw_data_length${CH} 4.0 # trace length, minimum 3.28

caput VME99:MDIG1:CS_Ena Enable
caput VME99:MDIG1:veto_enable 0

caput VME99:MDIG1:trigger_mux_select IntAcptAll

caput VME99:MDIG1:master_fifo_reset reset
caput VME99:MDIG1:master_fifo_reset run

caput VME99:MDIG1:master_logic_enable Enable




