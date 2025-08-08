## This is the 'start run' script for use on the test stand (VME99, no detector,
## hosted by machine 'slopebox')


if [ $# -lt 2 ]; then
    arg1="$1"
    arg2=30
	
	echo "default run time 30 sec"

else
    arg1="$1"
    arg2="$2"
fi


#!/bin/bash -l
export TERM=vt100
echo " terminals" 

echo "EPICS ports:"   
echo EPICS_CA_SERVER_PORT=$EPICS_CA_SERVER_PORT
echo EPICS_CA_REPEATER_PORT=$EPICS_CA_REPEATER_PORT

source basic_settings.sh

sleep 2

#rm -rf TestStand_run$1
#xterm -T dgsReceiver -hold -geometry 157x50+0+0 -sb -sl 1000 -e "./dgsReceiver" "vme99"  "TestStand_run$1" "gtd01" "2000000000" "14" &

#rm -rf haha*
#xterm -T haha  -geometry 130x50+0+0 -sb -sl 100000 -hold -e "./dgsReceiver_Ryan" "vme99"  "haha" "gtd01" "2000000000" "14" &

#rm -rf haha*
#xterm -T haha  -geometry 150x50+0+0 -sb -sl 100000 -hold -e "./tcp_Receiver" "192.168.203.211" "9001" "XXXX$1" &
gnome-terminal --title="haha" --window --geometry=150x100+0+0 -- bash -c './tcp_Receiver 192.168.203.211 9001 data/'"$arg1"'; exec bash' &

#gnome-terminal --title="haha" --window --geometry=150x100+0+0 -- bash -c 'gdb --args ./tcp_Receiver 192.168.203.211 9001 data/'"$arg1"' --batch -ex run' &


#wait for the xterm open
sleep 2

#===== start run

caput VME99:MDIG1:master_logic_enable Enable

caput Online_CS_StartStop Start

waitTime=$arg2
echo ">>>>>>>>>>>>>> Run for $waitTime sec"
sleep $waitTime

caput Online_CS_StartStop Stop
#caput Online_CS_SaveData No Save

#caput VME99:MDIG1:master_logic_enable Reset


