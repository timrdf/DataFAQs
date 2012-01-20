#!/bin/bash

# rapper -g -c b.ttl 
# rapper: Parsing returned 17 triples

count=0
while [ $# -gt 0 ]; do
   file="$1"
   if [ -e $file ]; then
      c=`rapper -g -c $file 2>&1 | grep "Parsing returned [^ ]* triples" | awk '{printf($4)}'`
      if [ ${#c} -gt 0 ]; then
         let "count=count+c"
      fi
   fi
   shift
done
echo $count
