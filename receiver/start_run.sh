#!/bin/bash -l

expName="haha"
dataType=8

if [ $# -lt 2 ]; then
  arg1="$1"
  arg2=30	
	echo "default run time 30 sec"
else
  arg1="$1"
  arg2="$2"
fi

RunID=$(printf "%03d" "$arg1")
Folder=${expName}_${RunID}
waitTime=$arg2

#source basic_settings.sh

#sleep 2

mkdir -p ${Folder}
rm -f pidList.txt

#          1     2    3      4     5     6     7     8    9     10    11   12
IPList=("141" "142" "143" "144" "145" "177" "178" "179" "180" "183" "181" "182")
for ((i=0; i<${#IPList[@]}; i++)); do
  IP="192.168.203.${IPList[$i]}" 
  name="ioc$(($i+1))-${IPList[$i]}"

  col=0
  row=$((40 + $i*200))
  if [ $i -gt 5 ]; then 
    col=750
    row=$((40 + ($i-6)*200))
  fi
  
  xterm -T ${name} -hold -geometry 120x12+${col}+$row -sb -sl 1000 -e './tcp_Receiver' ${IP} '9001'  ${dataType} "$Folder/$Folder" &

  pID=$!
  echo "$name - ${IP} - $pID"
  echo ${pID} >> pidList.txt

done

#caput VME10:MTRG:IMP_SYNC S
#caput VME10:MTRG:IMP_SYNC -

caput VME10:MTRG:CS_Ena Enable


sleep 2

#===== start run
caput Online_CS_SaveData Save #Save must do before ACQ start
caput Online_CS_StartStop Start

if [ $waitTime -gt 10 ]; then
  
  echo -e "\033[31m >>>>>>>>>>>>>> Run for $waitTime sec \033[m"
  sleep $waitTime

  caput Online_CS_StartStop Stop

  sleep 2
  caput VME10:MTRG:SOFTWARE_VETO on
  caput Online_CS_SaveData No Save

  echo -e "\033[31m run the kill_IOC.sh to kill all receiver terminals. \033[m"

else

  echo -e "\033[31m The set run-time is < 10 sec and the run will run FOERVER unit stop.\033[m"
  
fi




