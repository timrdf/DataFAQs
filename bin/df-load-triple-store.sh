#!/bin/bash
#
# if DATAFAQS_PUBLISH_TDB = true, publish into
#     DATAFAQS_PUBLISH_TDB_DIR
#
# if DATAFAQS_PUBLISH_VIRTUOSO = true publishes into 
#     CSV2RDF4LOD_PUBLISH_VIRTUOSO_PORT
#     using
#     CSV2RDF4LOD_PUBLISH_VIRTUOSO_ISQL_PATH
#     CSV2RDF4LOD_PUBLISH_VIRTUOSO_USERNAME
#     CSV2RDF4LOD_PUBLISH_VIRTUOSO_PASSWORD

log=$DATAFAQS_LOG_DIR/`basename $0`/log.txt
if [ ! -e `dirname $log` ]; then
   mkdir -p `dirname $log`
fi

if [[ $# -lt 1 || "$1" == "--help" ]]; then
   echo "usage: `basename $0` ( --recursive-by-sd-name | [--graph graph-name] file )"
   exit 1
fi

name_paths=`find . -name "*.sd_name"`
total=`cat $name_paths | wc -l | awk '{print $1}'`
if [ "$1" == "--recursive-by-sd-name" ]; then
   n=0
   for name_path in $name_paths; do
      let "n=n+1"
      pushd `dirname $name_path` &> /dev/null
         name=`basename $name_path` 
         rdf=${name%.sd_name}
         if [ -e $rdf ]; then
            echo "($n/$total)"
            $0 --graph `cat $name` $rdf
         else
            echo "[WARNING] could not find $rdf for $name"
         fi
      popd &> /dev/null
   done
fi

graph=""
if [ "$1" == "--graph" ]; then
   if [ $# -gt 1 ]; then
      graph="$2"
      shift 2
   else
      echo "[ERROR] missing value for --graph"
      exit
   fi
fi

file="$1"
shift

if [ "$DATAFAQS_PUBLISH_TDB" == "true" ]; then

   if [ ! `which tdbloader` ]; then
      echo "tdbloader not on path; skipping tdb triple store load."
   fi
   if [[ ${#DATAFAQS_PUBLISH_TDB_DIR} -gt 0 ]]; then
      if [[ -d "$DATAFAQS_PUBLISH_TDB_DIR" ]]; then
         if [ ${#graph} -gt 0 ]; then
            echo >> $log
            pwd >> $log
            echo tdbloader --loc=$DATAFAQS_PUBLISH_TDB_DIR --graph=$graph $file 2>> $log 1>> $log
            tdbloader --loc=$DATAFAQS_PUBLISH_TDB_DIR --graph=$graph $file      2>> $log 1>> $log
         else
            echo >> $log
            pwd >> $log
            echo tdbloader --loc=$DATAFAQS_PUBLISH_TDB_DIR $file 2>> $log 1>> $log
            tdbloader --loc=$DATAFAQS_PUBLISH_TDB_DIR $file      2>> $log 1>> $log
         fi
      else
         echo "$DATAFAQS_PUBLISH_TDB_DIR does not exist; skipping tdb triple store load."
      fi
   else
      echo DATAFAQS_PUBLISH_TDB_DIR not set, trying to use context to find a tdb directory.
   fi

elif [ "$DATAFAQS_PUBLISH_VIRTUOSO" == "true" ]; then

   # CSV2RDF4LOD_PUBLISH_VIRTUOSO_PORT
   # using
   # CSV2RDF4LOD_PUBLISH_VIRTUOSO_ISQL_PATH
   # CSV2RDF4LOD_PUBLISH_VIRTUOSO_USERNAME
   # CSV2RDF4LOD_PUBLISH_VIRTUOSO_PASSWORD
   # CSV2RDF4LOD_CONVERT_DATA_ROOT

   # usage: vload [--target] {rdf, ttl, nt, nq} <data_file> <graph_uri> [-v | --verbose]
   $CSV2RDF4LOD_HOME/bin/util/virtuoso/vload `guess-syntax.sh --inspect $file vload` $file $graph 2>> $log 1>> $log

elif [ "$DATAFAQS_PUBLISH_ALLEGROGRAPH" == "true" ]; then

   echo TODO ag
fi
