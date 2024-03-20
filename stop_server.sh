#!/bin/bash

# 
PID=$(ps aux | grep 'Data_Storage.py' | grep -v grep | awk '{print $2}')

#
if [ -z "$PID" ]; then
    echo "Process not found, maybe stopped."
else
    kill "$PID"
    echo "Process Stopped"
fi
