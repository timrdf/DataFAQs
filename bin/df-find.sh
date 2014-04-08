#!/bin/bash
#
#3> <> prov:specializationOf <https://github.com/timrdf/DataFAQs/blob/master/bin/df-find.sh> .

if [[ $# -eq 0 || "$1" == "--help" ]]; then
   echo "`basename` in <epoch> datasets [1|2]"      >&2
   echo "`basename` in <epoch> evaluated datasets"  >&2
   echo "`basename` in <epoch> invalid evaluations" >&2
   exit
fi

epoch="${2#__PIVOT_epoch/}"

# Enforce directory conventions
#if [ `basename \`pwd\`` != "faqt-brick" ]; then
#   echo "`basename $0` must be initiated at the faqt-brick root."
#   echo "See https://github.com/timrdf/DataFAQs/wiki/FAqT-Brick"
#   exit 1
#fi

if [[ -z "$epoch" ]]; then
   echo "ERROR: epoch must be defined." >&2
   $0 --help
   exit
fi
if [[ ! -e __PIVOT_epoch/$epoch ]]; then
   echo "ERROR: epoch \"$epoch\" does not exist." >&2
   $0 --help
   exit
fi



if [[ "$3 $4" == "datasets 1" ]]; then
   find __PIVOT_epoch/$epoch -name 'dataset.ttl'

elif [[ "$3" == "datasets" ]]; then
   find __PIVOT_faqt -name "$epoch" | grep __PIVOT_dataset | grep __PIVOT_epoch/$epoch

elif [[ "$3 $4" == "evaluated datasets" ]]; then
   find __PIVOT_faqt -name "request.sh" | grep __PIVOT_epoch/$epoch

elif [[ "$3 $4" == "invalid evaluations" ]]; then
   find __PIVOT_faqt/ -name "evaluation" | grep __PIVOT_epoch/$epoch

#elif [[ "$3 $4" == "invalid evaluations" ]]; then
#   if [[ "`find . -maxdepth 1 -name epoch.* | wc -l | awk '{print $1}'`" -gt 0 ]]; then
#   fi
fi
