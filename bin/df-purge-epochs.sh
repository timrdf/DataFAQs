#!/bin/bash

if [[ $# -lt 1 || "$1" == "--help" ]]; then
   echo "usage: `basename $0` [-n | -w] epoch [epoch...]"
   echo "-n dryrun"
   echo "-w do it"
   echo "epoch e.g. 2012-01-19 or __PIVOT_epoch/2012-01-19" 
   exit 1
fi

dryRun="true"
if [ "$1" == "-w" ]; then
   dryRun="false"
   shift
elif [ "$1" == "-n" ]; then
   shift
else
   echo "must specify -n or -w"
   exit 1
fi

while [ $# -gt 0 ]; do
   epoch="$1"
   if [[ ${#epoch} -gt 0 && ( -d "$epoch" || -d __PIVOT_epoch/"$epoch" ) ]]; then
      echo "Purging $epoch"
      if [ "$dryRun" == "false" ]; then
         rm -rf $epoch __PIVOT_epoch/$epoch &> /dev/null
         df-purge-orphaned-epochs.sh -w
      fi
   fi
   shift
done
