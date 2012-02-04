export DATAFAQS_HOME="/opt/DataFAQs"
export PATH=$PATH`$DATAFAQS_HOME/bin/df-situate-paths.sh`

# Project settings
export DATAFAQS_BASE_URI="http://aquarius.tw.rpi.edu/projects/datafaqs"
export DATAFAQS_LOG_DIR="`pwd`/log"
export DATAFAQS_PUBLISH_TDB="true"
export DATAFAQS_PUBLISH_TDB_DIR="`pwd`/tdb"
export DATAFAQS_PUBLISH_THROUGHOUT_EPOCH="true"
export DATAFAQS_PUBLISH_METADATA_GRAPH_NAME="http://www.w3.org/ns/sparql-service-description#NamedGraph"

# Software dependencies: 
export CSV2RDF4LOD_HOME="/opt/csv2rdf4lod-automation"
export PATH=$PATH`$CSV2RDF4LOD_HOME/bin/util/cr-situate-paths.sh`

export TDBROOT="/opt/tdb/TDB-0.8.10"
if [ ! `which tdbloader` ]; then
   export PATH=$PATH":$TDBROOT/bin"
fi
