#!/bin/bash
#
#3> <> prov:specializationOf <https://github.com/timrdf/DataFAQs/blob/master/bin/df-find.sh> .

if [[ $# -eq 0 || "$1" == "--help" ]]; then
   echo "`basename $0` in <epoch> datasets"                    >&2
   echo "   e.g. __PIVOT_epoch/2014-04-07/__PIVOT_dataset/datahub.io/dataset/2000-us-census-rdf/dataset.ttl" >&2
   echo "`basename $0` in <epoch> dataset evaluation requests" >&2
   echo "`basename $0` in <epoch> evaluated datasets"          >&2
   echo "`basename $0` in <epoch> invalid evaluations"         >&2
   exit
fi

epoch="${2#__PIVOT_epoch/}"
epoch="${epoch%/}"

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



if [[ "$3" == "datasets" ]]; then
   find __PIVOT_epoch/$epoch -name 'dataset.ttl'

elif [[ "$3 $4" == "dataset evaluations" ]]; then
   find __PIVOT_faqt -name "$epoch" | grep __PIVOT_dataset | grep __PIVOT_epoch/$epoch

elif [[ "$3 $4 $5" == "dataset evaluation requests" ]]; then
   find __PIVOT_faqt -name "request.sh" | grep __PIVOT_epoch/$epoch

elif [[ "$3 $4" == "invalid evaluations" ]]; then
   find __PIVOT_faqt/ -name "evaluation" | grep __PIVOT_epoch/$epoch

#elif [[ "$3 $4" == "invalid evaluations" ]]; then
#   if [[ "`find . -maxdepth 1 -name epoch.* | wc -l | awk '{print $1}'`" -gt 0 ]]; then
#   fi
fi
