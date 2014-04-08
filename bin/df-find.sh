#!/bin/bash
#
#3> <> prov:specializationOf <https://github.com/timrdf/DataFAQs/blob/master/bin/df-find.sh> .

if [[ $# -eq 0 || "$1" == "--help" ]]; then
   echo
   DATASETS='datasets'
   echo "`basename $0` in <epoch> $DATASETS"                    >&2
   echo
   echo "   e.g. __PIVOT_epoch/2014-04-07/__PIVOT_dataset/datahub.io/dataset/aemet/dataset.ttl" >&2
   echo
   DATASET_EVALUATIONS='dataset evaluations'
   echo "`basename $0` in <epoch> $DATASET_EVALUATIONS"         >&2
   echo
   echo "   e.g. __PIVOT_faqt/lodcloud.tw.rpi.edu/sadi-services/named-graphs/__PIVOT_dataset/datahub.io/dataset/aemet/__PIVOT_epoch/2014-04-07" >&2
   echo
   DATASET_EVALUATION_REQUESTS='dataset evaluation requests'
   echo "`basename $0` in <epoch> $DATASET_EVALUATION_REQUESTS" >&2
   echo
   echo "   e.g. __PIVOT_faqt/lodcloud.tw.rpi.edu/sadi-services/named-graphs/__PIVOT_dataset/datahub.io/dataset/aemet/__PIVOT_epoch/2014-04-07/request.sh" >&2
   echo
   DATASETS_EVALUATED='datasets evaluated'
   echo "`basename $0` in <epoch> $DATASETS_EVALUATED"          >&2
   echo
   echo "   e.g. __PIVOT_epoch/2014-04-07/__PIVOT_dataset/datahub.io/dataset/aemet/dataset.ttl" >&2
   echo
   VALID_EVALUATIONS='valid evaluations'
   echo "`basename $0` in <epoch> $VALID_EVALUATIONS"         >&2
   echo
   echo "   e.g. " >&2
   echo
   echo
   INVALID_EVALUATIONS='invalid evaluations'
   echo "`basename $0` in <epoch> $INVALID_EVALUATIONS"         >&2
   echo
   echo "   e.g. __PIVOT_faqt/lodcloud.tw.rpi.edu/sadi-services/named-graphs/__PIVOT_dataset/datahub.io/dataset/radatana/__PIVOT_epoch/2014-04-07/evaluation" >&2
   echo
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

elif [[ "$3 $4" == "$DATASETS_EVALUATED" ]]; then
   for dir in `$0 in $epoch $DATASET_EVALUATION_REQUESTS`; do
      echo $dir
      ls $dir
   done

elif [[ "$3 $4" == "valid evaluations" ]]; then
   for dir in `$0 in $epoch $DATASET_EVALUATION_REQUESTS`; do
      echo FOUND $dir
      if [[ "`find . -maxdepth 1 -name evaluation.* | wc -l | awk '{print $1}'`" -gt 0 ]]; then
         find . -maxdepth 1 -name evaluation.*
      fi
   done

elif [[ "$3 $4" == "invalid evaluations" ]]; then
   find __PIVOT_faqt/ -name "evaluation" | grep __PIVOT_epoch/$epoch
fi
