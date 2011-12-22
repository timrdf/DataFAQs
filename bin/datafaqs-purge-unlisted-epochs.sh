#!/bin/bash
#
# https://github.com/timrdf/DataFAQs/blob/master/bin/datafaqs-purge-unlisted-epochs.sh
# 

if [[ "$1" == "--help" || $# -ne 1 ]]; then
   echo "usage: `basename $0` <-n | -w>"
   echo
   echo "  -n: perform dry run; do not modify anything."
   echo "  -w: remove all epochs that are not listed in datafaqs.localhost/epochs/"
   exit 0
fi

# Enforce directory conventions
if [ `basename \`pwd\`` != "faqt-brick" ]; then
   echo "`basename $0` must be initiated at the faqt-brick root."
   echo "See https://github.com/timrdf/DataFAQs/wiki/FAqT-Brick"
   exit 1
fi

INFO="(dry run) [INFO]"
dryrun="true"
if [ "$1" == "-w" ]; then
   dryrun="false"
   INFO="[INFO]"
   shift
fi

keep_these="`pwd`/datafaqs.localhost/epochs/"

for pivot_epoch in `find . -name "__PIVOT_epoch"`; do
   pushd $pivot_epoch &> /dev/null
      for epoch in `$CSV2RDF4LOD_HOME/bin/util/directories.sh`; do
         if [ ! -d $keep_these/$epoch ]; then
            echo "$INFO Removing $epoch"
            if [ "$dryrun" == "false" ]; then
               rm -rf $epoch
            fi
         fi
      done
   popd &> /dev/null
done
