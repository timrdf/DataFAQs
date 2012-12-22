#!/bin/bash
#
#

if [ "$1" == "--check" ]; then
   if [ ! `which tdbloader` ]; then
      echo
      echo "[WARNING]: rapper not found on path. Publishing and many other things will fail."
   else
      echo
      echo "[INFO]: rapper found"
   fi
   if [[ ! `which tdbloader` || ! `which tdbquery` ]]; then
      echo
      echo "[WARNING]: tdbloader not found on path. Unit testing with cr-test-conversion.sh will fail."
   else
      echo
      echo "[INFO]: tdbloader and tdbquery found"
   fi
      echo
   exit 0
fi

if [ ${1:-"no"} != "CLEAR" ]; then
   show_all="no"
   if [ "$1" == "--all" ]; then
      show_all="yes";
   fi
   #echo "CLASSPATH                             $CLASSPATH"
   #echo "PATH                                  $PATH"

#   echo "  "
   echo "CSV2RDF4LOD_HOME                                      ${CSV2RDF4LOD_HOME:-"!!! -- MUST BE SET -- !!! source datafaqs-source-me.sh"}"
   echo "DATAFAQS_HOME                                         ${DATAFAQS_HOME:-"!!! -- MUST BE SET -- !!! source datafaqs-source-me.sh"}"
   echo "DATAFAQS_BASE_URI                                     ${DATAFAQS_BASE_URI:-"!!! -- MUST BE SET -- !!! source datafaqs-source-me.sh"}"
#   echo "DATAFAQS_BASE_URI_OVERRIDE                            ${DATAFAQS_BASE_URI_OVERRIDE:="(not required, \$DATAFAQS_BASE_URI will be used.)"}"
#   echo "  "
#   echo "DATAFAQS_CONVERT_MACHINE_URI                          ${DATAFAQS_CONVERT_MACHINE_URI:="(not required, but recommended! see https://github.com/timrdf/csv2rdf4lod-automation/wiki/DATAFAQS_CONVERT_PERSON_URI)"}"
#   echo "DATAFAQS_CONVERT_PERSON_URI                           ${DATAFAQS_CONVERT_PERSON_URI:="(not required, but recommended! see https://github.com/timrdf/csv2rdf4lod-automation/wiki/DATAFAQS_CONVERT_PERSON_URI)"}"

   echo "  "
   echo "DATAFAQS_LOG_DIR                                      ${DATAFAQS_LOG_DIR:="(not required)"}"
   echo "DATAFAQS_PROVENANCE_CODE_RAW_BASE                     ${DATAFAQS_PROVENANCE_CODE_RAW_BASE:="(Will omit prov:hadPlan upon service deref)"}"
   echo "DATAFAQS_PROVENANCE_CODE_PAGE_BASE                    ${DATAFAQS_PROVENANCE_CODE_PAGE_BASE:="(Will omit prov:hadPlan upon service deref)"}"

#   echo "DATAFAQS_CONVERT_OMIT_RAW_LAYER                       ${DATAFAQS_CONVERT_OMIT_RAW_LAYER:="(will default to: false)"}"
#   echo "DATAFAQS_CONVERT_SAMPLE_NUMBER_OF_ROWS                ${DATAFAQS_CONVERT_SAMPLE_NUMBER_OF_ROWS:="(will default to: 2)"}"
#   echo "DATAFAQS_CONVERT_SAMPLE_SUBSET_ONLY                   ${DATAFAQS_CONVERT_SAMPLE_SUBSET_ONLY:="(will default to: false)"}"
#   echo "DATAFAQS_CONVERT_EXAMPLE_SUBSET_ONLY                  ${DATAFAQS_CONVERT_EXAMPLE_SUBSET_ONLY:="(will default to: false)"}"
#   extensions=`dump-file-extensions.sh`
#   echo "DATAFAQS_CONVERT_DUMP_FILE_EXTENSIONS                 \"${DATAFAQS_CONVERT_DUMP_FILE_EXTENSIONS}\" => ${extensions:="(void:dataDump URLs will not have file extensions)"}"
#   echo "DATAFAQS_CONVERT_PROVENANCE_GRANULAR                  ${DATAFAQS_CONVERT_PROVENANCE_GRANULAR:="(will default to: false)"}"
#   echo "DATAFAQS_CONVERT_PROVENANCE_FRBR                      ${DATAFAQS_CONVERT_PROVENANCE_FRBR:="(will default to: false)"}"


#   echo "  "
#   echo "DATAFAQS_PUBLISH                                      ${DATAFAQS_PUBLISH:-"(will default to: true)"}"
#   echo "DATAFAQS_PUBLISH_DELAY_UNTIL_ENHANCED                 ${DATAFAQS_PUBLISH_DELAY_UNTIL_ENHANCED:-"(will default to: true)"}"

#   echo "DATAFAQS_PUBLISH_TTL                                  ${DATAFAQS_PUBLISH_TTL:-"(will default to: true)"}"
#   echo "DATAFAQS_PUBLISH_TTL_LAYERS                           ${DATAFAQS_PUBLISH_TTL_LAYERS:-"(will default to: true)"}"

#   echo "DATAFAQS_PUBLISH_NT                                   ${DATAFAQS_PUBLISH_NT:-"(will default to: false)"}"

#   echo "DATAFAQS_PUBLISH_RDFXML                               ${DATAFAQS_PUBLISH_RDFXML:-"(will default to: false)"}"
#   echo "DATAFAQS_PUBLISH_COMPRESS                             ${DATAFAQS_PUBLISH_COMPRESS:-"(will default to: false)"}"

#   echo "  "
#   echo "DATAFAQS_PUBLISH_SUBSET_VOID                          ${DATAFAQS_PUBLISH_SUBSET_VOID:="(will default to: true)"}"
#   echo "DATAFAQS_PUBLISH_SUBSET_VOID_NAMED_GRAPH              ${DATAFAQS_PUBLISH_SUBSET_VOID_NAMED_GRAPH:="(will default to: auto)"}"
#   echo "DATAFAQS_PUBLISH_SUBSET_SAMEAS                        ${DATAFAQS_PUBLISH_SUBSET_SAMEAS:="(will default to: false)"}"
#   echo "DATAFAQS_PUBLISH_SUBSET_SAMEAS_NAMED_GRAPH            ${DATAFAQS_PUBLISH_SUBSET_SAMEAS_NAMED_GRAPH:="(will default to: auto)"}"
#   echo "DATAFAQS_PUBLISH_SUBSET_SAMPLES                       ${DATAFAQS_PUBLISH_SUBSET_SAMPLES:="(will default to: false)"}"

#   echo "  "
#   echo "DATAFAQS_PUBLISH_OUR_SOURCE_ID                        ${DATAFAQS_PUBLISH_OUR_SOURCE_ID:="(will not archive conversion metadata into versioned dataset.)"}"
#   echo "DATAFAQS_PUBLISH_OUR_DATASET_ID                       ${DATAFAQS_PUBLISH_OUR_DATASET_ID:="(will not archive conversion metadata into versioned dataset.)"}"
#   echo "DATAFAQS_PUBLISH_CONVERSION_PARAMS_NAMED_GRAPH        ${DATAFAQS_PUBLISH_CONVERSION_PARAMS_NAMED_GRAPH:="(will default to: auto)"}"

#   echo "  "

#   echo "DATAFAQS_PUBLISH_LOD_MATERIALIZATION_WWW_ROOT         ${DATAFAQS_PUBLISH_LOD_MATERIALIZATION_WWW_ROOT:-"(will default to: VVV/publish/lod-mat/)"}"
#   echo "DATAFAQS_PUBLISH_VARWWW_DUMP_FILES                    ${DATAFAQS_PUBLISH_VARWWW_DUMP_FILES:-"(will default to: false)"}"
#   echo "DATAFAQS_PUBLISH_VARWWW_LINK_TYPE                     ${DATAFAQS_PUBLISH_VARWWW_LINK_TYPE:-"(will default to: hard)"}"
#   echo "DATAFAQS_PUBLISH_LOD_MATERIALIZATION                  ${DATAFAQS_PUBLISH_LOD_MATERIALIZATION:-"(will default to: false)"}"
#   if [ "$DATAFAQS_PUBLISH_LOD_MATERIALIZATION" == "true" -o $show_all == "yes" ]; then
#   echo "DATAFAQS_PUBLISH_LOD_MATERIALIZATION_WRITE_FREQUENCY  ${DATAFAQS_PUBLISH_LOD_MATERIALIZATION_WRITE_FREQUENCY:-"(will default to: 1,000,000)"}"
#
#   echo "DATAFAQS_PUBLISH_LOD_MATERIALIZATION_REPORT_FREQUENCY ${DATAFAQS_PUBLISH_LOD_MATERIALIZATION_REPORT_FREQUENCY:-"(will default to: 1,000)"}"
#
#   echo "DATAFAQS_CONCURRENCY                                  ${DATAFAQS_CONCURRENCY:-"(will default to: 1)"}"
#   else
#      echo "   ..."
#   fi

   echo "  "
   echo "DATAFAQS_PUBLISH_THROUGHOUT_EPOCH                     ${DATAFAQS_PUBLISH_THROUGHOUT_EPOCH:-"(will default to: false)"}"
   echo "DATAFAQS_PUBLISH_METADATA_GRAPH_NAME                  ${DATAFAQS_PUBLISH_METADATA_GRAPH_NAME:-"(will default to: http://www.w3.org/ns/sparql-service-description#NamedGraph)"}"
   echo
   echo "DATAFAQS_PUBLISH_TDB                                  ${DATAFAQS_PUBLISH_TDB:-"(will default to: false)"}"
   echo "DATAFAQS_PUBLISH_TDB_DIR                              ${DATAFAQS_PUBLISH_TDB_DIR:-"(will default to: VVV/publish/tdb/)"}"
   echo "JENAROOT                                              ${JENAROOT:-"(will default to: )"}"
#   echo "DATAFAQS_PUBLISH_TDB_INDIV                            ${DATAFAQS_PUBLISH_TDB_INDIV:-"(will default to: false)"}"

#   echo "  "
#   echo "DATAFAQS_PUBLISH_4STORE                               ${DATAFAQS_PUBLISH_4STORE:-"(will default to: false)"}"
#   if [ "$DATAFAQS_PUBLISH_4STORE" == "true" -o $show_all == "yes" ]; then
#   echo "DATAFAQS_PUBLISH_4STORE_KB                            ${DATAFAQS_PUBLISH_4STORE_KB:-"(will default to: csv2rdf4lod -- leading to /var/lib/4store/csv2rdf4lod)"}" 
#   else
#      echo "   ..."
#   fi

   echo "  "
   echo "DATAFAQS_PUBLISH_VIRTUOSO                             ${DATAFAQS_PUBLISH_VIRTUOSO:-"(will default to: false)"}"
                                                    virtuoso_home=${CSV2RDF4LOD_PUBLISH_VIRTUOSO_HOME:-"/opt/virtuoso"}
   if [ "$DATAFAQS_PUBLISH_VIRTUOSO" == "true" -o $show_all == "yes" ]; then
   echo "CSV2RDF4LOD_CONVERT_DATA_ROOT                         ${CSV2RDF4LOD_CONVERT_DATA_ROOT:-"(not required, but vload will copy files when loading)"}"
   echo "CSV2RDF4LOD_PUBLISH_VIRTUOSO_HOME                     ${CSV2RDF4LOD_PUBLISH_VIRTUOSO_HOME:-"(will default to: /opt/virtuoso)"}"
   echo "CSV2RDF4LOD_PUBLISH_VIRTUOSO_ISQL_PATH                ${CSV2RDF4LOD_PUBLISH_VIRTUOSO_ISQL_PATH:-"(will default to: $virtuoso_home/bin/isql)"}"
   echo "CSV2RDF4LOD_PUBLISH_VIRTUOSO_PORT                     ${CSV2RDF4LOD_PUBLISH_VIRTUOSO_PORT:-"(will default to: 1111)"}"
   echo "CSV2RDF4LOD_PUBLISH_VIRTUOSO_USERNAME                 ${CSV2RDF4LOD_PUBLISH_VIRTUOSO_USERNAME:-"(will default to: dba)"}"
   echo "CSV2RDF4LOD_PUBLISH_VIRTUOSO_PASSWORD                 ${CSV2RDF4LOD_PUBLISH_VIRTUOSO_PASSWORD:-"(will default to: dba)"}"
   else
      echo "..."
   fi
   echo "  "
   echo "DATAFAQS_PUBLISH_SESAME                               ${DATAFAQS_PUBLISH_SESAME:-"(will default to: false)"}"
   if [ "$DATAFAQS_PUBLISH_SESAME" == "true" -o $show_all == "yes" ]; then
   echo "DATAFAQS_PUBLISH_SESAME_HOME                          ${DATAFAQS_PUBLISH_SESAME_HOME:-"(!!! REQUIRED to publish sesame !!!)"}"
   echo "DATAFAQS_PUBLISH_SESAME_SERVER                        ${DATAFAQS_PUBLISH_SESAME_SERVER:-"(!!! REQUIRED to publish sesame !!!)"}"
   echo "DATAFAQS_PUBLISH_SESAME_REPOSITORY_ID                 ${DATAFAQS_PUBLISH_SESAME_REPOSITORY_ID:-"(!!! REQUIRED to publish sesame !!!)"}"
   else
      echo "..."
   fi
   echo "  "
   echo "CSV2RDF4LOD_CONCURRENCY                               ${CSV2RDF4LOD_CONCURRENCY:-"(will default to: 1)"}"
   echo "X_CKAN_API_Key                                        ${X_CKAN_API_Key:-"(FAqT services will not be able to talk to CKAN!)"}"
#   echo "DATAFAQS_PUBLISH_VIRTUOSO_INI_PATH                    ${DATAFAQS_PUBLISH_VIRTUOSO_INI_PATH:-"(will default to: $virtuoso_home/var/lib/virtuoso/db/virtuoso.ini)"}"
#   echo "DATAFAQS_PUBLISH_VIRTUOSO_SCRIPT_PATH                 ${DATAFAQS_PUBLISH_VIRTUOSO_SCRIPT_PATH:-"(DEPRECATED. will default to: /opt/virtuoso/scripts/vload)"}"
#   else
#      echo "   ..."
#   fi 
#   echo "DATAFAQS_PUBLISH_VIRTUOSO_SPARQL_ENDPOINT             ${DATAFAQS_PUBLISH_VIRTUOSO_SPARQL_ENDPOINT:-"(will fail to describe provenance in pvload.sh)"}"

#   echo "  "
#   echo "DATAFAQS_PUBLISH_SPARQL_ENDPOINT                      ${DATAFAQS_PUBLISH_VIRTUOSO:-"(will default to: none)"}"
#   echo "DATAFAQS_PUBLISH_SPARQL_RESULTS_DIRECTORY             ${DATAFAQS_PUBLISH_VIRTUOSO:-"(will default to: none)"}"

   if [ ${#DATAFAQS_HOME} -gt 0 ]; then
      echo "  "
      echo "see documentation for variables in: https://github.com/timrdf/DataFAQs/wiki/DATAFAQS-environment-variables"
   fi
else

   echo "clearing..."
   export DATAFAQS_HOME=""
   export DATAFAQS_BASE_URI=""
   export DATAFAQS_BASE_URI_OVERRIDE=""           

   export DATAFAQS_CONVERT_MACHINE_URI=""           
   export DATAFAQS_CONVERT_PERSON_URI=""           

   export DATAFAQS_LOG_DIR=""
   export DATAFAQS_CONVERT_OMIT_RAW_LAYER=""
   export DATAFAQS_CONVERT_SAMPLE_NUMBER_OF_ROWS=""
   export DATAFAQS_CONVERT_SAMPLE_SUBSET_ONLY=""
   export DATAFAQS_CONVERT_EXAMPLE_SUBSET_ONLY=""
   export DATAFAQS_CONVERT_DUMP_FILE_EXTENSIONS=""
   export DATAFAQS_CONVERT_PROVENANCE_GRANULAR=""
   export DATAFAQS_CONVERT_PROVENANCE_FRBR=""
   export DATAFAQS_CONVERT_DEBUG_LEVEL=""
   # "  "

   export DATAFAQS_PUBLISH=""
   export DATAFAQS_PUBLISH_DELAY_UNTIL_ENHANCED=""
   export DATAFAQS_PUBLISH_TTL=""
   export DATAFAQS_PUBLISH_TTL_LAYERS=""
   export DATAFAQS_PUBLISH_NT=""
   export DATAFAQS_PUBLISH_RDFXML=""
   export DATAFAQS_PUBLISH_COMPRESS=""
   # "  "
   export DATAFAQS_PUBLISH_SUBSET_VOID=""
   export DATAFAQS_PUBLISH_SUBSET_VOID_NAMED_GRAPH=""
   export DATAFAQS_PUBLISH_SUBSET_SAMEAS=""
   export DATAFAQS_PUBLISH_SUBSET_SAMEAS_NAMED_GRAPH=""
   export DATAFAQS_PUBLISH_SUBSET_SAMPLES=""
   # "  "
   export DATAFAQS_PUBLISH_OUR_SOURCE_ID=""
   export DATAFAQS_PUBLISH_OUR_DATASET_ID=""
   export DATAFAQS_PUBLISH_CONVERSION_PARAMS_NAMED_GRAPH=""
   export DATAFAQS_PUBLISH_VARWWW_DUMP_FILES=""
   export DATAFAQS_PUBLISH_VARWWW_LINK_TYPE=""
   # "  "
   export DATAFAQS_PUBLISH_LOD_MATERIALIZATION=""
   export DATAFAQS_PUBLISH_LOD_MATERIALIZATION_WWW_ROOT=""
   export DATAFAQS_PUBLISH_LOD_MATERIALIZATION_WRITE_FREQUENCY=""
   export DATAFAQS_PUBLISH_LOD_MATERIALIZATION_REPORT_FREQUENCY=""
   export DATAFAQS_CONCURRENCY=""
   # "  "
   export DATAFAQS_PUBLISH_TDB=""
   export DATAFAQS_PUBLISH_TDB_DIR=""

   export DATAFAQS_PUBLISH_TDB_INDIV=""

   # "  "
   export DATAFAQS_PUBLISH_4STORE=""
   export DATAFAQS_PUBLISH_4STORE_KB=""
   
   # "  "
   export DATAFAQS_PUBLISH_VIRTUOSO=""
   export DATAFAQS_PUBLISH_VIRTUOSO_HOME=""
   export DATAFAQS_PUBLISH_VIRTUOSO_ISQL_PATH=""
   export DATAFAQS_PUBLISH_VIRTUOSO_PORT=""
   export DATAFAQS_PUBLISH_VIRTUOSO_USERNAME=""
   export DATAFAQS_PUBLISH_VIRTUOSO_PASSWORD=""
   export DATAFAQS_PUBLISH_VIRTUOSO_INI_PATH=""
   export DATAFAQS_PUBLISH_VIRTUOSO_SCRIPT_PATH=""
   export DATAFAQS_PUBLISH_VIRTUOSO_SPARQL_ENDPOINT=""

   export DATAFAQS_PUBLISH_SESAME=""
   export DATAFAQS_PUBLISH_SESAME_HOME=""
   export DATAFAQS_PUBLISH_SESAME_SERVER=""
   export DATAFAQS_PUBLISH_SESAME_REPOSITORY_ID=""
   # "  "
   export DATAFAQS_PUBLISH_SPARQL_ENDPOINT=""       
   export DATAFAQS_PUBLISH_SPARQL_RESULTS_DIRECTORY=""
   
   echo "...cleared."
   $0 # Run this script again to show that they were cleared.
fi
