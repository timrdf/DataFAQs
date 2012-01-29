#!/bin/bash

if [[ $# -lt 1 || "$1" == "--help" ]]; then
   echo "usage: `basename $0` url"
   exit 1
fi

while [ $# -gt 0 ]; do
   uri="$1"
   echo "no Accept:"
   curl --silent -L $uri | head
   for content_type in 'application/rdf+xml' 'text/turtle' 'text/plain'; do
      echo; echo; echo; echo; echo;
      echo $content_type
      echo curl --silent -H "\"Accept: $content_type\"" -L $uri
      curl --silent -H "\"Accept: $content_type\"" -L $uri | head
   done
   shift
done
