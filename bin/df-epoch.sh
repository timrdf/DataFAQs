#!/bin/bash
#
# https://github.com/timrdf/DataFAQs/blob/master/bin/datafaqs-evaluate.sh
# 
# DataFAqTs core evaluation engine: 
#   Retrieves dataset and FAqT evaluation service lists, 
#   Invokes evaluation services with dataset information, and
#   Stores the results in a datacube-like directory structure.

DATAFAQS_HOME=${DATAFAQS_HOME:?"not set; see https://github.com/timrdf/DataFAQs/wiki/Installing-DataFAQs"}
CSV2RDF4LOD_HOME=${CSV2RDF4LOD_HOME:?"not set; see https://github.com/timrdf/csv2rdf4lod-automation/wiki/CSV2RDF4LOD-not-set"}
DATAFAQS_BASE_URI=${DATAFAQS_BASE_URI:?"not set; see https://github.com/timrdf/DataFAQs/wiki/DATAFAQS-envrionment-variables"}

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
   fi
   if [ ! -e __PIVOT_epoch/$epoch ]; then
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

# # # # Hard coded parameters

ACCEPT_HEADER="Accept: text/turtle; application/rdf+xml; q=0.8, text/plain; q=0.6"
ACCEPT_HEADER="Accept: text/turtle; application/x-turtle; q=0.9, application/rdf+xml; q=0.8, text/plain; q=0.6"

# # # #

echo "[INFO] Using __PIVOT_epoch/$epoch $latest_requested"

if [ "$epoch_existed" != "true" ]; then

   echo "[INFO] Requesting FAqT services from $faqts_service"
   echo "curl -s -H 'Content-Type: text/turtle' -H 'Accept: text/turtle' -d @$faqts_input $faqts_service"                                                       > $epochDir/faqt-services.sh
   source $epochDir/faqt-services.sh                                                                                                                            > $epochDir/faqt-services.ttl
   echo "$DATAFAQS_BASE_URI/datafaqs/epoch/$epoch/config/faqt-services"                                                                                         > $epochDir/faqt-services.ttl.sd_name
   rapper -q -g -o ntriples $epochDir/faqt-services.ttl | sed 's/<//g;s/>//g' | grep "purl.org/dc/terms/hasPart" | awk '{print $3}' | grep "^http://" | sort -u > $epochDir/faqt-services.ttl.csv

   echo "[INFO] Requesting datasets from $datasets_service"
   mime=`guess-syntax.sh $datasets_input mime`
   echo "curl -s -H \"Content-Type: $mime\" -H 'Accept: text/turtle' -d @$datasets_input $datasets_service"                                        > $epochDir/datasets.sh
   source $epochDir/datasets.sh                                                                                                                    > $epochDir/datasets.ttl
   echo "$DATAFAQS_BASE_URI/datafaqs/epoch/$epoch/config/datasets"                                                                                 > $epochDir/datasets.ttl.sd_name

   echo "[INFO] Requesting dataset descriptions from $references_service"
   send="$epochDir/datasets.ttl"
   mime=`guess-syntax.sh $send mime`
   echo "curl -s -H 'Content-Type: $mime' -H 'Accept: text/turtle' -d @$send $references_service"                                          > $epochDir/dataset-references.sh
   source $epochDir/dataset-references.sh                                                                                                  > $epochDir/dataset-references.ttl
   echo "$DATAFAQS_BASE_URI/datafaqs/epoch/$epoch/config/dataset-references"                                                               > $epochDir/dataset-references.ttl.sd_name
   rapper -q -g -o ntriples $epochDir/dataset-references.ttl | sed 's/<//g; s/>//g'                                                        > $epochDir/dataset-references.ttl.nt
   cat $epochDir/dataset-references.ttl.nt | grep "vocab/datafaqs#WithReferences *\." | awk '{print $1}' | grep "^http://" | sort -u       > $epochDir/datasets.ttl.csv
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
   faqtDir=${faqt#'http://'}
   # /faqt-brick/sparql.tw.rpi.edu/services/datafaqs/faqt/void-triples/
   echo "@prefix datafaqs: <http://purl.org/twc/vocab/datafaqs#> ."  > $faqtDir/service.ttl
   echo "<$faqt> a datafaqs:FAqTService ."                          >> $faqtDir/service.ttl                             # service.ttl

   mkdir -p $faqtDir/__PIVOT_dataset &> /dev/null
   # /faqt-brick/sparql.tw.rpi.edu/services/datafaqs/faqt/void-triples/__PIVOT_dataset

   # Where the dataset descriptions will be stored.
   pushd $faqtDir/__PIVOT_dataset &> /dev/null
      d=0 # dataset tally
      for dataset in $datasetsRandom; do
         let 'd=d+1'
         datasetDir=${dataset#'http://'}
         # /faqt-brick/sparql.tw.rpi.edu/services/datafaqs/faqt/void-triples/__PIVOT_dataset/thedatahub.org/dataset/farmers-markets-geographic-data-united-states/
         echo "@prefix void: <http://rdfs.org/ns/void#> ."  > $datasetDir/dataset.ttl
         echo "<$dataset> a void:Dataset ."                >> $datasetDir/dataset.ttl                                   # dataset.ttl
         mkdir -p $datasetDir/__PIVOT_epoch/$epoch &> /dev/null
         # /faqt-brick/sparql.tw.rpi.edu/services/datafaqs/faqt/void-triples/__PIVOT_dataset/thedatahub.org/dataset/farmers-markets-geographic-data-united-states/__PIVOT_epoch/2012-01-14
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
   # /faqt-brick/__PIVOT_epoch/2012-01-14 
   # /faqt-brick/sparql.tw.rpi.edu/services/datafaqs/faqt/void-triples/__PIVOT_epoch
   for faqt in $faqtsRandom; do
      let "f=f+1" 
      faqtDir=${faqt#'http://'}
      echo "$faqtDir ($f/$numFAqTs)"
      mkdir -p $faqtDir/__PIVOT_epoch/$epoch &> /dev/null
      # /faqt-brick/__PIVOT_epoch/2012-01-14/__PIVOT_faqt/sparql.tw.rpi.edu/services/datafaqs/faqt/void-triples          
      pushd    $faqtDir/__PIVOT_epoch/$epoch &> /dev/null
         pcurl.sh $faqt -n faqt-service -e turtle &> /dev/null
         $CSV2RDF4LOD_HOME/bin/util/rename-by-syntax.sh faqt-service
         rapper -q -g -o turtle $faqt > faqt-service.ttl                                                                 # faqt-service.{ttl,rdf,nt}
         echo "$DATAFAQS_BASE_URI/datafaqs/epoch/$epoch/faqt/$f" > faqt-service.ttl.sd_name                              # faqt-service.ttl.sd_name
         echo "@prefix prov: <http://www.w3.org/ns/prov-o/> ."                                      > faqt-service.ttl.meta
         echo "<$DATAFAQS_BASE_URI/datafaqs/epoch/$epoch/faqt/$f> prov:specializationOf <$faqt> ." >> faqt-service.ttl.meta # faqt-service.ttl.meta
      popd &> /dev/null
   done

   echo
   echo "[INFO] Gathering information about CKAN Datasets. Will be input to FAqT evaluation services."
   echo
   #
   # Gather descriptions about the CKAN datasets (to input to the FAqT evaluation services).
   #
   d=0
   # /faqt-brick/__PIVOT_epoch/2012-01-14 
   pushd $epochDir &> /dev/null
      for dataset in `cat $epochDir/datasets.ttl.csv`; do
         let "d=d+1" 
         datasetDir=${dataset#'http://'}
         echo "$datasetDir ($d/$numDatasets)"

         # Where the dataset info is stored. 
         # Becomes the input to FAqT evaluation services.
         mkdir -p __PIVOT_dataset/$datasetDir
         # /faqt-brick/__PIVOT_epoch/2012-01-14/__PIVOT_dataset/thedatahub.org/dataset/farmers-markets-geographic-data-united-states 
         pushd __PIVOT_dataset/$datasetDir &> /dev/null
            echo "@prefix datafaqs: <http://purl.org/twc/vocab/datafaqs#> ."                                              > dataset.ttl
            echo "<$dataset> a datafaqs:CKANDataset ."                                                                   >> dataset.ttl
            cat $epochDir/dataset-references.ttl.nt | grep $dataset | grep 'http://www.w3.org/2000/01/rdf-schema#seeAlso' > references.nt
            cat references.nt | grep $dataset | grep 'http://www.w3.org/2000/01/rdf-schema#seeAlso' | awk '{print $3}'    > references.nt.csv
            s=0 # see also
            file="part-$s"
            curl -s -L -H "$ACCEPT_HEADER" $dataset > $file
            extension=`guess-syntax.sh --inspect $file extension`
            head -1 $file | awk '{print "   "$0}'
            mv $file $file.$extension                                                                                     # part-0
            rapper -q -g -o turtle "$file.$extension" > post.ttl
            for reference in `cat references.nt.csv`; do
               let 's=s+1'
               file="part-$s"
               echo "   $s: $reference"
               curl -s -L -H "$ACCEPT_HEADER" $reference > "$file"
               head -1 $file | awk '{print "      "$0}'
               extension=`guess-syntax.sh --inspect "$file" extension`
               mv $file $file.$extension                                                                                  # part-1,2,3...
               rapper -q -g -o turtle $file.$extension >> post.ttl                                                        # post.ttl
            done
            rapper -q -g -o rdfxml post.ttl > post.ttl.rdf                                                                # post.ttl.rdf
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
   datasetDir=${dataset#'http://'}
   for faqt in $faqtsRandom; do
      faqtDir=${faqt#'http://'}
      let 'f=f+1'
      let 'e=e+1'
      echo "[INFO] dataset $d/$numDatasets, FAqT $f/$numFAqTs ($e/$total total)"
      echo "[INFO] $dataset"
      echo "[INFO] $faqt"
      post="`pwd`/__PIVOT_epoch/$epoch/__PIVOT_dataset/$datasetDir/post.ttl.rdf" # pwd b/c paths are variable depth
      # /faqt-brick/sparql.tw.rpi.edu/services/datafaqs/faqt/void-triples/__PIVOT_dataset/thedatahub.org/dataset/farmers-markets-geographic-data-united-states/__PIVOT_epoch/2012-01-14 
      pushd $faqtDir/__PIVOT_dataset/$datasetDir/__PIVOT_epoch/$epoch &> /dev/null
         output="evaluation"
         echo "#!/bin/bash" > request.sh
         #echo curl -s -H "'Content-Type: text/turtle'" -H "'Accept: text/turtle'" -d @$post $faqt >> request.sh           # request.sh
         echo curl -s -H "'Content-Type: application/rdf+xml'" -H "'Accept: text/turtle'" -d @$post $faqt >> request.sh    # request.sh
         source request.sh > $output
         echo "[INFO] `du -sh evaluation | awk '{print $1}'` of `guess-syntax.sh --inspect $output mime`"
         $CSV2RDF4LOD_HOME/bin/util/rename-by-syntax.sh $output                                                            # result.{ttl,rdf,nt}
      popd &> /dev/null
      echo
   done
   f=0
done