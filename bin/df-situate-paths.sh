#!/bin/bash
#
#3> <> prov:specializationOf <https://github.com/timrdf/DataFAQs/blob/master/bin/df-situate-paths.sh> .
#
# Usage:
#   export PATH=$PATH`$DATAFAQS_HOME/bin/df-situate-paths.sh`
#   (can be repeated indefinately, once paths are in PATH, nothing is returned.)

HOME=$(cd ${0%/*} && echo ${PWD%/*})

if [ "$1" == "--help" ]; then
   echo "`basename $0` [--help]"
   echo
   echo "Return the shell paths needed for DataFAQs scripts to run."
   echo "Set them executing:"
   echo
   echo "    export PATH=\$PATH\`$HOME/bin/${0##*/}\`"
   exit
fi

missing=""

if [ ! `which df-epoch.sh` ]; then
   missing=":"
   missing=$missing$HOME/bin
fi

if [[ ! `which tdbloader` && -d "$TDBROOT" ]]; then
   if [ ${#missing} -gt 0 ]; then
      missing=$missing":"
   fi
   missing=$missing$TDBROOT/bin
fi

#if [ ! `which pcurl.sh` ]; then export PATH=$PATH:$DATAFAQS_HOME/bin/util
#   if [ ${#missing} -gt 0 ]; then
#      missing=$missing":"
#   fi
#   missing=$missing$DATAFAQS_HOME/bin/util
#fi
#
#if [ ! `which vload` ]; then
#   if [ ${#missing} -gt 0 ]; then
#      missing=$missing":"
#   fi
#   missing=$missing$DATAFAQS_HOME/bin/util/virtuoso
#fi

echo $missing

#for path in `echo ${PATH//://  }`; do
#   echo $path
#done
