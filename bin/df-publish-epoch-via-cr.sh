#!/bin/bash
#
#3> <> prov:specializationOf <https://github.com/timrdf/DataFAQs/tree/master/bin/df-publish-epoch-via-cr.sh>;
#3>    rdfs:seeAlso          <https://github.com/timrdf/DataFAQs/wiki/Situating-a-FAqT-Brick-into-csv2rdf4lod-automation> .
#

if [[ $# -lt 1 || "$1" == "--help" || "$1" == "-h" ]]; then
   echo "usage: `basename $0` [-n] <epoch>"
   echo
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

dryrun="false"
if [ "$1" == "-n" ]; then
   dryrun="true"
   shift
fi

epochID=${1%'/'}
epochID=${epochID#'__PIVOT_epoch/'}

echo $epochID >&2

if [ "$dryrun" != "true" ]; then
   if [[ ! -e ../$epochID/source ]]; then
      mkdir -p ../$epochID/source
   fi

   rm -rf ../$epochID/source/*.rdf
   rm -rf ../$epochID/source/*.ttl
fi

echo ln -s `pwd`/__PIVOT_epoch/$epochID/epoch.ttl             ../$epochID/source/
echo ln -s `pwd`/__PIVOT_epoch/$epochID/datasets.ttl.rdf      ../$epochID/source/
echo ln -s `pwd`/__PIVOT_epoch/$epochID/faqt-services.ttl.rdf ../$epochID/source/
if [ "$dryrun" != "true" ]; then
   ln -s `pwd`/__PIVOT_epoch/$epochID/epoch.ttl             ../$epochID/source/
   ln -s `pwd`/__PIVOT_epoch/$epochID/datasets.ttl.rdf      ../$epochID/source/
   ln -s `pwd`/__PIVOT_epoch/$epochID/faqt-services.ttl.rdf ../$epochID/source/
fi

# Total dataset descriptions, the RDF POSTed to FAqT Services.
for posted in `find __PIVOT_epoch/$epochID/__PIVOT_dataset -name post.nt.rdf`; do
   md5=`md5.sh -qs "$posted"`
   echo ln -s `pwd`/$posted ../$epochID/source/post-$md5.rdf
   if [ "$dryrun" != "true" ]; then
        ln -s `pwd`/$posted ../$epochID/source/post-$md5.rdf
   fi
done

# The FAqT Services' responses. TODO: must it be .rdf extension?
for evaluation in `find __PIVOT_faqt -name evaluation.rdf | grep __PIVOT_epoch/$epochID`; do
   md5=`md5.sh -qs "$evaluation"`
   echo ln -s `pwd`/$evaluation ../$epochID/source/evaluation-$md5.rdf
   if [ "$dryrun" != "true" ]; then
        ln -s `pwd`/$evaluation ../$epochID/source/evaluation-$md5.rdf
   fi
done

# The FAqT Services' self-descriptions (and our add-on independent of the version).
for service in `find __PIVOT_faqt/ -name "faqt-service.ttl" | grep __PIVOT_epoch/$epochID`; do
   md5=`md5.sh -qs "$service"`
   echo ln -s `pwd`/$service ../$epochID/source/service-$md5.ttl
   if [ "$dryrun" != "true" ]; then
        ln -s `pwd`/$service ../$epochID/source/service-$md5.ttl
   fi
   versionless=${service%%/__PIVOT_epoch*}/service.ttl
   ls -lt $versionless
done

if [ "$dryrun" != "true" ]; then
   pushd ../$epochID &> /dev/null
      aggregate-source-rdf.sh --compress --turtle --link-as-latest source/*.rdf
   popd &> /dev/null
fi
