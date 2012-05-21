#!/bin/bash
#
# https://github.com/timrdf/DataFAQs/blob/master/bin/datafaqs-evaluate.sh
# 
# DataFAqTs core evaluation engine: 
#   Retrieves dataset and FAqT evaluation service lists, 
#   Invokes evaluation services with dataset information, and
#   Stores the results in a datacube-like directory structure.

if [ -e datafaqs-source-me.sh ]; then
   source datafaqs-source-me.sh
fi

DATAFAQS_HOME=${DATAFAQS_HOME:?"not set; see https://github.com/timrdf/DataFAQs/wiki/Installing-DataFAQs"}
export PATH=$PATH`$DATAFAQS_HOME/bin/df-situate-paths.sh`

CSV2RDF4LOD_HOME=${CSV2RDF4LOD_HOME:?"not set; see https://github.com/timrdf/csv2rdf4lod-automation/wiki/CSV2RDF4LOD-not-set"}
export PATH=$PATH`$CSV2RDF4LOD_HOME/bin/util/cr-situate-paths.sh`

if [[ "$DATAFAQS_PUBLISH_TDB" == "true" && ! `which tdbloader` ]]; then
   if [ -d "${TDBROOT}" ]; then
      export PATH="$PATH:$TDBROOT/bin"
   else
      echo "[WARNING]: DATAFAQS_PUBLISH_TDB = true but tdbloader not on path and TDBROOT not set. Will not be able to load tdb triple store."
   fi
fi

DATAFAQS_BASE_URI=${DATAFAQS_BASE_URI:?"not set; see https://github.com/timrdf/DataFAQs/wiki/DATAFAQS-envrionment-variables"}


metadata_name=${DATAFAQS_PUBLISH_METADATA_GRAPH_NAME:-'http://www.w3.org/ns/sparql-service-description#NamedGraph'}
export DATAFAQS_LOG_DIR=${DATAFAQS_LOG_DIR:-`pwd`/log}

local="$DATAFAQS_HOME/services/sadi"
service_base='http://sparql.tw.rpi.edu/services'

faqts_input="$local/core/select-faqts/identity-materials/sample-inputs/max-1-topic-tag.ttl" # TODO: TEMP
faqts_service="$service_base/datafaqs/core/select-faqts/identity"

faqts_input="$local/core/select-faqts/via-sparql-query-materials/sample-inputs/from-official-sadi-registry.ttl"
faqts_service="$service_base/datafaqs/core/select-faqts/via-sparql-query"

datasets_input="$local/core/select-datasets/by-ckan-group-materials/sample-inputs/thedatahub-datafaqs.ttl"
datasets_service="$service_base/datafaqs/core/select-datasets/by-ckan-group"

references_service="$service_base/datafaqs/core/augment-datasets/with-preferred-uri-and-ckan-meta-void"

if [ "$1" == "--help" ]; then
   echo "usage: `basename $0` [-n] [--force-epoch | --reuse-epoch <existing-epoch>]"
   echo "`echo \`basename $0\` | sed 's/./ /g'`             [--faqts    <rdf-file> <service-uri>]"
   echo "`echo \`basename $0\` | sed 's/./ /g'`             [--datasets <rdf-file> <service-uri>]"
   echo
   echo "            -n : perform dry run (not implemented yet)."
   echo
   echo "    --datasets : override the service-uri and its input (to evaluate a different set of datasets)."
   echo "                   default service-uri: $datasets_service"
   echo "                   default input:       $datasets_input"
   echo "                   e.g.    input:       \$DATAFAQS_HOME/services/sadi/core/select-datasets/by-ckan-group-materials/sample-inputs/thedatahub-lodcloud.ttl"
   echo
   echo "       --faqts : override the service-uri and its input (to evaluate with a different set of FAqT evaluation services)."
   echo "                   default service-uri: $faqts_service"
   echo "                   default input:       $faqts_input"
   echo "                   e.g.    service-uri: $service_base/datafaqs/core/select-faqts/identity"
   echo "                   e.g.    input:       \$DATAFAQS_HOME/services/sadi/core/select-faqts/identity-materials/sample-inputs/max-1-topic-tag.ttl"
   echo
   echo " --force-epoch : force new epoch; ignore 'once per day' convention."
   echo
   echo " --reuse-epoch : reapply FAqT evaluation services to datasets in existing epoch. Takes precedence over --force-epoch."
   echo "                   e.g.:  datafaqs-evaluate.sh --reuse-epoch                           2011-Dec-21_20_22_42"
   echo "                   e.g.:  datafaqs-evaluate.sh --reuse-epoch __PIVOT_epoch/2011-Dec-21_20_22_42"
   echo "                   e.g.:  datafaqs-evaluate.sh --reuse-epoch datafaqs:latest"
   echo
   echo "environment variables required:"
   echo "  DATAFAQS_BASE_URI e.g. http://sparql.tw.rpi.edu"
   exit 0
fi

function noprotocol {
   url="$1"
   url=${url#'http://'}
   url=${url#'https://'}
   url=${url%#*} # take off fragment identifier
   echo $url
}  

# Enforce directory conventions
if [ `basename \`pwd\`` != "faqt-brick" ]; then
   echo "`basename $0` must be initiated at the faqt-brick root."
   echo "See https://github.com/timrdf/DataFAQs/wiki/FAqT-Brick"
   exit 1
fi

dryrun="false"
if [ "$1" == "-n" ]; then
   dryrun="true"
   shift
fi

force_epoch="false"
if [ "$1" == "--force-epoch" ]; then
   force_epoch="true"
   shift
fi

epoch=`date +%Y-%m-%d`
if [ "$dryrun" == "true" ]; then
   epoch="dryrun"
elif [ "$1" == "--reuse-epoch" ]; then
   if [ $# -lt 2 ]; then
      echo "[ERROR] --reuse-epoch argument must be followed by the name of an epoch, or 'datafaqs:latest'."
      echo
      $0 --help
      exit
   else
      epoch="${2#__PIVOT_epoch/}"
      shift 2
   fi 
   if [ "$epoch" == "datafaqs:latest" ]; then
      epoch=`ls -lt __PIVOT_epoch/ | grep -v "^total" | head -1 | awk '{print $NF}'`
      latest_requested=" (datafaqs:latest)"
      reusing="Reu"
   fi
   if [[ ! -e __PIVOT_epoch/$epoch || ${#epoch} -eq 0 ]]; then
      echo "[ERROR] epoch from --reuse-epoch ($epoch) does not exist: __PIVOT_epoch/$epoch"
      echo
      $0 --help
      exit
   else
      epoch_existed="true"
   fi
elif [[ -e __PIVOT_epoch/$epoch && $force_epoch == "false" ]]; then
   echo
   echo "An evaluation epoch has already been initiated today ($epoch)."
   echo "Start one tomorrow, use --force-epoch to create another one today, or use --help."
   exit 1
elif [[ -e __PIVOT_epoch/$epoch && $force_epoch == "true" ]]; then
   epoch=`date +%Y-%m-%d_%H_%M_%S`
fi

epochDir="`pwd`/__PIVOT_epoch/$epoch"
if [ ! -d $epochDir ]; then
   mkdir -p $epochDir
fi

if [ "$1" == "--faqts" ]; then
   if [ $# -lt 3 ]; then
      echo
      echo "--faqts argument must be followed by a service-uri and input." 
      exit 1
   else
      faqts_service="$2"
      faqts_input="$3" 
      shift 3
   fi 
fi

if [ "$1" == "--datasets" ]; then
   if [ "$epoch_existed" == "true" ]; then
      echo
      echo "--datasets cannot be used in conjunction with --reuse-epoch, since they compete to list the datasets to evaluate."
      echo "Replace --reuse-epoch with --force-epoch to start new epoch."
      exit 1
   fi
   if [ $# -lt 3 ]; then
      echo
      echo "--datasets argument must be followed by a service-uri and input." 
      exit 1
   else
      datasets_service="$2"
      datasets_input="$3" 
      shift 3
   fi 
fi

if [ "$DATAFAQS_PUBLISH_TDB" == "true" ]; then
   mkdir tdb &> /dev/null
   export DATAFAQS_PUBLISH_TDB_DIR=`pwd`/tdb
fi

# # # # Hard coded parameters

ACCEPT_HEADER="Accept: text/turtle; application/rdf+xml; q=0.8, text/plain; q=0.6"
ACCEPT_HEADER="Accept: text/turtle; application/x-turtle; q=0.9, application/rdf+xml; q=0.8, text/plain; q=0.6"
ACCEPT_HEADER="Accept: text/turtle; application/x-turtle; q=0.9, application/rdf+xml; q=0.8, text/plain; q=0.6, */*; q=0.4"
ACCEPT_HEADER="Accept: text/turtle,application/turtle,application/rdf+xml;q=0.8,text/plain;q=0.9,*/*;q=.5" # Alvaro-approved.
ACCEPT_HEADER="Accept: application/rdf+xml, text/rdf;q=0.6, */*;q=0.1" # This is what rapper uses.

# # # #

echo "[INFO] ${reusing-U}sing __PIVOT_epoch/$epoch $latest_requested"

if [ "$epoch_existed" != "true" ]; then

   if [ -e epoch.ttl ]; then
      rapper -q -g -o rdfxml epoch.ttl > epoch.ttl.rdf
      faqts_input=`df-core.py epoch.ttl.rdf faqt-selectors | awk '{print $2}' | head -1`
      faqts_service=`df-core.py epoch.ttl.rdf faqt-selectors | awk '{print $1}' | head -1`

      datasets_input=`df-core.py epoch.ttl.rdf dataset-selectors | awk '{print $2}' | head -1`
      datasets_service=`df-core.py epoch.ttl.rdf dataset-selectors | awk '{print $1}' | head -1`

      references_service=`df-core.py epoch.ttl.rdf dataset-referencers | head -1`
      cp epoch.ttl $epochDir/epoch.ttl
      perl -pi -e "s|_:faqtlist|<$DATAFAQS_BASE_URI/datafaqs/epoch/$epoch/config/faqt-services>|g"          $epochDir/epoch.ttl
      perl -pi -e "s|_:datasetlist|<$DATAFAQS_BASE_URI/datafaqs/epoch/$epoch/config/datasets>|g"            $epochDir/epoch.ttl
      perl -pi -e "s|_:seeAlsolist|<$DATAFAQS_BASE_URI/datafaqs/epoch/$epoch/config/dataset-references>|g"  $epochDir/epoch.ttl
      echo "<$DATAFAQS_BASE_URI/datafaqs/epoch/$epoch> a datafaqs:Epoch ."                               >> $epochDir/epoch.ttl            # epoch.ttl
      echo $metadata_name                                                                                 > $epochDir/epoch.ttl.sd_name    # epoch.ttl.sd_name
   fi

   dir="__PIVOT_epoch/$epoch"

   #echo "[INFO] Requesting FAqT services from        $faqts_service"
   #pushd $epochDir &> /dev/null; 
   #   pcurl.sh $faqts_input -n faqt-services.post &> /dev/null
   #   rapper -q `guess-syntax.sh --inspect faqt-services.post rapper` -o turtle $faqts_input                                                                    >           faqt-services.post.ttl
   #popd &> /dev/null
   #echo "curl -s -H 'Content-Type: text/turtle' -H 'Accept: text/turtle' -d @$epochDir/faqt-services.post.ttl $faqts_service"                                   > $epochDir/faqt-services.sh
   #source $epochDir/faqt-services.sh                                                                                                                            > $epochDir/faqt-services.ttl

   faqt_selectors=`df-core.py epoch.ttl.rdf faqt-selectors | awk '{print $1}' | sort -u`
   s=0 # selector
   for faqt_selector in $faqt_selectors; do
      let "s=s+1"
      mkdir -p "__PIVOT_epoch/$epoch/faqt-services/$s"
      echo "[INFO] Requesting evaluation services from $faqt_selector"
      i=0 # input to selector
      for selector_input in `df-core.py epoch.ttl.rdf faqt-selector-inputs $faqt_selector`; do
         let "i=i+1"
         mkdir -p "__PIVOT_epoch/$epoch/faqt-services/$s/$i"
         pushd    "__PIVOT_epoch/$epoch/faqt-services/$s/$i" &> /dev/null; 
            echo "[INFO]    using input: $selector_input"
            echo "pcurl.sh $selector_input -n selector-input &> /dev/null"                                                                      > get-input.sh
            echo "rapper -q \`guess-syntax.sh --inspect selector-input rapper\` -o turtle selector-input $selector_input > selector-input.ttl" >> get-input.sh
            source get-input.sh

            #echo "curl -s -H \"Content-Type: text/turtle\" -H 'Accept: text/turtle' -d @selector-input.ttl $faqt_selector > selection.ttl"     > get-selection.sh
            # TODO: selctor needs to accept conneg.
            echo "curl -s -H \"Content-Type: text/turtle\" -d @selector-input.ttl $faqt_selector > selection.ttl"                               > get-selection.sh
            source get-selection.sh
         popd &> /dev/null
      done 
   done

   for input in `find $dir/faqt-services -name "selection.ttl"`; do 
      syntax=`guess-syntax.sh --inspect $input rapper`
      if [ "${#syntax}" -gt 0 ]; then
         rapper -q -g -o turtle $input                                                                                                                         >> $epochDir/faqt-services.ttl
      else
         echo "[WARNING] Could not guess syntax of $input"
      fi
   done
   if [ `void-triples.sh $epochDir/faqt-services.ttl` -le 0 ]; then
      echo "[ERROR] No FAqT Services selected; cannot perform evaluations."
      exit 1
   fi
   rapper -q -g -o rdfxml $epochDir/faqt-services.ttl                                                                                                           > $epochDir/faqt-services.ttl.rdf 
   triples=`void-triples.sh $dir/faqt-services.ttl`
   df-epoch-metadata.py faqt-services $DATAFAQS_BASE_URI $epoch $dir/faqt-services.ttl text/turtle ${triples:-0}                                                > $epochDir/faqt-services.meta.ttl
   echo "$DATAFAQS_BASE_URI/datafaqs/epoch/$epoch/config/faqt-services"                                                                                         > $epochDir/faqt-services.ttl.sd_name
   df-core.py $epochDir/faqt-services.ttl.rdf faqt-services | grep "^http://" | sort -u                                                                         > $epochDir/faqt-services.ttl.csv
   #rm $epochDir/faqt-services.ttl.rdf



   #echo  "[INFO] Requesting datasets from             $datasets_service"
   #pushd $epochDir &> /dev/null
   #   pcurl.sh $datasets_input -n datasets.post &> /dev/null
   #   rapper -q `guess-syntax.sh --inspect datasets.post rapper` -o turtle $datasets_input                                                          >           datasets.post.ttl 
   #popd &> /dev/null

   dataset_selectors=`df-core.py epoch.ttl.rdf dataset-selectors | awk '{print $1}' | sort -u`
   s=0 # selector
   for dataset_selector in $dataset_selectors; do
      let "s=s+1"
      mkdir -p "__PIVOT_epoch/$epoch/datasets/$s"
      echo $dataset_selector > "__PIVOT_epoch/$epoch/datasets/$s/selector"
      echo "[INFO] Requesting datasets            from $dataset_selector"
      i=0 # input to selector
      for selector_input in `df-core.py epoch.ttl.rdf dataset-selector-inputs $dataset_selector`; do
         let "i=i+1"
         mkdir -p "__PIVOT_epoch/$epoch/datasets/$s/$i"
         pushd    "__PIVOT_epoch/$epoch/datasets/$s/$i" &> /dev/null; 
            echo "pcurl.sh $selector_input -n selector-input &> /dev/null"                                                                      > get-input.sh
            echo "rapper -q \`guess-syntax.sh --inspect selector-input rapper\` -o turtle selector-input $selector_input > selector-input.ttl" >> get-input.sh
            source get-input.sh

            #echo "curl -s -H \"Content-Type: text/turtle\" -H 'Accept: text/turtle' -d @selector-input.ttl $dataset_selector > selection.ttl"   > get-selection.sh
            # TODO: selector needs to accept conneg.
            echo "curl -s -H \"Content-Type: text/turtle\" -d @selector-input.ttl $dataset_selector > selection.ttl"                            > get-selection.sh
            source get-selection.sh
         popd &> /dev/null
      done 
   done

   for input in `find $dir/datasets -name "selection.ttl"`; do
      syntax=`guess-syntax.sh --inspect $input rapper`
      if [ "${#syntax}" -gt 0 ]; then
         rapper -q -g -o turtle $input                                                                                                            >> $epochDir/datasets.ttl
      else
         echo "[WARNING] Could not guess syntax of $input"
      fi
   done
   if [ `void-triples.sh $epochDir/datasets.ttl` -le 0 ]; then
      echo "[ERROR] No datasets selected; cannot perform evaluations."
      exit 1
   fi
   triples=`void-triples.sh $dir/datasets.ttl`
   df-epoch-metadata.py 'datasets' $DATAFAQS_BASE_URI $epoch $dir/datasets.ttl 'text/turtle' ${triples:-0}                                      > $epochDir/datasets.meta.ttl
   echo "$DATAFAQS_BASE_URI/datafaqs/epoch/$epoch/config/datasets"                                                                              > $epochDir/datasets.ttl.sd_name
   # Reserialize
   rapper -q -g -o rdfxml $epochDir/datasets.ttl                                                                                                > $epochDir/datasets.ttl.rdf 
   df-core.py $epochDir/datasets.ttl.rdf datasets                                                                                               > $epochDir/datasets.ttl.csv




   for dataset_referencer in `df-core.py epoch.ttl.rdf dataset-referencers`; do
      # TODO: this for loop expects just one value. It needs to be generalized to more.
      echo "[INFO] Requesting dataset references  from $dataset_referencer"
      send="$epochDir/datasets.ttl"
      mime=`guess-syntax.sh $send mime`
      rsyn=`guess-syntax.sh $send rapper`
      # TODO: they aren't accepting conneg!
      echo "curl -s -H 'Content-Type: $mime' -H 'Accept: text/turtle' -d @$send $dataset_referencer"                                          > $epochDir/dataset-references.sh
      rapper -q $rsyn -o rdfxml $send > $epochDir/datasets.ttl.rdf
      pushd $epochDir &> /dev/null
         df-core.py datasets.ttl.rdf datasets df:chunk &> /dev/null # creates dataset-references.post.1.ttl,  dataset-references.post.2.ttl in blocks of 25 
         if [ -e dataset-references.post.1.ttl ]; then
            echo
            count=0
            for post in dataset-references.post*; do let "count=count+1"; done
            total=$count
            count=0
            for post in dataset-references.post*; do
               let "count=count+1"
               echo "[INFO] Following rdfs:seeAlso references for datasets listed in $post ($count/$total)"
               #curl -s -H "Content-Type: $mime" -H 'Accept: text/turtle' -d @$post $dataset_referencer                                        >> dataset-references.ttl
               # TODO: they aren't accepting conneg!
               curl -s -H "Content-Type: $mime" -d @$post $dataset_referencer                                                                  >> b.ttl
               if [ `void-triples.sh b.ttl` -le 0 ]; then
                  echo "[WARNING] Could not find triples in response."
               else
                  cat b.ttl                                                                                                                    >> dataset-references.ttl
               fi
               rm b.ttl
            done
         else
            echo "[ERROR] $epochDir/datasets.ttl.rdf did not list any datasets."
            exit 1
         fi
      popd &> /dev/null
      # 502s: source $epochDir/dataset-references.sh                                                                                                  > $epochDir/dataset-references.ttl
      echo "$DATAFAQS_BASE_URI/datafaqs/epoch/$epoch/config/dataset-references"                                                               > $epochDir/dataset-references.ttl.sd_name
      triples=`void-triples.sh $dir/dataset-references.ttl`
      df-epoch-metadata.py dataset-references $DATAFAQS_BASE_URI $epoch $dir/dataset-references.ttl text/turtle ${triples:-0}                 > $epochDir/dataset-references.meta.ttl
      if [ `void-triples.sh b.ttl` -le 0 ]; then
         echo "[WARNING] $epochDir/dataset-references.ttl did not provide any references."
         touch                                                                                                                                  $epochDir/dataset-references.ttl.nt
      else
         rapper -q -g -o ntriples $epochDir/dataset-references.ttl | sed 's/<//g; s/>//g'                                                     > $epochDir/dataset-references.ttl.nt
      fi
      # moved to datasets.ttl above: cat $epochDir/dataset-references.ttl.nt | grep "vocab/datafaqs#WithReferences *\." | awk '{print $1}' | grep "^http://" | sort -u > $epochDir/datasets.ttl.csv
   done

   if [ "$DATAFAQS_PUBLISH_THROUGHOUT_EPOCH" == "true" ]; then
      df-load-triple-store.sh --graph `cat $epochDir/epoch.ttl.sd_name`              $epochDir/epoch.ttl                   | awk '{print "[INFO] loaded",$0,"triples"}'

      df-load-triple-store.sh --graph `cat $epochDir/faqt-services.ttl.sd_name`      $epochDir/faqt-services.ttl           | awk '{print "[INFO] loaded",$0,"triples"}'
      df-load-triple-store.sh --graph $metadata_name                                 $epochDir/faqt-services.meta.ttl      | awk '{print "[INFO] loaded",$0,"triples"}'

      df-load-triple-store.sh --graph `cat $epochDir/datasets.ttl.sd_name`           $epochDir/datasets.ttl                | awk '{print "[INFO] loaded",$0,"triples"}'
      df-load-triple-store.sh --graph $metadata_name                                 $epochDir/datasets.meta.ttl           | awk '{print "[INFO] loaded",$0,"triples"}'

      if [ -e $epochDir/dataset-references.ttl ]; then
         df-load-triple-store.sh --graph `cat $epochDir/dataset-references.ttl.sd_name` $epochDir/dataset-references.ttl      | awk '{print "[INFO] loaded",$0,"triples"}'
         df-load-triple-store.sh --graph $metadata_name                                 $epochDir/dataset-references.meta.ttl | awk '{print "[INFO] loaded",$0,"triples"}'
      fi
   fi
else
   echo "[INFO] Reusing dataset listing and descriptions from __PIVOT_epoch/$epoch"
fi

numFAqTs=`wc -l $epochDir/faqt-services.ttl.csv | awk '{print $1}'`
numDatasets=`wc -l $epochDir/datasets.ttl.csv | awk '{print $1}'`

faqtsRandom=`cat $epochDir/faqt-services.ttl.csv | randomize-line-order.py`
datasetsRandom=`cat $epochDir/datasets.ttl.csv | randomize-line-order.py`

echo
echo "[INFO] $numFAqTs FAqT services will evaluate $numDatasets datasets."
sleep 2
echo
echo "[INFO] FAqT Services:"
echo
cat $epochDir/faqt-services.ttl.csv | awk '{print "[INFO] "$0}'
echo
echo "[INFO] CKAN Datasets:"
echo
cat $epochDir/datasets.ttl.csv | awk '{print "[INFO] "$0}' 

#
# Set up the directory structure before starting.
# (can be used as a progress meter)
#
f=0 # faqt evaluation service tally
for faqt in $faqtsRandom; do

   let 'f=f+1'
   #faqtDir="__PIVOT_faqt/${faqt#'http://'}" REPLACED by noprotocol
   faqtDir="__PIVOT_faqt/`noprotocol $faqt`"
   # faqt-brick/__PIVOT_faqt/sparql.tw.rpi.edu/services/datafaqs/faqt/void-triples/__PIVOT_dataset
   mkdir -p $faqtDir/__PIVOT_dataset &> /dev/null

   # faqt-brick/__PIVOT_faqt/sparql.tw.rpi.edu/services/datafaqs/faqt/void-triples/
   echo "@prefix datafaqs: <http://purl.org/twc/vocab/datafaqs#> ."  > $faqtDir/service.ttl
   echo "<$faqt> a datafaqs:FAqTService ."                          >> $faqtDir/service.ttl                             # service.ttl
   #echo "$faqt"                                                      > $faqtDir/service.ttl.sd_name                     # service.ttl.sd_name

   # Where the dataset evaluations will be stored.
   pushd $faqtDir/__PIVOT_dataset &> /dev/null
      d=0 # dataset tally
      for dataset in $datasetsRandom; do
         let 'd=d+1'
         #datasetDir=${dataset#'http://'} REPLACED by noprotocol
         datasetDir=`noprotocol $dataset`
         # faqt-brick/__PIVOT_faqt/sparql.tw.rpi.edu/services/datafaqs/faqt/void-triples/__PIVOT_dataset/thedatahub.org/dataset/farmers-markets-geographic-data-united-states/__PIVOT_epoch/2012-01-14
         mkdir -p $datasetDir/__PIVOT_epoch/$epoch &> /dev/null
         # faqt-brick/__PIVOT_faqt/sparql.tw.rpi.edu/services/datafaqs/faqt/void-triples/__PIVOT_dataset/thedatahub.org/dataset/farmers-markets-geographic-data-united-states/
         echo "@prefix void: <http://rdfs.org/ns/void#> ."  > $datasetDir/dataset.ttl
         echo "<$dataset> a void:Dataset ."                >> $datasetDir/dataset.ttl                                   # dataset.ttl
         #echo "$dataset"                                    > $datasetDir/dataset.ttl.sd_name                           # dataset.ttl.sd_name
      done
   popd &> /dev/null
done

if [ "$epoch_existed" != "true" ]; then

   echo
   echo "[INFO] Gathering information about FAqT evaluation services."
   echo
   #
   # Gather descriptions about the FAqT services (just good to know).
   #
   f=0
   # faqt-brick/__PIVOT_epoch/2012-01-14 
   # faqt-brick/__PIVOT_faqt/sparql.tw.rpi.edu/services/datafaqs/faqt/void-triples/__PIVOT_epoch
   for faqt in $faqtsRandom; do
      let "f=f+1" 
      #faqtDir="__PIVOT_faqt/${faqt#'http://'}" REPLACED by noprotocol
      faqtDir="__PIVOT_faqt/`noprotocol $faqt`"
      echo "[INFO] ${faqtDir#'__PIVOT_faqt/'} ($f/$numFAqTs)"
      mkdir -p $faqtDir/__PIVOT_epoch/$epoch &> /dev/null
      # faqt-brick/__PIVOT_faqt/sparql.tw.rpi.edu/services/datafaqs/faqt/void-triples          
      epDir=$faqtDir/__PIVOT_epoch/$epoch
      pushd $faqtDir/__PIVOT_epoch/$epoch &> /dev/null
         pcurl.sh $faqt -n faqt-service -e ttl &> /dev/null
         $CSV2RDF4LOD_HOME/bin/util/rename-by-syntax.sh faqt-service
         rapper -q -g -o turtle $faqt > faqt-service.ttl                                                                    # faqt-service.{ttl,rdf,nt}
         echo "$DATAFAQS_BASE_URI/datafaqs/epoch/$epoch/faqt/$f" > faqt-service.ttl.sd_name                                 # faqt-service.ttl.sd_name
         triples=`void-triples.sh faqt-service.ttl`
         dump=$faqtDir/__PIVOT_epoch/$epoch/faqt-service.ttl
         df-epoch-metadata.py faqt-service $DATAFAQS_BASE_URI $epoch $faqt $f $dump text/turtle ${triples:-0} > faqt-service.meta.ttl # faqt-service.meta.ttl
         if [ "$DATAFAQS_PUBLISH_THROUGHOUT_EPOCH" == "true" ]; then
            df-load-triple-store.sh --graph `cat faqt-service.ttl.sd_name` faqt-service.ttl | awk '{print "[INFO] loaded",$0,"triples"}'
            df-load-triple-store.sh --graph $metadata_name faqt-service.meta.ttl            | awk '{print "[INFO] loaded",$0,"triples"}'
         fi
      popd &> /dev/null
   done

   echo
   echo "[INFO] Gathering information about CKAN Datasets. Will be input to FAqT evaluation services."
   echo
   #
   # Gather descriptions about the CKAN datasets (to input to the FAqT evaluation services).
   #
   d=0
   # faqt-brick/__PIVOT_epoch/2012-01-14 
   pushd $epochDir &> /dev/null
      for dataset in $datasetsRandom; do
         let "d=d+1" 
         #datasetDir=${dataset#'http://'} REPLACED by noprotocol
         datasetDir=`noprotocol $dataset`
         echo "[INFO] $datasetDir ($d/$numDatasets)"

         # Where the dataset info is stored. 
         # Becomes the input to FAqT evaluation services.
         mkdir -p __PIVOT_dataset/$datasetDir
         # faqt-brick/__PIVOT_epoch/2012-01-14/__PIVOT_dataset/thedatahub.org/dataset/farmers-markets-geographic-data-united-states/
         pushd __PIVOT_dataset/$datasetDir &> /dev/null
            echo "@prefix datafaqs: <http://purl.org/twc/vocab/datafaqs#> ."                                                 > dataset.ttl
            echo "<$dataset> a datafaqs:CKANDataset ."                                                                      >> dataset.ttl
            if [ -e $epochDir/dataset-references.ttl.nt ]; then
               cat $epochDir/dataset-references.ttl.nt | grep $dataset | grep 'http://www.w3.org/2000/01/rdf-schema#seeAlso' > references.nt
               cat references.nt | grep $dataset | grep 'http://www.w3.org/2000/01/rdf-schema#seeAlso' | awk '{print $3}'    > references.nt.csv
            else
               echo $dataset                                                                                                 > references.nt.csv
            fi
            s=0 # see also
            file="part-$s"
            echo "curl -s -L -H \"$ACCEPT_HEADER\" $dataset > $file" > get-$file.sh
            source get-$file.sh
            triples=`void-triples.sh $file`
            if [ "$triples" -gt 0 ]; then
               extension=`guess-syntax.sh --inspect $file extension`
               head -1 $file | awk '{print "   "$0}'
               mv $file $file.$extension                                                                                      # part-0
               echo a
               rapper -q -g -o turtle "$file.$extension" > post.ttl
               for reference in `cat references.nt.csv`; do
                  let 's=s+1'
                  file="part-$s"
                  echo "   $s: $reference"
                  curl -s -L -H "$ACCEPT_HEADER" $reference > "$file"
                  head -1 $file | awk '{print "      "$0}'
                  extension=`guess-syntax.sh --inspect "$file" extension`
                  #mimetype=`guess-syntax.sh --inspect "$file" mime`
                  mv $file $file.$extension                                                                                # part-{1,2,3,...}.{ttl,rdf,nt}
                  echo b
                  rapper -q -g -o turtle $file.$extension >> post.ttl                                                      # post.ttl
               done
               echo "$DATAFAQS_BASE_URI/datafaqs/epoch/$epoch/dataset/$d" > post.ttl.sd_name                                  # post.ttl.sd_name 
               triples=`void-triples.sh post.ttl`
               dump="__PIVOT_epoch/$epoch/__PIVOT_dataset/$datasetDir/post.ttl"
               df-epoch-metadata.py dataset $DATAFAQS_BASE_URI $epoch $dataset $d $dump text/turtle $triples > post.meta.ttl  # post.meta.ttl 
               if [ "$DATAFAQS_PUBLISH_THROUGHOUT_EPOCH" == "true" ]; then
                  df-load-triple-store.sh --graph `cat post.ttl.sd_name` post.ttl | awk '{print "[INFO] loaded",$0,"triples"}'
                  df-load-triple-store.sh --graph $metadata_name post.meta.ttl    | awk '{print "[INFO] loaded",$0,"triples"}'
               fi
               echo c
               rapper -q -g -o rdfxml post.ttl > post.ttl.rdf                                                                 # post.ttl.rdf
            else
               echo "[WARNING]: no triples found in $epochDir/__PIVOT_dataset/$datasetDir/$file"
            fi
         popd &> /dev/null
         echo
      done # end datasets
   popd &> /dev/null
fi

if [ "$dryrun" == "true" ]; then
   echo "[INFO] skipping (dryrun): Submitting CKAN dataset information to FAqT evaluation services."
   exit 1
fi

echo
echo "[INFO] Submitting CKAN dataset information to FAqT evaluation services. Will store responses."
echo

let "total = numDatasets * numFAqTs"
f=0 # faqt evaluation service tally
d=0 # dataset tally
e=0 # evaluation tally
# Ordering randomized to distribute load among evaluation services.
for dataset in $datasetsRandom; do
   let 'd=d+1'
   #datasetDir=${dataset#'http://'} REPLACED by noprotocol
   datasetDir=`noprotocol $dataset`
   for faqt in $faqtsRandom; do
      #faqtDir="__PIVOT_faqt/${faqt#'http://'}" REPLACED by noprotocol
      faqtDir="__PIVOT_faqt/`noprotocol $faqt`"
      let 'f=f+1'
      let 'e=e+1'
      echo "[INFO] dataset $d/$numDatasets, FAqT $f/$numFAqTs ($e/$total total)"
      echo "[INFO] $dataset"
      echo "[INFO] $faqt"
      post="`pwd`/__PIVOT_epoch/$epoch/__PIVOT_dataset/$datasetDir/post.ttl.rdf" # pwd b/c paths are variable depth
      # faqt-brick/sparql.tw.rpi.edu/services/datafaqs/faqt/void-triples/__PIVOT_dataset/thedatahub.org/dataset/farmers-markets-geographic-data-united-states/__PIVOT_epoch/2012-01-14 
      evalDir=$faqtDir/__PIVOT_dataset/$datasetDir/__PIVOT_epoch/$epoch
      pushd $evalDir &> /dev/null
         output="evaluation"
         echo "#!/bin/bash" > request.sh
         #echo curl -s -H "'Content-Type: text/turtle'" -H "'Accept: text/turtle'" -d @$post $faqt >> request.sh                            # evaluation.sh
         echo curl -s -H "'Content-Type: application/rdf+xml'" -H "'Accept: text/turtle'" -d @$post $faqt >> request.sh                     # evaluation.sh
         source request.sh > $output
         mimetype=`guess-syntax.sh --inspect $output mime`
         echo "[INFO] `du -sh evaluation | awk '{print $1}'` of $mimetype"
         rename=`$CSV2RDF4LOD_HOME/bin/util/rename-by-syntax.sh -v $output`                                                                 # evaluation.{ttl,rdf,nt}
         # Meta
         if [[ "$rename" == "$output" || "$rename" == "" ]]; then
            meta=$output.meta.ttl # There was no extension
            rename="$output"
         else
            # blah.blah.rdf -> blah.blah.meta.rdf 
            meta=`echo $rename | sed 's/\(\.[^.]*\)$/.meta\1/'` # does not append anything if there is no extension
         fi
         echo "$DATAFAQS_BASE_URI/datafaqs/epoch/$epoch/faqt/$f/dataset/$d" > $rename.sd_name                                               # evaluation.{ttl,rdf,nt}.sd_name
         dump=$evalDir/$rename
         triples=`void-triples.sh $rename`
         echo "# df-epoch-metadata.py evaluation $DATAFAQS_BASE_URI $epoch $faqt $f $dataset $d $dump ${mimetype:-.} ${triples:-0}" > $meta
         df-epoch-metadata.py evaluation $DATAFAQS_BASE_URI $epoch $faqt $f $dataset $d $dump ${mimetype:-.} ${triples:-0}         >> $meta # evaluation.{ttl,rdf,nt}.meta
         if [ "$DATAFAQS_PUBLISH_THROUGHOUT_EPOCH" == "true" ]; then
            df-load-triple-store.sh --graph `cat $rename.sd_name` $rename | awk '{print "[INFO] loaded",$0,"triples"}'
            df-load-triple-store.sh --graph $metadata_name $meta          | awk '{print "[INFO] loaded",$0,"triples"}'
         fi
      popd &> /dev/null
      echo
   done
   f=0
done

#if [ -e epoch.ttl.rdf ]; then
#   rm epoch.ttl.rdf
#fi
