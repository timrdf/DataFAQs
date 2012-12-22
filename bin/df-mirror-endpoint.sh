#!/bin/bash
#
# <> prov:specializationOf <https://github.com/timrdf/DataFAQs/tree/master/bin/df-mirror-endpoint.sh> .
#

HOME=$(cd ${0%/*} && echo ${PWD%/*})
me=$(cd ${0%/*} && echo ${PWD})/`basename $0`

if [[ $# -lt 0 || "$1" == "--help" ]]; then
   echo "usage: `basename $0` <endpoint>+"
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

for endpoint in $*; do
   endpoint_path=`noprotocolnohash $endpoint`
   echo $endpoint_path
   mkdir -p $endpoint_path/__PIVOT__
   df-named-graphs.py $endpoint > $endpoint_path/sdnames.csv
   for sdname in `cat $endpoint_path/sdnames.csv`; do
      pushd $endpoint_path/__PIVOT__ &> /dev/null
         sdname_path=`noprotocolnohash $sdname`
         echo "  $endpoint_path/__PIVOT__/$sdname_path"
         mkdir -p $sdname_path
         pushd $sdname_path &> /dev/null
            echo $sdname > sdname.csv
            cat $me.rq | perl -pi -e "s|SDNAME|$sdname|" > sdname.rq
            if [ ! -e sdname/sdname.rq.xml ]; then
               cache-queries.sh $endpoint -o xml -q sdname.rq -od sdname
            fi
            if [ ! -e inputs.csv ]; then
               saxon.sh $HOME/bin/get-binding.xsl a a -v name=input -in sdname/sdname.rq.xml > inputs.csv
            fi
            for input in `cat inputs.csv`; do
               hash=`md5.sh -qs $input`
               if [ ! -e input_$hash ]; then
                  pcurl.sh $input -n input_$hash
                  retrieved=`rename-by-syntax.sh -v input_$hash`
                  echo "<$retrieved> prov:alternateOf <input_$hash> ." >> input_$hash.pml.ttl
                  echo $sdname > $retrieved.sd_name
                  touch input_$hash
               fi
            done
         popd &> /dev/null
      popd &> /dev/null
   done
done
