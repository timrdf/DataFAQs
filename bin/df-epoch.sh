#!/bin/bash
#
#3> <> prov:specializationOf <https://github.com/timrdf/DataFAQs/blob/master/bin/df-epoch.sh> .
#
# DataFAqTs core evaluation engine:
#   Retrieves dataset and FAqT evaluation service lists,
#   Invokes evaluation services with dataset information, and
#   Stores the results in a datacube-like directory structure.

if [ -e ../../datafaqs-source-me.sh ]; then
   source ../../datafaqs-source-me.sh # This could set DATAFAQS_HOME...
fi
if [ -e datafaqs-source-me.sh ]; then
   source datafaqs-source-me.sh # This could set DATAFAQS_HOME...
fi

HOME=$(cd ${0%/*} && echo ${PWD%/*})
me=$(cd ${0%/*} && echo ${PWD})/`basename $0`

# Permit the environment variable to point to a DATAFAQS_HOME that is different from this script's,
# unless it just doens't work. Then default to this script's home.
if [[ -z "$DATAFAQS_HOME" || ! -e "$DATAFAQS_HOME"/bin/df-epoch.sh ]]; then
   DATAFAQS_HOME=$HOME
fi
export PATH=$PATH`$DATAFAQS_HOME/bin/df-situate-paths.sh`

# Fall back to the CSV2RDF4LOD_HOME if this DataFAQs is part of Prizms.
prizms_home=${HOME%/}           # Avoid trailing slash.
prizms_home=${prizms_home%/*/*} # Strip two steps off end.
if [[ ( -z "$CSV2RDF4LOD_HOME" || ! -e "$CSV2RDF4LOD_HOME/bin/cr-vars.sh" ) && `basename $prizms_home` == "prizms" ]]; then
   # /home/lebot/opt/prizms/repos/DataFAQs
   #                                       -> /home/lebot/opt/prizms
   export CSV2RDF4LOD_HOME=$prizms_home/repos/csv2rdf4lod-automation
else
   CSV2RDF4LOD_HOME=${CSV2RDF4LOD_HOME:?"not set; see https://github.com/timrdf/csv2rdf4lod-automation/wiki/CSV2RDF4LOD-not-set"}
fi
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
   space=`echo \`basename $0\` | sed 's/./ /g'`
   echo "usage: `basename $0` [-n] [--force-epoch | --reuse-epoch <existing-epoch>]"
   #echo "$space             [--faqts    <rdf-file> <service-uri>]"
   #echo "$space             [--datasets <rdf-file> <service-uri>]"
   echo
   echo "            -n : Perform dry run (not implemented yet)."
   echo
   #echo "       --faqts : override the service-uri and its input (to evaluate with a different set of FAqT evaluation services)."
   #echo "                   default service-uri: $faqts_service"
   #echo "                   default input:       $faqts_input"
   #echo "                   e.g.    service-uri: $service_base/datafaqs/core/select-faqts/identity"
   #echo "                   e.g.    input:       \$DATAFAQS_HOME/services/sadi/core/select-faqts/identity-materials/sample-inputs/max-1-topic-tag.ttl"
   #echo
   #echo "    --datasets : override the service-uri and its input (to evaluate a different set of datasets)."
   #echo "                   default service-uri: $datasets_service"
   #echo "                   default input:       $datasets_input"
   #echo "                   e.g.    input:       \$DATAFAQS_HOME/services/sadi/core/select-datasets/by-ckan-group-materials/sample-inputs/thedatahub-lodcloud.ttl"
   #echo
   echo " --force-epoch : Force new epoch; ignore 'once per day' convention."
   echo
   echo " --reuse-epoch : Reapply FAqT evaluation services to datasets in existing epoch."
   echo "                 Takes precedence over --force-epoch."
   echo "                 e.g. `basename $0` --reuse-epoch               2011-Dec-21_20_22_42"
   echo "                 e.g. `basename $0` --reuse-epoch __PIVOT_epoch/2011-Dec-21_20_22_42"
   echo "                 e.g. `basename $0` --reuse-epoch datafaqs:latest"
   echo
   echo "environment variables required:"
   echo "  DATAFAQS_BASE_URI e.g. http://sparql.tw.rpi.edu (currently $DATAFAQS_BASE_URI)"
   exit
fi

function noprotocolnohash {
   url="$1"
   url=${url#'http://'}
   url=${url#'https://'}
   url=${url%#*} # take off fragment identifier
   echo $url
}

function noprotocol {
   url="$1"
   url=${url#'http://'}
   url=${url#'https://'}
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
ACCEPT_HEADER="Accept: application/rdf+xml, text/turtle, text/n3, application/xhtml+xml; q=0.9, text/html; q=0.8, text/plain; q=0.6, */*" # http://sindice.com/developers/publishing
ACCEPT_HEADER="Accept: text/turtle,application/turtle,application/rdf+xml;q=0.8,text/plain;q=0.7,*/*;q=0.5"                               # Alvaro-approved.
ACCEPT_HEADER="Accept: application/rdf+xml, text/rdf;q=0.6, */*;q=0.1"                                                                    # This is what rapper uses.

# # # #

echo "[INFO] - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -"
echo "[INFO] - - - - - - - - - - - - - - - - Determining epoch configuration - - - - - - - - - - - - - - - - - -"

#
#
# Gather list of FAqT services and list of datasets.
#
#

echo "[INFO] ${reusing-U}sing __PIVOT_epoch/$epoch $latest_requested"

if [ "$epoch_existed" != "true" ]; then

   if [ -e epoch.ttl ]; then
      echo $metadata_name                                                                                 > $epochDir/epoch.ttl.sd_name
      cp epoch.ttl                                                                                          $epochDir/epoch.ttl
      perl -pi -e "s|_:faqtlist|<$DATAFAQS_BASE_URI/datafaqs/epoch/$epoch/config/faqt-services>|g"          $epochDir/epoch.ttl
      perl -pi -e "s|_:datasetlist|<$DATAFAQS_BASE_URI/datafaqs/epoch/$epoch/config/datasets>|g"            $epochDir/epoch.ttl
      perl -pi -e "s|_:seeAlsolist|<$DATAFAQS_BASE_URI/datafaqs/epoch/$epoch/config/dataset-references>|g"  $epochDir/epoch.ttl
      # TODO: _:augmentateddataset needs to be replaced with a URI.
      echo "<$DATAFAQS_BASE_URI/datafaqs/epoch/$epoch> a datafaqs:Epoch ."                               >> $epochDir/epoch.ttl
      rapper -q -g -o rdfxml epoch.ttl                                                                    > $epochDir/epoch.ttl.rdf

        faqts_input=`df-core.py $epochDir/epoch.ttl.rdf faqt-selectors | awk '{print $2}' | head -1`
      faqts_service=`df-core.py $epochDir/epoch.ttl.rdf faqt-selectors | awk '{print $1}' | head -1`
      # NOTE: These one-only variables are DEPRECATED in favor of the multiple-input to multiple-selectors done below.
        datasets_input=`df-core.py $epochDir/epoch.ttl.rdf dataset-selectors | awk '{print $2}' | head -1`
      datasets_service=`df-core.py $epochDir/epoch.ttl.rdf dataset-selectors | awk '{print $1}' | head -1`

      #echo
      #echo "[INFO] FAqTs selection:"
      #echo $faqts_input
      #echo "  ^---< $faqts_service"
      #echo
      #echo "[INFO] Dataset selection:"
      #echo $datasets_input
      #echo "  ^---< $datasets_service"

      # Referencers accept POSTs of the dataset and annotate with rdfs:seeAlso that should be requested.
      df-core.py $epochDir/epoch.ttl.rdf dataset-referencers                                              > $epochDir/referencers.csv
      # Augmenters accept POSTs of the dataset and annotate directly.
      df-core.py $epochDir/epoch.ttl.rdf dataset-augmenters                                               > $epochDir/augmenters.csv
      #echo
      #echo "[INFO] Referencers:"
      #cat $epochDir/referencers.csv
      #echo
      #echo "[INFO] Augmenters:"
      #cat $epochDir/augmenters.csv
      #echo
   fi

   dir="__PIVOT_epoch/$epoch" # This is relative, $epochDir is absolute

   #
   # Select FAqT evaluation services (using multiple inputs to multiple selectors)
   #
   faqt_selectors=`df-core.py $epochDir/epoch.ttl.rdf faqt-selectors | awk '{print $1}' | sort -u`
   s=0 # selector
   for faqt_selector in $faqt_selectors; do
      let "s=s+1"
      echo "[INFO] Requesting evaluation services from $faqt_selector (#$s)"
      mkdir -p "__PIVOT_epoch/$epoch/faqt-services/$s"
      echo $faqt_selector > __PIVOT_epoch/$epoch/faqt-services/$s/selector
      i=0 # input to selector
      for selector_input in `df-core.py $epochDir/epoch.ttl.rdf faqt-selector-inputs $faqt_selector`; do
         let "i=i+1"
         mkdir -p "__PIVOT_epoch/$epoch/faqt-services/$s/$i"
         pushd    "__PIVOT_epoch/$epoch/faqt-services/$s/$i" &> /dev/null;
            echo $selector_input > input.url
            echo "[INFO]    using input:                     $selector_input (#$i)"
            echo "pcurl.sh $selector_input -n selector-input &> /dev/null"                                                                      > get-selector-input.sh
            echo "rapper -q \`guess-syntax.sh --inspect selector-input rapper\` -o turtle selector-input $selector_input > selector-input.ttl" >> get-selector-input.sh
            source get-selector-input.sh

            # TODO: selector needs to accept conneg. (add -H Accept back in)
            echo "curl -s -H \"Content-Type: text/turtle\" -d @selector-input.ttl $faqt_selector > faqt-services.ttl"                           > select.sh
            source select.sh                                                                                                      # <- creates    faqt-services.ttl
         popd &> /dev/null
      done
   done
   echo "$DATAFAQS_BASE_URI/datafaqs/epoch/$epoch/config/faqt-services"                                                                 > $epochDir/faqt-services.ttl.sd_name
   # Aggregate all valid FAqT evaluation service listings.
   for input in `find $dir/faqt-services -name "faqt-services.ttl"`; do
      if [ `void-triples.sh $input` -gt 0 ]; then
         rapper -q -g -o turtle $input                                                                                                 >> $epochDir/faqt-services.ttl
      else
         echo "[WARNING] Could not guess syntax of $input"
      fi
   done
   if [ `void-triples.sh $epochDir/faqt-services.ttl` -le 0 ]; then
      echo "[ERROR] No FAqT Services selected; cannot perform evaluations."
      exit 1
   fi
   triples=`void-triples.sh $dir/faqt-services.ttl`
   df-epoch-metadata.py faqt-services $DATAFAQS_BASE_URI $epoch $dir/faqt-services.ttl text/turtle ${triples:-0}                             > $epochDir/faqt-services.meta.ttl
   rapper -q -g -o rdfxml $epochDir/faqt-services.ttl                                                                                        > $epochDir/faqt-services.ttl.rdf
   df-core.py $epochDir/faqt-services.ttl.rdf faqt-services | grep "^http://" | sort -u                                                      > $epochDir/faqt-services.ttl.csv


   # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
   # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 


   #
   # Select datasets to evaluate (using multiple inputs to multiple selectors)
   #
   dataset_selectors=`df-core.py $epochDir/epoch.ttl.rdf dataset-selectors | awk '{print $1}' | sort -u`
   s=0 # selector
   for dataset_selector in $dataset_selectors; do
      let "s=s+1"
      echo "[INFO] Requesting datasets            from $dataset_selector (#$s)"
      mkdir -p "__PIVOT_epoch/$epoch/datasets/$s"
      echo $dataset_selector > "__PIVOT_epoch/$epoch/datasets/$s/selector"
      i=0 # input to selector
      for selector_input in `df-core.py $epochDir/epoch.ttl.rdf dataset-selector-inputs $dataset_selector`; do
         let "i=i+1"
         mkdir -p "__PIVOT_epoch/$epoch/datasets/$s/$i"
         pushd    "__PIVOT_epoch/$epoch/datasets/$s/$i" &> /dev/null;
            echo "[INFO]    using input:                     $selector_input (#$i)"
            echo $selector_input > input.url
            echo "pcurl.sh $selector_input -n selector-input &> /dev/null"                                                                         > get-selector-input.sh
            if [[ "$selector_input" =~ https ]]; then
               # http://carnivore.it/2011/10/07/error_14077458_ssl_routines_ssl23_get_server_hello_reason_1112
               echo "curl -sL --sslv3 \"$selector_input\" > selector-input"                                                                       >> get-selector-input.sh
               echo "rdf2ttl.sh selector-input > selector-input.ttl"                                                                              >> get-selector-input.sh
            else
               echo "rapper -q \`guess-syntax.sh --inspect selector-input rapper\` -o turtle selector-input $selector_input > selector-input.ttl" >> get-selector-input.sh
            fi
            source get-selector-input.sh

            #echo "curl -s -H \"Content-Type: text/turtle\" -H 'Accept: text/turtle' -d @selector-input.ttl $dataset_selector > datasets.ttl"   > select.sh
            # TODO: selector needs to accept conneg.
            echo "curl -s -H \"Content-Type: text/turtle\" -d @selector-input.ttl $dataset_selector > datasets.ttl"                             > select.sh
            source select.sh                                                                                                       # <- creates   datasets.ttl
         popd &> /dev/null
      done
   done
   echo "$DATAFAQS_BASE_URI/datafaqs/epoch/$epoch/config/datasets"                                                                            > $epochDir/datasets.ttl.sd_name
   # Aggregate all valid dataset listings.
   for input in `find $dir/datasets -name "datasets.ttl"`; do
      if [ `void-triples.sh $input` -gt 0 ]; then
         rapper -q -g -o turtle $input                                                                                                        >> $epochDir/datasets.ttl
      else
         echo "[WARNING] Could not guess syntax of $input"
      fi
   done
   if [ `void-triples.sh $epochDir/datasets.ttl` -le 0 ]; then
      echo "[ERROR] No datasets selected; cannot perform evaluations."
      exit 1
   fi
   triples=`void-triples.sh $dir/datasets.ttl`
   df-epoch-metadata.py 'datasets' $DATAFAQS_BASE_URI $epoch $dir/datasets.ttl 'text/turtle' ${triples:-0}                                       > $epochDir/datasets.meta.ttl
   # Reserialize
   rapper -q -g -o rdfxml $epochDir/datasets.ttl                                                                                                 > $epochDir/datasets.ttl.rdf
   df-core.py $epochDir/datasets.ttl.rdf datasets                                                                                                > $epochDir/datasets.ttl.csv


   # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
   # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 


   #
   # Extract s-p-DATASET-p-o graphs about each selected dataset (for posting to Augmenters).
   #
   # faqt-brick/__PIVOT_epoch/2012-05-22
   pushd $epochDir &> /dev/null
      df-core.py $epochDir/datasets.ttl.rdf datasets df:individual                                                                 # <- creates   dataset.ttl
      # ^- - - - creates faqt-brick/__PIVOT_epoch/2012-06-12/__PIVOT_dataset/thedatahub.org/dataset/farmers-markets-geographic-data-united-states/dataset.ttl
      #                  faqt-brick/__PIVOT_epoch/2012-06-12/__PIVOT_dataset/thedatahub.org/dataset/lobd/dataset.ttl
      #                  faqt-brick/__PIVOT_epoch/2012-06-12/__PIVOT_dataset/thedatahub.org/dataset/.../dataset.ttl
      #                  faqt-brick/__PIVOT_epoch/2012-06-12/__PIVOT_dataset/.../dataset/.../dataset.ttl
      # for each dcat:Dataset.
   popd &> /dev/null


   #
   # Dataset references. TODO: Is this necessary now that the datasets determine their own references with get-references-0.sh?
   #
   #for dataset_referencer in `cat $epochDir/referencers.csv`; do       # TODO: This for loop expects just one value. It needs to be generalized to more.
   #   # ^ e.g. http://aquarius.tw.rpi.edu/projects/datafaqs/services/sadi/core/augment-datasets/with-preferred-uri-and-ckan-meta-void
   #   echo "[INFO] Requesting dataset references  from $dataset_referencer"
   #   send="$epochDir/datasets.ttl"
   #   mime=`guess-syntax.sh $send mime`
   #   rsyn=`guess-syntax.sh $send rapper`
   #   # TODO: they aren't accepting conneg!
   #   echo "curl -s -H 'Content-Type: $mime' -H 'Accept: text/turtle' -d @$send $dataset_referencer"                                        > $epochDir/dataset-references.sh
   #   rapper -q $rsyn -o rdfxml $send                                                                                                         > $epochDir/datasets.ttl.rdf
   #   echo "$DATAFAQS_BASE_URI/datafaqs/epoch/$epoch/config/dataset-references"                                                     > $epochDir/dataset-references.ttl.sd_name
   #   pushd $epochDir &> /dev/null
   #      df-core.py datasets.ttl.rdf datasets df:chunk &> /dev/null # creates dataset-references.post.1.ttl,
   #      if [ -e dataset-references.post.1.ttl ]; then              #         dataset-references.post.2.ttl in blocks of 25
   #         # Contains "one-liners", e.g.: <http://thedatahub.org/dataset/instance-hub-fiscal-years> a <http://www.w3.org/ns/dcat#Dataset> .
   #         echo
   #         total=0
   #         for post in dataset-references.post*; do let "total=total+1"; done
   #         count=0
   #         for chunk in dataset-references.post*; do
   #            let "count=count+1"
   #            echo "[INFO] Following rdfs:seeAlso references for datasets listed in $chunk ($count/$total)"
   #            #curl -s -H "Content-Type: $mime" -H 'Accept: text/turtle' -d @$chunk $dataset_referencer                                      >> dataset-references.ttl
   #            # TODO: they aren't accepting conneg!
   #            curl -s -H "Content-Type: $mime" -d @$chunk $dataset_referencer                                                                >> dataset-references-response
   #            if [ `void-triples.sh dataset-references-response` -le 0 ]; then
   #               echo "[WARNING] Could not find triples in response from $dataset_referencer"
   #            else
   #               cat dataset-references-response                                                                                             >> dataset-references.ttl
   #            fi
   #            rm dataset-references-response
   #         done
   #      else
   #         echo "[WARNING] $epochDir/datasets.ttl.rdf did not list any datasets."
   #         exit 1
   #      fi
   #   popd &> /dev/null
   #   # 502s: source $epochDir/dataset-references.sh                                                                                        > $epochDir/dataset-references.ttl
   #   triples=`void-triples.sh $dir/dataset-references.ttl`
   #   df-epoch-metadata.py dataset-references $DATAFAQS_BASE_URI $epoch $dir/dataset-references.ttl text/turtle ${triples:-0}         > $epochDir/dataset-references.meta.ttl
   #   if [ $triples -le 0 ]; then
   #      echo "[WARNING] $epochDir/dataset-references.ttl did not provide any references."
   #      touch                                                                                                                             $epochDir/dataset-references.ttl.nt
   #   else
   #      # This file is grep'ed for each dataset to get the rdfs:seeAlso objects.
   #      rapper -q -g -o ntriples $epochDir/dataset-references.ttl | sed 's/<//g; s/>//g'                                                > $epochDir/dataset-references.ttl.nt
   #   fi
   #done

   if [ "$DATAFAQS_PUBLISH_THROUGHOUT_EPOCH" == "true" ]; then
      df-load-triple-store.sh --graph `cat $epochDir/epoch.ttl.sd_name`                 $epochDir/epoch.ttl                   | awk '{print "[INFO] loaded",$0,"triples"}'

      df-load-triple-store.sh --graph `cat $epochDir/faqt-services.ttl.sd_name`         $epochDir/faqt-services.ttl           | awk '{print "[INFO] loaded",$0,"triples"}'
      df-load-triple-store.sh --graph $metadata_name                                    $epochDir/faqt-services.meta.ttl      | awk '{print "[INFO] loaded",$0,"triples"}'

      df-load-triple-store.sh --graph `cat $epochDir/datasets.ttl.sd_name`              $epochDir/datasets.ttl                | awk '{print "[INFO] loaded",$0,"triples"}'
      df-load-triple-store.sh --graph $metadata_name                                    $epochDir/datasets.meta.ttl           | awk '{print "[INFO] loaded",$0,"triples"}'

      if [ -e $epochDir/dataset-references.ttl ]; then
         df-load-triple-store.sh --graph `cat $epochDir/dataset-references.ttl.sd_name` $epochDir/dataset-references.ttl      | awk '{print "[INFO] loaded",$0,"triples"}'
         df-load-triple-store.sh --graph $metadata_name                                 $epochDir/dataset-references.meta.ttl | awk '{print "[INFO] loaded",$0,"triples"}'
      fi
   fi
else
   echo "[INFO] Reusing FAqT services and dataset lists and descriptions already gathered during __PIVOT_epoch/$epoch"
fi

   numFAqTs=`wc -l $epochDir/faqt-services.ttl.csv | awk '{print $1}'`
numDatasets=`wc -l $epochDir/datasets.ttl.csv      | awk '{print $1}'`

   faqtsRandom=`cat $epochDir/faqt-services.ttl.csv | randomize-line-order.py`
datasetsRandom=`cat $epochDir/datasets.ttl.csv      | randomize-line-order.py`

echo
echo "[INFO] - - - - - - - - - - - - - - - Finished determining epoch configuration. - - - - - - - - - - - - - -"
echo "[INFO] - - - - - - - - - - - - - - (df-epoch.sh --reuse-epoch datafaqs:latest) - - - - - - - - - - - - - -"

echo
echo "[INFO] $numFAqTs FAqT services will evaluate $numDatasets datasets."
sleep 2
echo
echo "[INFO] FAqT Services:"
cat $epochDir/faqt-services.ttl.csv | awk '{print "[INFO] "$0}'
echo
echo "[INFO] CKAN Datasets:"
cat $epochDir/datasets.ttl.csv      | awk '{print "[INFO] "$0}'

echo "[INFO] - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -"


#
# Set up the directory structure before starting.
# Mark the directories as a service or dataset.
#
f=0
for faqt in $faqtsRandom; do
   let 'f=f+1' # faqt evaluation service tally

   # The FAqT service for all datasets and all epochs:
   #                               FAqT Service - - - - - - - - - - - - - - - - - - - -|
   #       faqt-brick/__PIVOT_faqt/sparql.tw.rpi.edu/services/datafaqs/faqt/void-triples
   faqtDir="__PIVOT_faqt/`noprotocolnohash $faqt`"
   mkdir -p $faqtDir &> /dev/null
   echo "#3> <> prov:wasAttributedTo [ foaf:name \"df-epoch.sh\" ]; . # 499"  > $faqtDir/service.ttl
   echo "@prefix datafaqs: <http://purl.org/twc/vocab/datafaqs#> ."          >> $faqtDir/service.ttl
   echo "<$faqt> a datafaqs:FAqTService ."                                   >> $faqtDir/service.ttl
   #echo "$faqt"                                                              > $faqtDir/service.ttl.sd_name

   # The datasets that the FAqT service has evaluated (at any time):
   #       faqt-brick/__PIVOT_faqt/sparql.tw.rpi.edu/services/datafaqs/faqt/void-triples/__PIVOT_dataset
   mkdir -p $faqtDir/__PIVOT_dataset &> /dev/null
   pushd    $faqtDir/__PIVOT_dataset &> /dev/null
      d=0 # dataset tally
      for dataset in $datasetsRandom; do
         let 'd=d+1'
         datasetDir=`noprotocolnohash $dataset`
         #                         FAqT Service - - - - - - - - - - - - - - - - - - - -|                 Dataset - - - - - - - - - - - - - - - - - - |
         # faqt-brick/__PIVOT_faqt/sparql.tw.rpi.edu/services/datafaqs/faqt/void-triples/__PIVOT_dataset/thedatahub.org/dataset/farmer...united-states/
         mkdir -p $datasetDir/__PIVOT_epoch/$epoch &> /dev/null
         echo "#3> <> prov:wasAttributedTo [ foaf:name \"df-epoch.sh\" ]; . # 515"                                                            > $datasetDir/dataset.ttl
         echo "@prefix void: <http://rdfs.org/ns/void#> ."                                                                                   >> $datasetDir/dataset.ttl
         echo "<$dataset> a void:Dataset ."                                                                                                  >> $datasetDir/dataset.ttl
         #echo "$dataset"                                                                                                                     > $datasetDir/dataset.ttl.sd_name

         #                         FAqT Service - - - - - - - - - - - - - - - - - - - -|                 Dataset - - - - - - - - - - - - - - - - - - |               Epoch - -|
         # faqt-brick/__PIVOT_faqt/sparql.tw.rpi.edu/services/datafaqs/faqt/void-triples/__PIVOT_dataset/thedatahub.org/dataset/farmer...united-states/__PIVOT_epoch/2012-01-14
         # (Where the dataset evaluations will be stored)
      done
   popd &> /dev/null
done


#
#
# Gather descriptions of FAqT services and datasets.
#
#


if [ "$epoch_existed" != "true" ]; then

   echo
   echo "[INFO] Gathering information about FAqT evaluation services:"
   echo
   #
   # Gather descriptions about the FAqT services.
   #
   f=0 # "faqt"
   for faqt in $faqtsRandom; do # http://aquarius.tw.rpi.edu/projects/datafaqs/services/sadi/faqt/connected/void-linkset
      let "f=f+1"
      #                         FAqT Service - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -|
      # faqt-brick/__PIVOT_faqt/aquarius.tw.rpi.edu/projects/datafaqs/services/sadi/faqt/connected/void-linkset/
      faqtDir="__PIVOT_faqt/`noprotocolnohash $faqt`"
      echo "[INFO] ${faqtDir#'__PIVOT_faqt/'} ($f/$numFAqTs)"

      # The FAqT service as described at different times.
      #                         FAqT Service - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -|               Epoch - -|
      # faqt-brick/__PIVOT_faqt/aquarius.tw.rpi.edu/projects/datafaqs/services/sadi/faqt/connected/void-linkset/__PIVOT_epoch/2012-05-22/
      mkdir -p $faqtDir/__PIVOT_epoch/$epoch &> /dev/null
         epDir=$faqtDir/__PIVOT_epoch/$epoch

      pushd $faqtDir/__PIVOT_epoch/$epoch &> /dev/null
         pcurl.sh $faqt -n faqt-service -e ttl &> /dev/null
         $CSV2RDF4LOD_HOME/bin/util/rename-by-syntax.sh faqt-service
         echo "$DATAFAQS_BASE_URI/datafaqs/epoch/$epoch/faqt/$f"                                                                       > faqt-service.ttl.sd_name
         rapper -q -g -o turtle $faqt                                                                                                  > faqt-service.ttl
         triples=`void-triples.sh faqt-service.ttl`
         dump=$faqtDir/__PIVOT_epoch/$epoch/faqt-service.ttl
         df-epoch-metadata.py faqt-service $DATAFAQS_BASE_URI $epoch $faqt $f $dump text/turtle ${triples:-0}                          > faqt-service.meta.ttl
         if [ "$DATAFAQS_PUBLISH_THROUGHOUT_EPOCH" == "true" ]; then
            df-load-triple-store.sh --graph `cat faqt-service.ttl.sd_name` faqt-service.ttl | awk '{print "[INFO] loaded",$0,"triples"}'
            df-load-triple-store.sh --graph $metadata_name faqt-service.meta.ttl            | awk '{print "[INFO] loaded",$0,"triples"}'
         fi
      popd &> /dev/null
   done


   echo
   echo "[INFO] Gathering information about CKAN Datasets (will be input to FAqT evaluation services):"
   echo
   #
   # Gather descriptions about the datasets (to input to the FAqT evaluation services).
   #
   d=0 # "dataset"
   pushd $epochDir &> /dev/null
      #                          Epoch - -|
      # faqt-brick/__PIVOT_epoch/2012-01-14
      for dataset in $datasetsRandom; do # http://thedatahub.org/dataset/farmers-markets-geographic-data-united-states
         let "d=d+1"
         datasetDir=`noprotocol $dataset`
         echo "[INFO] $datasetDir ($d/$numDatasets)"

         # The dataset as described during **this** epoch (becomes the input to FAqT evaluation services).
         #
         #                          Epoch - -|                 Dataset - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -|
         # faqt-brick/__PIVOT_epoch/2012-01-14/__PIVOT_dataset/thedatahub.org/dataset/farmers-markets-geographic-data-united-states/
         mkdir -p __PIVOT_dataset/$datasetDir
         pushd __PIVOT_dataset/$datasetDir &> /dev/null

            # File 'dataset.ttl' is already here, created above by 'df-core.py $epochDir/datasets.ttl.rdf datasets df:individual'

            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
            #
            # Set up (and submit) requests for references.
            #
            r=1 # "referencer"
            for referencer in `cat $epochDir/referencers.csv`; do 
               # ^ e.g. http://aquarius.tw.rpi.edu/projects/datafaqs/services/sadi/core/augment-datasets/with-preferred-uri-and-ckan-meta-void
               referencer=${referencer%#*} # Strip fragment-identifier
               echo "curl -s -H 'Content-Type: text/turtle' -d @dataset.ttl $referencer > references-$r"                         > get-references-$r.sh
               let 'r=r+1'
            done
            r=1 # "referencer"
            for referencer in `cat $epochDir/referencers.csv`; do
               source                                                                                                              get-references-$r.sh
               file=`$CSV2RDF4LOD_HOME/bin/util/rename-by-syntax.sh --verbose references-$r`                                     # references-$r
               if [[ `valid-rdf.sh $file` == "yes" ]]; then
                  rdf2nt.sh -I $referencer $file                                                                                >> references.nt
               else
                  echo "[WARNING] $file was not valid RDF."
               fi
               let 'r=r+1'
            done

            # Compile the list of references.
            echo $dataset                                                                                                        > references.csv
            if [[ -e references.nt ]]; then
               seeAlso='http://www.w3.org/2000/01/rdf-schema#seeAlso'
               cat references.nt | grep $dataset | grep $seeAlso | sed 's/<//g;s/>//g' | awk '{print $3}'                       >> references.csv
               rm references.nt
            fi
            #
            # references.nt and referencers.csv now contain URL references that should also provide information about the dataset.
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #



            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
            #
            # Set up requests for references.
            #
            s=0 # "see also" (The zeroth is the actual URI; all others are third-party)
            for reference in `cat references.csv`; do
               file="reference-$s"
               echo "curl -s -L -H \"$ACCEPT_HEADER\" $reference > reference-$s"                                                 > get-reference-$s.sh
               let 's=s+1'
            done
            #
            # Request references.
            #
            s=0 # "see also"
            indent=""
            for reference in `cat references.csv`; do
               file="reference-$s"
               echo "$indent   ($s): $reference"
               source                                                                                                              get-reference-$s.sh
               file=`$CSV2RDF4LOD_HOME/bin/util/rename-by-syntax.sh --verbose $file`                                             # reference-{1,2,3,...}.{ttl,rdf,nt}
               triples=`void-triples.sh $file`
               mime=`guess-syntax.sh --inspect "$file" mime`
               head -1 $file | awk -v indent="$indent" -v triples=$triples -v mime=$mime '{print indent"    `=> "triples" "mime" triples: "substr($0,1,60)}'
               if [[ `valid-rdf.sh $file` == "yes" ]]; then
                  rdf2nt.sh -I $reference $file                                                                                 >> post.nt
               fi
               let 's=s+1'
               indent="     "
            done
            rdf2nt.sh dataset.ttl                                                                                               >> post.nt 
            #         ^ - - What we found out from the Dataset Selectors should also be POSTed Augmenters.
            #
            # post.nt now has everything that we could find out from the Dataset Selectors and all reference URLs provided by the Referencers.
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #




            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #     To post to Augmenters \........../             
            rapper -q -i ntriples -o rdfxml post.nt                                                                              > post.nt.rdf
 
            #
            # Set up requests for augmenters.
            #
            a=1 # "augmenter"
            for augmenter in `cat $epochDir/augmenters.csv`; do
               # Wilkinson's lab can't handle conneg:
               # echo "curl -s -H 'Content-Type: text/turtle' -d @post.ttl $augmenter > augmentation-$a"                         > get-augmentation-$a.sh
               echo "curl -s -H 'Content-Type: application/rdf+xml' -d @post.nt.rdf $augmenter > augmentation-$a"                > get-augmentation-$a.sh
               let 'a=a+1'
            done
            #
            # Request augmentations.
            #
            a=1 # "augmenter"
            for augmenter in `cat $epochDir/augmenters.csv`; do
               source                                                                                                              get-augmentation-$a.sh
               file=`$CSV2RDF4LOD_HOME/bin/util/rename-by-syntax.sh --verbose augmentation-$a`                                   # augmentation-$a
               if [ `void-triples.sh $file` -gt 0 ]; then
                  rdf2nt.sh -I $augmenter $file                                                                                 >> augmentations.nt
               fi
               let 'a=a+1'
            done
            if [ -e augmentations.nt ]; then
               cat augmentations.nt >> post.nt
            fi

            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #      To post to FAqT Services \........../             
            rapper -q -i ntriples -o rdfxml post.nt                                                                              > post.nt.rdf
            cr-default-prefixes.sh --turtle > post.nt.ttl0
            cat post.nt.ttl0 post.nt | serdi -i turtle -o turtle -                                                               > post.nt.ttl
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #     For human readability    /^^^^^^^^^\
            rm post.nt.ttl0



 
            #
            # Create metadata and publish
            #
            triples=`void-triples.sh post.nt`
            if (( $triples > 0 )); then
               echo "$DATAFAQS_BASE_URI/datafaqs/epoch/$epoch/dataset/$d"                                                        > post.nt.sd_name
               touch post.nt
               if [ "$DATAFAQS_PUBLISH_THROUGHOUT_EPOCH" == "true" ]; then
                  df-load-triple-store.sh --graph `cat post.nt.sd_name` post.nt.rdf | awk '{print "[INFO] loaded",$0,"triples"}'
               fi
            fi
            # Graph metadata (regardless of the graph size)
            dump="__PIVOT_epoch/$epoch/__PIVOT_dataset/$datasetDir/post.nt"
            df-epoch-metadata.py dataset $DATAFAQS_BASE_URI $epoch $dataset $d $dump text/turtle $triples                        > post.meta.ttl
            if [ "$DATAFAQS_PUBLISH_THROUGHOUT_EPOCH" == "true" ]; then
               df-load-triple-store.sh --graph $metadata_name post.meta.ttl    | awk '{print "[INFO] loaded",$0,"triples"}'
            fi
         popd &> /dev/null
         echo
      done # end datasets
   popd &> /dev/null
fi
# Find references and augmentations that were not RDF (in df-find.sh):
#
# find __PIVOT_epoch/2013-04-14/__PIVOT_dataset/ -name "augmentation-*" -o -name "reference-*" | xargs valid-rdf.sh -v | grep "^no"

if [ "$dryrun" == "true" ]; then
   echo "[INFO] skipping (dryrun): Submitting CKAN dataset information to FAqT evaluation services."
   exit 1
fi


# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 


echo
echo "[INFO] Submitting CKAN dataset information to FAqT evaluation services. Will store responses."
echo

#
# Total number of datasets that *will be* evaluated:
#
# (in df-find.sh)
# find __PIVOT_epoch/2014-04-07 -name "dataset.ttl" | wc -l
# 890
#
# (in df-find.sh)
# find __PIVOT_faqt -name 2014-04-07 | grep '__PIVOT_dataset' | grep '__PIVOT_epoch/2014-04-07'
# 890
#
#
# Total number of datasets that *were* evaluated: (in df-find.sh)
#
# find __PIVOT_faqt -name "request.sh" | grep '__PIVOT_epoch/2014-04-07' | wc -l
# 508
#
# Dataset evaluations that were not RDF: (in df-find.sh)
#
# find __PIVOT_faqt/ -name "evaluation" | grep '__PIVOT_epoch/2014-04-07'

let "total = numDatasets * numFAqTs"
f=0 # faqt evaluation service tally
d=0 # dataset                 tally
e=0 # evaluation              tally
for dataset in $datasetsRandom; do # Ordering randomized to distribute load among evaluation services.
   let 'd=d+1'
   datasetDir=`noprotocolnohash $dataset`
   for faqt in $faqtsRandom; do
      faqtDir="__PIVOT_faqt/`noprotocolnohash $faqt`"
      let 'f=f+1'
      let 'e=e+1'
      echo "[INFO] dataset $d/$numDatasets, FAqT $f/$numFAqTs ($e/$total total)"
      echo "[INFO] $dataset"
      echo "[INFO] $faqt"


      # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
      post="`pwd`/__PIVOT_epoch/$epoch/__PIVOT_dataset/$datasetDir/post.nt.rdf" # pwd for absolute path of brick root  #
      #                          Epoch - -|                 Dataset - - - - - - - - - - - - - - - - - - -|             #
      # faqt-brick/__PIVOT_epoch/2012-01-14/__PIVOT_dataset/thedatahub.org/dataset/farmers...united-states/post.nt.rdf #
      # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 


      # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
      evalDir=$faqtDir/__PIVOT_dataset/$datasetDir/__PIVOT_epoch/$epoch                                                                                        #  
      #            FAqT Service - - - - - - - - - - - - - - - - - - - -|                 Dataset - - - - - - - - - - - - - - - - - - -|               Epoch - -|
      # faqt-brick/sparql.tw.rpi.edu/services/datafaqs/faqt/void-triples/__PIVOT_dataset/thedatahub.org/dataset/farmers...united-states/__PIVOT_epoch/2012-01-14
      # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 


      pushd $evalDir &> /dev/null # Directory already placed by loop above that placed 'dataset.ttl' within __PIVOT_faqt/__PIVOT_dataset/__PIVOT_epoch/.
         # The request.sh HAS NOT been placed until now, when it is about to be run. So it is a flag for whether or not it was already done.
         if [[ ! -e request.sh ]]; then
            #
            # Set up request
            #
            [[ "$DATAFAQS_EVALUATION_TIMEOUT" =~ ^-?[0-9]+$ && "$DATAFAQS_EVALUATION_TIMEOUT" -gt 0 ]] && timeout="--max-time $DATAFAQS_EVALUATION_TIMEOUT" || timeout=''
            output="evaluation"
            echo "#!/bin/bash"                                                                                                         > request.sh
            # TODO http://code.google.com/p/sadi/issues/detail?id=15
            # TODO: ^^> echo curl -s -H "'Content-Type: application/rdf+xml'" -H "'Accept: text/turtle'" -d @$post $faqt >> request.sh # evaluation.sh
            echo curl -s -H "'Content-Type: application/rdf+xml'" $timeout -d @$post $faqt                                            >> request.sh

            #
            # Request
            #
            source request.sh                                                                                                          > $output # evaluation

            mimetype=`guess-syntax.sh --inspect $output mime`
            echo "[INFO] `du -sh evaluation | awk '{print $1}'` of $mimetype"

            # Rename 'evaluation' to include a syntax-appropriate extension.
            rename=`$CSV2RDF4LOD_HOME/bin/util/rename-by-syntax.sh --verbose $output`                                                         # evaluation.{ttl,rdf,nt}
            # Meta
            if [[ "$rename" == "$output" || "$rename" == "" ]]; then
               meta=$output.meta.ttl # There was no extension
               rename="$output"
            else
               # blah.blah.rdf -> blah.blah.meta.rdf
               meta=`echo $rename | sed 's/\(\.[^.]*\)$/.meta\1/'` # does not append anything if there is no extension
            fi
            echo "$DATAFAQS_BASE_URI/datafaqs/epoch/$epoch/faqt/$f/dataset/$d" > $rename.sd_name                                              # evaluation.{ttl,rdf,nt}.sd_name
            dump=$evalDir/$rename
            triples=`void-triples.sh $rename`
            echo "# df-epoch-metadata.py evaluation $DATAFAQS_BASE_URI $epoch $faqt $f $dataset $d $dump ${mimetype:-.} ${triples:-0}" > $meta
                    df-epoch-metadata.py evaluation $DATAFAQS_BASE_URI $epoch $faqt $f $dataset $d $dump ${mimetype:-.} ${triples:-0} >> $meta # evaluation.{ttl,rdf,nt}.meta

            # State when evaluation returned HTML:  State when the evaluation returned RDF (NOTE: even if the RDF is a triple with a SADI error):
            # request.sh                            request.sh
            # evaluation                            evaluation.rdf
            # evaluation.sd_name                    evaluation.rdf.sd_name
            # evaluation.meta.ttl                   evaluation.meta.rdf

            if [ "$DATAFAQS_PUBLISH_THROUGHOUT_EPOCH" == "true" ]; then
               df-load-triple-store.sh --graph `cat $rename.sd_name` $rename | awk '{print "[INFO] loaded",$0,"triples"}'
               df-load-triple-store.sh --graph $metadata_name $meta          | awk '{print "[INFO] loaded",$0,"triples"}'
            fi
         else
            echo "[INFO] (evaluation already gathered; skipping)"
         fi
      popd &> /dev/null
      echo
   done
   f=0
done
