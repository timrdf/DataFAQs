#!/bin/bash

if [[ $# -lt 1 || "$1" == "--help" ]]; then
   echo "usage: `basename $0` [-n | -w] epoch [epoch...]"
   echo "-n dryrun"
   echo "-w do it"
   echo "epoch e.g. 2012-01-19 or __PIVOT_epoch/2012-01-19" 
   exit 1
fi

while [ $# -gt 0 ]; do
   if [[ ${#1} -gt 0 && ( -d "$1" || -d __PIVOT_epoch/"$1" ) ]]; then
      echo orphaning $1
      echo df-purge-orphaned-epochs.sh -w
   fi
done
