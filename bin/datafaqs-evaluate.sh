#!/bin/bash
#
# datafaqs-evaluate.sh

if [ "$1" == "--help" ]; then
   echo "usage: `basename $0` [-n] [--force]"
   echo "      -n: perform dry run (not implemented yet)"
   echo " --force: force new epoch; ignore 'once per day' convention."
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
fi

force_epoch="false"
if [ "$1" == "--force" ]; then
   force_epoch="true"
fi

epoch=`date +%Y-%b-%d`
if [[ -e datafaqs.localhost/epochs/$epoch && $force_epoch == "false" ]]; then
   echo "An evaluation epoch has already been initiated today ($epoch); try again tomorrow, or use --force to create another one today."
   echo
   $0 --help
   exit 1
elif [[ -e datafaqs.localhost/epochs/$epoch && $force_epoch == "true" ]]; then
   epoch=`date +%Y-%b-%d_%H_%M_%S`
fi

if [ "1" == "2" ]; then
epochDir="`pwd`/datafaqs.localhost/epochs/$epoch"
mkdir -p       "datafaqs.localhost/epochs/$epoch"

# # # # Hard coded parameters

local="$DATAFAQS_HOME/services/sadi/"
service_base='http://sparql.tw.rpi.edu/services'
ACCEPT_HEADER="Accept: text/turtle; application/rdf+xml; q=0.8, text/plain; q=0.6"
ACCEPT_HEADER="Accept: text/turtle; application/x-turtle; q=0.9, application/rdf+xml; q=0.8, text/plain; q=0.6"

# # # #

registry='core/select-evaluators/via-sparql-query-materials/sample-inputs/from-official-sadi-registry.ttl'
service='datafaqs/core/select-evaluators/via-sparql-query'
curl -s -H "Content-Type: text/turtle" -H "Accept: text/turtle" -d @$local/$registry $service_base/$service                                                  > $epochDir/faqt-services.ttl
rapper -q -g -o ntriples $epochDir/faqt-services.ttl | sed 's/<//g;s/>//g' | grep "purl.org/dc/terms/hasPart" | awk '{print $3}' | grep "^http://" | sort -u > $epochDir/faqt-services.ttl.csv

send="$local/core/select/by-ckan-group-materials/sample-inputs/thedatahub-datafaqs.ttl"
mime=`guess-syntax.sh $send mime`
curl -s -H "Content-Type: $mime" -H "Accept: text/turtle" -d @$send $service_base/datafaqs/core/select/by-ckan-group                          > $epochDir/datasets.ttl

send="$epochDir/datasets.ttl"
mime=`guess-syntax.sh $send mime`
curl -s -H "Content-Type: $mime" -H "Accept: text/turtle" -d @$send $service_base/datafaqs/core/augment/with-preferred-uri-and-ckan-meta-void > $epochDir/dataset-references.ttl
rapper -q -g -o ntriples $epochDir/dataset-references.ttl | sed 's/<//g; s/>//g'                                                              > $epochDir/dataset-references.ttl.nt
cat $epochDir/dataset-references.ttl.nt | grep "vocab/datafaqs#WithReferences *\." | awk '{print $1}' | grep "^http://" | sort -u             > $epochDir/datasets.ttl.csv

numFAqTs=`wc -l $epochDir/faqt-services.ttl.csv | awk '{print $1}'`
numDatasets=`wc -l $epochDir/datasets.ttl.csv | awk '{print $1}'`

echo `wc -l $epochDir/faqt-services.ttl.csv | awk '{print $1}'` FAqT services will evaluate `wc -l $epochDir/datasets.ttl.csv | awk '{print $1}'` datasets.
echo
echo "FAqT Services:"
echo
cat $epochDir/faqt-services.ttl.csv
echo
echo "CKAN Datasets:"
echo
cat $epochDir/datasets.ttl.csv

# Set up the directory structure before starting.
# (can be used as a progress meter)
for faqt in `cat $epochDir/faqt-services.ttl.csv`; do
   faqtDir=${faqt#'http://'}
   mkdir -p $faqtDir/__PIVOT_dataset
   echo "@prefix datafaqs: <http://purl.org/twc/vocab/datafaqs#> ." >  $faqtDir/service.ttl
   echo "<$faqt> a datafaqs:FAqTService ."                          >> $faqtDir/service.ttl

   # Where the dataset descriptions will be stored.
   pushd $faqtDir/__PIVOT_dataset &> /dev/null
      for dataset in `cat $epochDir/datasets.ttl.csv`; do
         datasetDir=${dataset#'http://'}
         mkdir -p $datasetDir/__PIVOT_epoch/$epoch
         echo "@prefix void: <http://rdfs.org/ns/void#> ." >  $datasetDir/dataset.ttl
         echo "<$dataset> a void:Dataset ."                >> $datasetDir/dataset.ttl
      done
   popd &> /dev/null
done

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

else
   epoch="2011-Dec-20_17_14_17"
   epochDir="/Users/lebot/afrl/phd/projects/DataFAQs/faqt-brick/datafaqs.localhost/epochs/2011-Dec-20_17_14_17" 
   numDatasets=3
   numFAqTs=2
   echo
   echo
   echo
   echo
   echo
   echo Using previous epoch $epoch
   echo
   echo
   echo
   echo
   echo
fi

echo "[INFO] Submitting CKAN dataset information to FAqT evaluation services."
echo

d=0
f=0
t=0
total=0
let "total = numDatasets * numFAqTs"
for dataset in `cat $epochDir/datasets.ttl.csv`; do
   let 'd=d+1'
   datasetDir=${dataset#'http://'}
   # Do datasets first to reduce load on individual services
   for faqt in `cat $epochDir/faqt-services.ttl.csv`; do # TODO: randomize evaluation service order.
      faqtDir=${faqt#'http://'}
      let 'f=f+1'
      let 't=t+1'
      echo "[INFO] dataset $d/$numDatasets, FAqT $f/$numFAqTs ($t/$total total)"
      echo "[INFO] $dataset"
      echo "[INFO] $faqt"
      post="`pwd`/datafaqs.localhost/epochs/$epoch/__PIVOT_dataset/$datasetDir/post.ttl"
      pushd $faqtDir/__PIVOT_dataset/$datasetDir/__PIVOT_epoch/$epoch &> /dev/null
         output="results.ttl"
         curl -s -H "Content-Type: text/turtle" -H "Accept: text/turtle" -d @$post $faqt > $output
      popd &> /dev/null
      echo
   done
   f=0
done
