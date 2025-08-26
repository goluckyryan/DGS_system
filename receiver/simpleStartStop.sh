#!/bin/bash -l

if [ $1 -eq 1 ]; then

  caput Online_CS_SaveData Save
  caput Online_CS_StartStop Start

else

  caput Online_CS_StartStop Stop
  caput Online_CS_SaveData No Save

fi




