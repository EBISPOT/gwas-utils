#!/usr/bin/env bash


# Generate sleep time:
sleepTime=$(shuf -i 10-100 -n 1)

# Generate exit code:
exitStatus=0
if [[ ${sleepTime: -1} -eq 0 || ${sleepTime: -1} -eq 5 ]]; then 
    exitStatus=1;
fi

# This script doesn/t do anything. It mimics running the indexer application.
t1=$(date '+%H:%m:%S')
echo "[Info] Starting process at ${t1}"
echo "[Info] Passed parameters: $*"
echo "[Info] sleep time: ${sleepTime}"
echo "[Info] Exit code: ${exitStatus}"

sleep ${sleepTime}

t2=$(date '+%H:%m:%S')
echo "[Info] Ending process at ${t2}"

exit $exitStatus

