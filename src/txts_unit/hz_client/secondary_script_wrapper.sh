#!/bin/bash

# Start the first process
python backup.py &
  
# Start the second process
python secondary_test.py &
  
# Wait for any process to exit
wait -n
  
# Exit with status of process that exited first
exit $?