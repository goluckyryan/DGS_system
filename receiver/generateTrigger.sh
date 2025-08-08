
count=$1

# Run the loop
for ((i = 1; i <= count; i++))
do
 caput VME99:MTRG:MANUAL_TRIGGER 1
 caput VME99:MTRG:MANUAL_TRIGGER 0
done
