#!/usr/bin/env bash
arg1=$1
arg2=$2

if [ -z "$1" ] ; then #|| [ -z "$2" ]
        echo "Missing arguments, exiting.."
        echo "Usage : $0 arg1 arg2"
        exit 1
fi
echo $1

# should run in parallel
python3 -m kalah_python.$1 &

sleep 1

java -jar ./kalah/ManKalah.jar "java -jar ./kalah/MKRefAgent.jar" "nc localhost 12345"