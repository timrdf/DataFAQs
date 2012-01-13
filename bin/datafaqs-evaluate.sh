#!/bin/bash
#
# https://github.com/timrdf/DataFAQs/blob/master/bin/datafaqs-evaluate.sh
# 
# DataFAqTs core evaluation engine: 
#   Retrieves dataset and FAqT evaluation service lists, 
#   Invokes evaluation services with dataset information, and
#   Stores the results in a datacube-like directory structure.

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
   echo "                   e.g.:  datafaqs-evaluate.sh --reuse-epoch datafaqs.localhost/epochs/2011-Dec-21_20_22_42"
   echo "                   e.g.:  datafaqs-evaluate.sh --reuse-epoch datafaqs:latest"
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
if [ "$1" == "--reuse-epoch" ]; then
   if [ $# -lt 2 ]; then
      echo "[ERROR] --reuse-epoch argument must be followed by the name of an epoch."
      echo
      $0 --help
   else
      epoch="${2#datafaqs.localhost/epochs/}"
      shift 2
   fi 
   if [ "$epoch" == "datafaqs:latest" ]; then
      epoch=`ls -lt datafaqs.localhost/epochs/ | grep -v "^total" | head -1 | awk '{print $NF}'`
      latest_requested=" (datafaqs:latest)"
   fi
   if [ ! -e datafaqs.localhost/epochs/$epoch ]; then
      echo "[ERROR] epoch from --reuse-epoch ($epoch) does not exist: datafaqs.localhost/epochs/$epoch"
      echo
      $0 --help
   else
      epoch_existed="true"
   fi
elif [[ -e datafaqs.localhost/epochs/$epoch && $force_epoch == "false" ]]; then
   echo
   echo "An evaluation epoch has already been initiated today ($epoch)."
   echo "Start one tomorrow, use --force-epoch to create another one today, or use --help."
   exit 1
elif [[ -e datafaqs.localhost/epochs/$epoch && $force_epoch == "true" ]]; then
   epoch=`date +%Y-%m-%d_%H_%M_%S`
fi

epochDir="`pwd`/datafaqs.localhost/epochs/$epoch"
if [ ! -d $epochDir ]; then
   mkdir -p "datafaqs.localhost/epochs/$epoch"
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

echo "[INFO] Using datafaqs.localhost/epochs/$epoch $latest_requested"
echo "[INFO] Requesting FAqT services from $faqts_service"
echo "[] dcterms:description \"curl -s -H \\\"Content-Type: text/turtle\\\" -H \\\"Accept: text/turtle\\\" -d @$faqts_input $faqts_service"                  > $epochDir/faqt-services.ttl.prov.ttl
curl -s -H "Content-Type: text/turtle" -H "Accept: text/turtle" -d @$faqts_input $faqts_service                                                              > $epochDir/faqt-services.ttl
rapper -q -g -o ntriples $epochDir/faqt-services.ttl | sed 's/<//g;s/>//g' | grep "purl.org/dc/terms/hasPart" | awk '{print $3}' | grep "^http://" | sort -u > $epochDir/faqt-services.ttl.csv

if [ "$epoch_existed" != "true" ]; then
   echo "[INFO] Requesting datasets from $datasets_service"
   mime=`guess-syntax.sh $datasets_input mime`
   echo "[] dcterms:description \"curl -s -H \\\"Content-Type: $mime\\\" -H \\\"Accept: text/turtle\\\" -d @$datasets_input $datasets_service\" ." > $epochDir/datasets.ttl.prov.ttl
   curl -s -H "Content-Type: $mime" -H "Accept: text/turtle" -d @$datasets_input $datasets_service                                                 > $epochDir/datasets.ttl

   echo "[INFO] Requesting dataset descriptions from $references_service"
   send="$epochDir/datasets.ttl"
   mime=`guess-syntax.sh $send mime`
   echo "[] dcterms:description \"curl -s -H \\\"Content-Type: $mime\\\" -H \\\"Accept: text/turtle\\\" -d @$send $references_service\" ." > $epochDir/dataset-references.ttl.prov.ttl
   curl -s -H "Content-Type: $mime" -H "Accept: text/turtle" -d @$send $references_service                                                 > $epochDir/dataset-references.ttl
   rapper -q -g -o ntriples $epochDir/dataset-references.ttl | sed 's/<//g; s/>//g'                                                        > $epochDir/dataset-references.ttl.nt
   cat $epochDir/dataset-references.ttl.nt | grep "vocab/datafaqs#WithReferences *\." | awk '{print $1}' | grep "^http://" | sort -u       > $epochDir/datasets.ttl.csv
else
   echo "[INFO] Reusing dataset listing and descriptions from datafaqs.localhost/epochs/$epoch"
fi

numFAqTs=`wc -l $epochDir/faqt-services.ttl.csv | awk '{print $1}'`
numDatasets=`wc -l $epochDir/datasets.ttl.csv | awk '{print $1}'`

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
echo

# Set up the directory structure before starting.
# (can be used as a progress meter)
for faqt in `cat $epochDir/faqt-services.ttl.csv`; do
   faqtDir=${faqt#'http://'}
   mkdir -p $faqtDir/__PIVOT_dataset &> /dev/null
   echo "@prefix datafaqs: <http://purl.org/twc/vocab/datafaqs#> ." >  $faqtDir/service.ttl
   echo "<$faqt> a datafaqs:FAqTService ."                          >> $faqtDir/service.ttl

   # Where the dataset descriptions will be stored.
   pushd $faqtDir/__PIVOT_dataset &> /dev/null
      for dataset in `cat $epochDir/datasets.ttl.csv`; do
         datasetDir=${dataset#'http://'}
         mkdir -p $datasetDir/__PIVOT_epoch/$epoch &> /dev/null
         echo "@prefix void: <http://rdfs.org/ns/void#> ." >  $datasetDir/dataset.ttl
         echo "<$dataset> a void:Dataset ."                >> $datasetDir/dataset.ttl
      done
   popd &> /dev/null
done

if [ "$epoch_existed" != "true" ]; then
   echo
   echo "[INFO] Gathering information about CKAN Datasets, for input to FAqT evaluation services."
   echo

   # Prepare the input to the FAqT evaluation services.
   d=0
   pushd $epochDir &> /dev/null
      for dataset in `cat $epochDir/datasets.ttl.csv`; do
         let "d=d+1" 
         datasetDir=${dataset#'http://'}
         echo "$datasetDir ($d/$numDatasets)"

         # Where the dataset info is stored. 
         # Becomes the input to FAqT evaluation services.
         mkdir -p __PIVOT_dataset/$datasetDir
         pushd __PIVOT_dataset/$datasetDir &> /dev/null
            cat $epochDir/dataset-references.ttl.nt | grep $dataset | grep 'http://www.w3.org/2000/01/rdf-schema#seeAlso' > references.nt
            cat references.nt | grep $dataset | grep 'http://www.w3.org/2000/01/rdf-schema#seeAlso' | awk '{print $3}'    > references.nt.csv
            s=0 # see also
            file="part-$s"
            curl -s -L -H "$ACCEPT_HEADER" $dataset > $file
            extension=`guess-syntax.sh --inspect $file extension`
            head -1 $file | awk '{print "   "$0}'
            mv $file $file.$extension
            rapper -q -g -o turtle "$file.$extension" > post.ttl
            for reference in `cat references.nt.csv`; do
               let 's=s+1'
               file="part-$s"
               echo "   $s: $reference"
               curl -s -L -H "$ACCEPT_HEADER" $reference > "$file"
               head -1 $file | awk '{print "      "$0}'
               extension=`guess-syntax.sh --inspect "$file" extension`
               mv $file $file.$extension
               rapper -q -g -o turtle $file.$extension >> post.ttl
            done
         popd &> /dev/null
         echo
      done # end datasets
   popd &> /dev/null
fi

echo "[INFO] Submitting CKAN dataset information to FAqT evaluation services."
echo

let "total = numDatasets * numFAqTs"
e=0 # evaluation tally
d=0 # dataset tally
f=0 # faqt evaluation service tally
# Ordering randomized to distribute load among evaluation services.
for dataset in `cat $epochDir/datasets.ttl.csv | randomize-line-order.py`; do
   let 'd=d+1'
   datasetDir=${dataset#'http://'}
   for faqt in `cat $epochDir/faqt-services.ttl.csv | randomize-line-order.py`; do
      faqtDir=${faqt#'http://'}
      let 'f=f+1'
      let 'e=e+1'
      echo "[INFO] dataset $d/$numDatasets, FAqT $f/$numFAqTs ($e/$total total)"
      echo "[INFO] $dataset"
      echo "[INFO] $faqt"
      post="`pwd`/datafaqs.localhost/epochs/$epoch/__PIVOT_dataset/$datasetDir/post.ttl"
      pushd $faqtDir/__PIVOT_dataset/$datasetDir/__PIVOT_epoch/$epoch &> /dev/null
         output="results"
         echo "#!/bin/bash" > request.sh
         echo curl -s -H "'Content-Type: text/turtle'" -H "'Accept: text/turtle'" -d @$post $faqt >> request.sh
         curl -s -H "Content-Type: text/turtle" -H "Accept: text/turtle" -d @$post $faqt > $output
         echo "[INFO] `du -sh results | awk '{print $1}'` of `guess-syntax.sh --inspect results mime` results"
      popd &> /dev/null
      echo
   done
   f=0
done
