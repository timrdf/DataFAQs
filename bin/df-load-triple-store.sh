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
# 
# if DATAFAQS_PUBLISH_SESAME = true, publish into
#    DATAFAQS_PUBLISH_SESAME_SERVER 's
#    DATAFAQS_PUBLISH_SESAME_REPOSITORY_ID USING
#    DATAFAQS_PUBLISH_SESAME_HOME/bin/console.sh

see='https://github.com/timrdf/DataFAQs/wiki/Installing-DataFAQs'
DATAFAQS_HOME=${DATAFAQS_HOME:?"not set; see $see"}
#see='https://github.com/timrdf/DataFAQs/wiki/DATAFAQS-environment-variables'
#DATAFAQS_LOG_DIR=${DATAFAQS_LOG_DIR:?"not set; see $see"}

log="/dev/null"
if [ $DATAFAQS_LOG_DIR != "/dev/null" ]; then
   log=$DATAFAQS_LOG_DIR/`basename $0`/log.txt
   if [ ! -e `dirname $log` ]; then
      mkdir -p `dirname $log`
   fi
fi

if [[ $# -lt 1 || "$1" == "--help" ]]; then
   echo "usage: `basename $0` (--target | --recursive-by-sd-name | [--graph graph-name] ( --recursive-meta | file ) )"
   echo ""
   echo "    --target               : print triple store destination information and quit."
   echo "    --recursive-by-sd-name : find all RDF files ending in .sd_name and load the corresponding file into the graph specified."
   echo "    --graph                : load the RDF file into 'graph-name'."
   echo "    --recursive-meta       : load all files ending in '.meta.ttl'."
   exit 1
fi

if [[ "$1" == "--target" ]]; then
   if [ "$DATAFAQS_PUBLISH_TDB" == "true" ]; then
      echo tdbloader --loc=$DATAFAQS_PUBLISH_TDB_DIR
      if [ ${#DATAFAQS_PUBLISH_TDB_DIR} -eq 0 ]; then
         echo "WARNING: DATAFAQS_PUBLISH_TDB_DIR must be set"
      fi
   elif [ "$DATAFAQS_PUBLISH_VIRTUOSO" == "true" ]; then
      $CSV2RDF4LOD_HOME/bin/util/virtuoso/vload --target
   elif [ "$DATAFAQS_PUBLISH_SESAME" == "true" ]; then
      if [ ! -e "$DATAFAQS_PUBLISH_SESAME_HOME/bin/console.sh" ]; then
         echo "WARNING: cannot find $DATAFAQS_PUBLISH_SESAME_HOME/bin/console.sh; set DATAFAQS_PUBLISH_SESAME_HOME?"
      fi
      if [ -z "$DATAFAQS_PUBLISH_SESAME_SERVER" ]; then
         echo "WARNING: no sesame server set in DATAFAQS_PUBLISH_SESAME_SERVER; e.g. http://localhost:8080/openrdf-sesame"
      fi
      if [ -z "$DATAFAQS_PUBLISH_SESAME_REPOSITORY_ID" ]; then
         echo "WARNING: no sesame repository id set in DATAFAQS_PUBLISH_SESAME_REPOSITORY_ID"
      fi
      echo "[INFO] Will load named graphs into repository $DATAFAQS_PUBLISH_SESAME_REPOSITORY_ID on $DATAFAQS_PUBLISH_SESAME_SERVER via $DATAFAQS_PUBLISH_SESAME_HOME/bin/console.sh"
   elif [ "$DATAFAQS_PUBLISH_ALLEGROGRAPH" == "true" ]; then
      echo todo allegrograph --target
   else
      echo "DATAFAQS_PUBLISH_TDB, DATAFAQS_PUBLISH_VIRTUOSO, DATAFAQS_PUBLISH_SESAME, and DATAFAQS_PUBLISH_ALLEGROGRAPH all false, will not publish."
   fi
   exit
fi

if [ "$1" == "--recursive-by-sd-name" ]; then
   name_paths=`find . -name "*.sd_name"`
   total=`cat $name_paths | wc -l | awk '{print $1}'`
   n=0
   for name_path in $name_paths; do
      let "n=n+1"
      pushd `dirname $name_path` &> /dev/null
         name=`basename $name_path` 
         rdf=${name%.sd_name}
         if [ -e $rdf ]; then
            echo "($n/$total) `cat $name` <- $rdf"
            $0 --graph `cat $name` $rdf
         else
            echo "[WARNING] could not find $rdf for $name"
         fi
      popd &> /dev/null
   done
   exit
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

if [ "$1" == "--recursive-meta" ]; then
   meta_paths=`find . -name "*.meta.ttl"`
   for meta in $meta_paths; do
      echo $meta
      if [ ${#graph} -gt 0 ]; then
         $0 --graph $graph $meta
      else
         $0 $meta
      fi
   done
else
   file="$1"

   if [ "$DATAFAQS_PUBLISH_TDB" == "true" ]; then

      if [ ! `which tdbloader` ]; then
         echo "[WARNING] tdbloader not on path; skipping tdb triple store load."
      fi
      if [[ ${#DATAFAQS_PUBLISH_TDB_DIR} -gt 0 ]]; then
         if [[ -d "$DATAFAQS_PUBLISH_TDB_DIR" ]]; then
            if [ ${#graph} -gt 0 ]; then
               echo >> $log
               pwd  >> $log
               echo "tdbloader --loc=$DATAFAQS_PUBLISH_TDB_DIR --graph=$graph $file" 2>> $log 1>> $log
                     tdbloader --loc=$DATAFAQS_PUBLISH_TDB_DIR --graph=$graph $file  2>> $log 1>> $log
            else
               echo >> $log
               pwd  >> $log
               echo "tdbloader --loc=$DATAFAQS_PUBLISH_TDB_DIR $file" 2>> $log 1>> $log
                     tdbloader --loc=$DATAFAQS_PUBLISH_TDB_DIR $file  2>> $log 1>> $log
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
      echo $CSV2RDF4LOD_HOME/bin/util/virtuoso/vload `guess-syntax.sh --inspect $file vload` $file $graph 2>> $log 1>> $log
           $CSV2RDF4LOD_HOME/bin/util/virtuoso/vload `guess-syntax.sh --inspect $file vload` $file $graph 2>> $log 1>> $log

   elif [ "$DATAFAQS_PUBLISH_SESAME" == "true" ]; then

      if [ -z "$DATAFAQS_PUBLISH_SESAME_SERVER" ]; then
         echo "[ERROR] DATAFAQS_PUBLISH_SESAME_SERVER not set."
      elif [ -z "$DATAFAQS_PUBLISH_SESAME_REPOSITORY_ID" ]; then
         echo "[ERROR] DATAFAQS_PUBLISH_SESAME_REPOSITORY_ID not set."
      elif [ ! -e $DATAFAQS_PUBLISH_SESAME_HOME/bin/console.sh ]; then
         echo "[ERROR] DATAFAQS_PUBLISH_SESAME_HOME/bin/console.sh does not exist.."
      else
         echo "connect $DATAFAQS_PUBLISH_SESAME_SERVER ."      > load.sc # TODO: pipe to log.
         echo "open $DATAFAQS_PUBLISH_SESAME_REPOSITORY_ID ." >> load.sc
         echo "load $file into $graph ."                      >> load.sc
         echo "exit ."                                        >> load.sc
         $DATAFAQS_PUBLISH_SESAME_HOME/bin/console.sh          < load.sc

         echo "connect $DATAFAQS_PUBLISH_SESAME_SERVER ."      > clear.sc
         echo "open $DATAFAQS_PUBLISH_SESAME_REPOSITORY_ID ." >> clear.sc
         echo "clear $graph ."                                >> clear.sc
         echo "exit ."                                        >> clear.sc
      fi

   elif [ "$DATAFAQS_PUBLISH_ALLEGROGRAPH" == "true" ]; then
      echo TODO ag
   fi
fi
