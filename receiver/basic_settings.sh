trigger=RAM #NIM or RAM
mode=CFD
digTrigger=IntAcptAll #IntAcptAll, ExTTCL

#####################################################
for vme in {01..12}; do

  digList=("MDIG1" "SDIG1" "MDIG2" "SDIG2")

  if [ "$vme" = "06" ] || [ "${vme}" = "10" ]; then
    digList=("MDIG1" "SDIG1")
  fi

  for dig in "${digList[@]}"; do
    echo -e "\033[31m########################### VME${vme}:${dig}\033[m"
  
    caput VME${vme}:${dig}:master_logic_enable Reset

    for CH in {5..9}; do
      if [ ${mode} == "LED" ]; then
        echo "======== LED CH:${CH}"
        caput VME${vme}:${dig}:p1_window${CH} 0.07
        caput VME${vme}:${dig}:p2_window${CH} 0.05
        caput VME${vme}:${dig}:m_window${CH}  2.5
        caput VME${vme}:${dig}:k0_window${CH} 0.5
        caput VME${vme}:${dig}:k_window${CH}  0.5
        caput VME${vme}:${dig}:d_window${CH}  0.16
      fi

      if [ ${mode} == "CFD" ]; then
        echo "======== CFD CH:${CH}"
        caput VME${vme}:${dig}:p1_window${CH} 0.07
        caput VME${vme}:${dig}:p2_window${CH} 0.05
        caput VME${vme}:${dig}:m_window${CH}  2.5
        caput VME${vme}:${dig}:k0_window${CH} 0.56
        caput VME${vme}:${dig}:k_window${CH}  0.16  #fixed
        caput VME${vme}:${dig}:d_window${CH}  0.1   #fixed
        caput VME${vme}:${dig}:CFD_fraction${CH} 50
      fi

      caput VME${vme}:${dig}:trigger_polarity${CH} RiseEdge
      caput VME${vme}:${dig}:led_threshold${CH} 30

      caput VME${vme}:${dig}:raw_data_delay${CH} 0.5 # us
      caput VME${vme}:${dig}:raw_data_length${CH} 4.0 # trace length, minimum 3.28

    done

    caput VME${vme}:${dig}:CS_Ena Enable
    caput VME${vme}:${dig}:veto_enable 0

    caput VME${vme}:${dig}:trigger_mux_select ${digTrigger}

    caput VME${vme}:${dig}:master_fifo_reset reset
    caput VME${vme}:${dig}:master_fifo_reset run

    caput VME${vme}:${dig}:master_logic_enable Enable
  done
  
done

#====== make sure 
caput Online_CS_StartStop Stop
caput Online_CS_SaveData Save

#====== MTRG settings
caput VME10:MTRG:IMP_SYNC 1
caput VME10:MTRG:IMP_SYNC 0


caput VME10:MTRG:SOFTWARE_VETO on
caput VME10:MTRG:ENBL_MON7_VETO on

caput VME10:MTRG:reg_SUM_OF_Y_THRESH 0
caput VME10:MTRG:reg_SUM_OF_X_THRESH 0

caput VME10:MTRG:EN_NIM1_DELAY N
caput VME10:MTRG:EN_SUM_X on

caput VME10:MTRG:CS_Ena Enable  #enable readout of Trigger
caput VME10:MTRG:FifoNum MAIN DATA FIFO

caput VME10:MTRG:SYSMON_ENABLE ON

caput VME10:MTRG:TRIG_MON_SEL ${trigger}

caput VME10:MTRG:reg_FIFO_RESETS 64
caput VME10:MTRG:reg_FIFO_RESETS 0



