#!/bin/bash -l

#IPList=("141" "142" "143" "144" "145" "177" "178" "179" "180" "183" "181" "182")
#for ((i=0; i<${#IPList[@]}; i++)); do
#  IP="192.168.203.${IPList[$i]}" 
#  name="${IP}"
#  ID=$(ps aux | grep ${name} | grep -v grep | awk '{print $2}')
#  echo $name"---"${ID}
#  kill -9 ${ID}
#done


xargs kill -9 < pidList.txt
