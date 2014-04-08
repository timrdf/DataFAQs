#!/bin/bash
#
#3> <> prov:specializationOf <https://github.com/timrdf/DataFAQs/blob/master/bin/df-find.sh> .

DATASETS='datasets'
INVALID_DATASET_DESCRIPTIONS='invalid dataset descriptions'
DATASET_EVALUATIONS='dataset evaluations'
DATASET_EVALUATION_REQUESTS='dataset evaluation requests'
DATASETS_EVALUATED='datasets evaluated'
INCOMPLETE_EVALUATIONS='incomplete evaluations'
VALID_EVALUATIONS='valid evaluations'
INVALID_EVALUATIONS='invalid evaluations'
if [[ $# -eq 0 || "$1" == "--help" ]]; then
   echo
   echo "`basename $0` in <epoch> $DATASETS"                        >&2
   echo
   echo "   e.g. __PIVOT_epoch/2014-04-07/__PIVOT_dataset/datahub.io/dataset/aemet/dataset.ttl" >&2
   echo
   echo "`basename $0` in <epoch> $INVALID_DATASET_DESCRIPTIONS"    >&2
   echo
   echo "   e.g. " >&2
   echo
   echo "`basename $0` in <epoch> $DATASET_EVALUATIONS"             >&2
   echo
   echo "   e.g. __PIVOT_faqt/lodcloud.tw.rpi.edu/sadi-services/named-graphs/__PIVOT_dataset/datahub.io/dataset/aemet/__PIVOT_epoch/2014-04-07" >&2
   echo
   echo "`basename $0` in <epoch> $DATASET_EVALUATION_REQUESTS"     >&2
   echo
   echo "   e.g. __PIVOT_faqt/lodcloud.tw.rpi.edu/sadi-services/named-graphs/__PIVOT_dataset/datahub.io/dataset/aemet/__PIVOT_epoch/2014-04-07/request.sh" >&2
   echo
   echo "`basename $0` in <epoch> $DATASETS_EVALUATED"              >&2
   echo
   echo "   e.g. __PIVOT_epoch/2014-04-07/__PIVOT_dataset/datahub.io/dataset/aemet/dataset.ttl" >&2
   echo
   echo "`basename $0` in <epoch> $INCOMPLETE_EVALUATIONS"          >&2
   echo
   echo "   e.g. " >&2
   echo
   echo
   echo "`basename $0` in <epoch> $VALID_EVALUATIONS"               >&2
   echo
   echo "   e.g. " >&2
   echo
   echo
   echo "`basename $0` in <epoch> $INVALID_EVALUATIONS [and CLEAR]" >&2
   echo
   echo "   e.g. __PIVOT_faqt/lodcloud.tw.rpi.edu/sadi-services/named-graphs/__PIVOT_dataset/datahub.io/dataset/radatana/__PIVOT_epoch/2014-04-07/evaluation" >&2
   echo "   [and CLEAR] - remove ALL files within the evaluation directory (i.e. request.sh, evaluation*)."
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



if [[ "$3" == "$DATASETS" ]]; then
   find __PIVOT_epoch/$epoch -name 'dataset.ttl'

elif [[ "$3 $4 $5" == "$INVALID_DATASET_DESCRIPTIONS" ]]; then
   find __PIVOT_epoch/$epoch/__PIVOT_dataset/ -name "augmentation-*" -o -name "reference-*" | xargs valid-rdf.sh -v | grep "^no" | awk '{print $2}'

elif [[ "$3 $4" == "$DATASET_EVALUATIONS" ]]; then
   find __PIVOT_faqt -name "$epoch" | grep __PIVOT_dataset | grep __PIVOT_epoch/$epoch

elif [[ "$3 $4 $5" == "$DATASET_EVALUATION_REQUESTS" ]]; then
   find __PIVOT_faqt -name "request.sh" | grep __PIVOT_epoch/$epoch

elif [[ "$3 $4" == "$DATASETS_EVALUATED" ]]; then
   for dir in `$0 in $epoch $DATASET_EVALUATION_REQUESTS`; do
      echo $dir
      ls $dir
   done

elif [[ "$3 $4" == "$INCOMPLETE_EVALUATIONS" ]]; then
   for dir in `$0 in $epoch $DATASET_EVALUATIONS`; do
      find $dir -mindepth 1 -maxdepth 1
      if [[ "`find $dir -mindepth 1 -maxdepth 1 | wc -l | awk '{print $1}'`" -eq 1 ]]; then
         #pushd $dir &> /dev/null
         echo $dir
            #find . -maxdepth 1 -name 'evaluation.*'
         #   find . -mindepth 1 -maxdepth 1
         #   if [[ "$5 $6" == 'and CLEAR' ]]; then
         #      find . -mindepth 1 -maxdepth 1 | xargs rm
         #   fi
         #popd &> /dev/null
      fi
   done

elif [[ "$3 $4" == "$VALID_EVALUATIONS" ]]; then
   for sh in `$0 in $epoch $DATASET_EVALUATION_REQUESTS`; do
      dir=`dirname $sh`

      #if [[ "`find $dir -maxdepth 1 -name 'evaluation.*' | wc -l | awk '{print $1}'`" -gt 0 ]]; then
      #   # 'evaluation' was renamed to a valid RDF extension, e.g. 'evaluation.rdf'
      #   pushd $dir &> /dev/null
      #      echo $dir
      #      find . -maxdepth 1 -name 'evaluation.*'
      #   popd &> /dev/null
      #fi

      # There should only be 4 files in the evaluation directory: 
      #    request.sh, (evaluation XOR evaluation.{rdf,ttl,nt}), 
      #                                evaluation.meta.rdf, evaluation.rdf.sd_name
      find $dir -maxdepth 1 -name 'evaluation.*' | grep -v .meta. | grep -v sd_name
   done

elif [[ "$3 $4" == "$INVALID_EVALUATIONS" ]]; then
   # Alternative: find __PIVOT_faqt/ -name "evaluation" | grep __PIVOT_epoch/$epoch

   for sh in `$0 in $epoch $DATASET_EVALUATION_REQUESTS`; do
      dir=`dirname $sh`

      if [[ "`find $dir -maxdepth 1 -name 'evaluation.*' | wc -l | awk '{print $1}'`" -lt 3 ]]; then
         # 'evaluation' was renamed to a valid RDF extension, e.g. 'evaluation.rdf'
         pushd $dir &> /dev/null
            echo $dir
            #find . -maxdepth 1 -name 'evaluation.*'
            find . -mindepth 1 -maxdepth 1
            if [[ "$5 $6" == 'and CLEAR' ]]; then
               find . -mindepth 1 -maxdepth 1 | xargs rm
            fi
         popd &> /dev/null
      fi
   done
fi
