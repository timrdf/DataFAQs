#!/bin/bash
#
#3> <> prov:specializationOf <https://github.com/timrdf/DataFAQs/tree/master/bin/df-mirror-endpoint.sh>;
#3>    prov:alternateOf <https://github.com/timrdf/csv2rdf4lod-automation/blob/master/bin/util/mirror-endpoint.sh>;
#3>    rdfs:seeAlso     <https://github.com/timrdf/csv2rdf4lod-automation/wiki/Named-graphs-that-know-where-they-came-from#mirroring-another-endpoints-named-graph>;
#3> .
#
# Usage:
#
#    df-mirror-endpoint.sh http://ieeevis.tw.rpi.edu/sparql
#       ^
#       Retrieves all named graphs' dump files.
#
#    df-mirror-endpoint.sh http://ieeevis.tw.rpi.edu/sparql --graph http://ieeevis.tw.rpi.edu/lam-2012-evaluations-2-categories
#       ^
#       Retrieves all named graphs' dump files
#
#    df-mirror-endpoint.sh --graph http://ieeevis.tw.rpi.edu/lam-2012-evaluations-2-categories http://ieeevis.tw.rpi.edu/sparql
#       ^
#       Retrieves the dump file for graph named http://ieeevis.tw.rpi.edu/lam-2012-evaluations-2-categories 
#                            in SPARQL endpoint http://ieeevis.tw.rpi.edu/sparql
#
#    df-mirror-endpoint.sh --graph http://ieeevis.tw.rpi.edu/lam-2012-evaluations-2-categories http://ieeevis.tw.rpi.edu/sparql http://logd.tw.rpi.edu/sparql
#       ^
#       Retrieves the dump file for graph named http://ieeevis.tw.rpi.edu/lam-2012-evaluations-2-categories 
#                           in SPARQL endpoints http://ieeevis.tw.rpi.edu/sparql 
#                                           AND http://logd.tw.rpi.edu/sparql

HOME=$(cd ${0%/*} && echo ${PWD%/*})
me=$(cd ${0%/*} && echo ${PWD})/`basename $0`

if [[ $# -le 0 || "$1" == "--help" ]]; then
   echo
   echo "usage: `basename $0` [--graph <graph-name>] <endpoint>+"
   echo
   echo "  --graph <graph-name> : The GRAPH {} name to retrieve."
   echo
   exit 1
fi

if [ ! `which cache-queries.sh` ]; then
   need='https://github.com/timrdf/csv2rdf4lod-automation/blob/master/bin/util/cache-queries.sh'
   echo "ERROR: need $need"
   exit 1
fi
if [ ! `which saxon.sh` ]; then
   need='https://github.com/timrdf/csv2rdf4lod-automation/blob/master/bin/dup/saxon.sh'
   echo "ERROR: need $need"
   exit 1
fi
if [ ! `which md5.sh` ]; then
   need='https://github.com/timrdf/csv2rdf4lod-automation/blob/master/bin/util/md5.sh'
   echo "ERROR: need $need"
   exit 1
fi

function noprotocolnohash {
   url="$1"
   url=${url#'http://'}
   url=${url#'https://'}
   url=${url%#*} # take off fragment identifier
   echo $url
}

while [[ $# -gt 0 ]]; do
   if [[ "$1" == "--graph" ]]; then
      focus="$2"
      shift 2
   fi
   if [[ $# -eq 0 ]]; then
      $0 --help
      echo
      echo "No endpoint given."
      exit 1
   fi
   endpoint="$1"
   shift
   endpoint_path=`noprotocolnohash $endpoint`
   echo $endpoint_path
   mkdir -p $endpoint_path/__PIVOT__
   if [[ -z "$focus" ]]; then
      # Determine all graph names in the endpoint.
      df-named-graphs.py $endpoint > $endpoint_path/sdnames.csv
   fi
   for sdname in ${focus:-`cat $endpoint_path/sdnames.csv`}; do
      pushd $endpoint_path/__PIVOT__ &> /dev/null
         sdname_path=`noprotocolnohash $sdname`
         echo "  $endpoint_path/__PIVOT__/$sdname_path"
         mkdir -p $sdname_path
         pushd $sdname_path &> /dev/null
            echo $sdname > sdname.csv
            # Note: this query depends on csv2rdf4lod-automation's provenance (via its pvload.sh)
            #    \\.//
            #     \./
            cat $me.rq | perl -pi -e "s|SDNAME|$sdname|" > sdname.rq
            if [ ! -e sdname/sdname.rq.xml ]; then
               cache-queries.sh $endpoint -o xml -q sdname.rq -od sdname # Find out the RDF filed loaded.
            fi
            if [ ! -e inputs.csv ]; then
               saxon.sh $HOME/bin/get-binding.xsl a a -v name=input -in sdname/sdname.rq.xml > inputs.csv
            fi
            for input in `cat inputs.csv`; do
               hash=`md5.sh -qs $input`
               if [ ! -e input_$hash ]; then
                  pcurl.sh $input -n input_$hash
                  retrieved=`rename-by-syntax.sh -v input_$hash`
                  echo "<$retrieved> prov:alternateOf <input_$hash> ." >> input_$hash.prov.ttl
                  echo $sdname > $retrieved.sd_name
                  touch input_$hash
               fi
            done
         popd &> /dev/null
      popd &> /dev/null
   done
done
