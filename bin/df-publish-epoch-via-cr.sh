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

if [[ ! -e ../$epochID/source ]]; then
   mkdir -p ../$epochID/source
fi

rm -rf ../$epochID/source/*.rdf

for posted in `find __PIVOT_epoch/$epochID/__PIVOT_dataset -name post.nt.rdf`; do
   md5=`md5.sh -qs "$posted"`
   echo ln -s `pwd`/$posted ../$epochID/source/post-$md5.rdf
        ln -s `pwd`/$posted ../$epochID/source/post-$md5.rdf
done

for evaluation in `find __PIVOT_faqt -name evaluation.rdf | grep __PIVOT_epoch/$epochID`; do
   md5=`md5.sh -qs "$evaluation"`
   echo ln -s `pwd`/$evaluation ../$epochID/source/evaluation-$md5.rdf
        ln -s `pwd`/$evaluation ../$epochID/source/evaluation-$md5.rdf
done

pushd ../$epochID &> /dev/null
   aggregate-source-rdf.sh --compress --turtle --link-as-latest source/*.rdf
popd &> /dev/null
