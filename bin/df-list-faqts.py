#!/usr/bin/python
#
# Output an RDF description of all FAqT evaluation service implementations
# nested within the current directory.
#
# The output can be used as a service registery, and can be used to synchronize
# with others' registeries.
#
# Example usage:
#
#    cd DataFAQs/services/sadi
#    df-list-faqts.py > all.ttl
#    rapper -qg -o rdfxml all.ttl > all.rdf
#    git add all.*

import os, fnmatch

implementations = []
for root, dirnames, filenames in os.walk('.'):
  for filename in fnmatch.filter(filenames, '*.py'):
      implementations.append(os.path.join(root, filename))

omit = {
   'path' : [ 'faqt-template', 'core/cross' ],
   'base' : [ 'test', 'ckan', 'contextual-inverse-functional', 'prov', 'util' ]
}

print '@prefix datafaqs: <http://purl.org/twc/vocab/datafaqs#> .'
print

# ./core/select-datasets/via-sparql-query.py
for implementation in implementations:
   path = implementation.replace('./','').replace('.py','')

   blacklisted = path in omit['path']
   for base in omit['base']:
      blacklisted = blacklisted or path.startswith(base)

   if not blacklisted:
      print '<'+path+'>' + ' a datafaqs:SADIService',

      if path.startswith('faqt'):
         print ', datafaqs:FAqTService',

      if path.startswith('core'):
         print ', datafaqs:CoreService',

      if path.startswith('core/select-faqts'):
         print ', datafaqs:FAqTSelector',

      if path.startswith('core/select-datasets'):
         print ', datafaqs:DatasetSelector',

      if path.startswith('core/augment-datasets/by-reference'):
         print ', datafaqs:DatasetReferencer',

      print ' .'

# http://aquarius.tw.rpi.edu/projects/datafaqs/services/sadi/core/select-datasets/via-sparql-query
#                                                          ./core/select-datasets/via-sparql-query.py

