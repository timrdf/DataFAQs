#!/bin/bash
#
#3> <> prov:specializationOf <https://github.com/timrdf/DataFAQs/tree/master/bin/df-publish-epoch-via-cr.sh> .
#

if [[ $# -lt 1 || "$1" == "--help" || "$1" == "-h" ]]; then
   echo "usage: `basename $0` <epoch>"
   echo "  Create publish/bin/publish.sh and invoke for every conversion cockpit within the current directory tree."
   echo "           <epoch> : e.g __PIVOT_epoch/2013-06-22/, 2013-06-22"
   exit
fi

# cr:data-root cr:source cr:directory-of-datasets cr:dataset cr:directory-of-versions cr:conversion-cockpit
ACCEPTABLE_PWDs="cr:conversion-cockpit"
if [ `${CSV2RDF4LOD_HOME}/bin/util/is-pwd-a.sh $ACCEPTABLE_PWDs` != "yes" ]; then
   echo `pwd` `cr-pwd.sh` `cr-pwd-type.sh` `${CSV2RDF4LOD_HOME}/bin/util/is-pwd-a.sh $ACCEPTABLE_PWDs`
   ${CSV2RDF4LOD_HOME}/bin/util/pwd-not-a.sh $ACCEPTABLE_PWDs
   exit 1
fi

epochID=${1%'/'}
epochID=${epochID#'__PIVOT_epoch/'}

echo $epochID

if [[ ! -e ../$epochID ]]; then
   mkdir -p ../$epochID
fi

find __PIVOT_epoch/$epochID/__PIVOT_dataset -name post.nt.rdf

find __PIVOT_faqt -name evaluation.rdf | grep __PIVOT_epoch/$epochID

