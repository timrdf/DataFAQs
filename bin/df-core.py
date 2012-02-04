#!/usr/bin/env python
#
# https://github.com/timrdf/DataFAQs/blob/master/bin/df-core.py
#
# Enumerate the FAqTSelector(s) and DatasetSelector(s) involved in the epoch described in the given RDF file (i.e. "epoch configuration file").
#    (optionally, include the URIs of the inputs that should be given to the Selectors)
#
# Enumerate the datasets returned by the DatasetSelector

import sys
from rdflib import *

from surf import *
from surf.query import a, select

import rdflib
rdflib.plugin.register('sparql', rdflib.query.Processor,
                       'rdfextras.sparql.processor', 'Processor')
rdflib.plugin.register('sparql', rdflib.query.Result,
                       'rdfextras.sparql.query', 'SPARQLQueryResult')

if len(sys.argv) != 3:
   print "usage: df-core.py epoch.ttl {faqt-selectors, dataset-selectors, dataset-augmenters}"
   print "  epoch.ttl          - an RDF description of the services to invoke with which inputs."
   print "  faqt-selectors     - print <service_uri> <input_uri> (one per line)."
   print "  dataset-selectors  - print <service_uri> <input_uri> (one per line)."
   print "  dataset-augmenters - print <service_uri> <input_uri> (one per line)."
   sys.exit(1)

ns.register(prov='http://www.w3.org/ns/prov-o/')
ns.register(dcat='http://www.w3.org/ns/dcat#')
ns.register(void='http://rdfs.org/ns/void#')
ns.register(datafaqs='http://purl.org/twc/vocab/datafaqs#')

epoch = sys.argv[1]
type  = sys.argv[2]

#store   = Store(reader='rdflib', writer='rdflib', rdflib_store = 'IOMemory')
#session = Session(store)
#store.load_triples(source=epoch,  format="n3")
#query = select("?service", "?input").where( ("?service", a, surf.ns.DATAFAQS['FAqTService']))
#results = session.default_store.execute(query)

prefixes = dict(prov=str(ns.PROV),
                datafaqs=str(ns.DATAFAQS),
                dcat=str(ns.DCAT),
                void=str(ns.VOID))

queries = {
   'faqt-selectors' : '''
select distinct ?service ?input where {
   [] 
      a prov:Activity;
      prov:used            ?input;
      prov:wasAttributedTo ?service;
   .
   ?service a datafaqs:FAqTSelector .
}
''',

   'dataset-selectors' : '''
select distinct ?service ?input where {
   [] 
      a prov:Activity;
      prov:used            ?input;
      prov:wasAttributedTo ?service;
   .
   ?service a datafaqs:DatasetSelector .
}
''',

   'dataset-augmenters' : '''
select distinct ?service where {
   ?service a datafaqs:DatasetReferencer .
}
''',

   'datasets' : '''
select distinct ?dataset ?type where {
   ?dataset a ?type .
   filter(?type = datafaqs:CKANDataset || ?type = void:Dataset)
}
''' # rdflib can't handle this query. # TODO: rework to only do dcat:Dataset.
}

graph = Graph()
#graph.parse(epoch, format="n3") # :: sigh ::
graph.parse(epoch)
results = graph.query(queries[type], initNs=prefixes)

if type == 'datasets':
   # Hack b/c rdflib can't handle the filter ||
   query = '''
select distinct ?dataset where {
   ?dataset a dcat:Dataset .
}
'''
   results = graph.query(query, initNs=prefixes)
   block = 1 # dear coding gods: I am so sorry.
   count = 0
   size = 50
   for bindings in results:
      if count == 0:
         if block > 1:
            post.close()
         filename = 'dataset-references.post.'+str(block)+'.ttl'
         if not(os.path.exists(filename)):
            print filename
            post = open(filename, 'w')
         else:
            print filename + " already exists. Not modifying."
      count += 1
      post.write('<' + bindings + '> a <http://www.w3.org/ns/dcat#Dataset> .\n')
      if count == size:
         count = 0
         block += 1

   # Hack b/c rdflib can't handle the filter ||
#   query = '''
#select distinct ?dataset where {
#   ?dataset a datafaqs:CKANDataset .
#}
#'''
#   results = graph.query(query, initNs=prefixes)
#   for bindings in results:
#      if count == 0:
#         if block > 1:
#            post.close()
#         filename = 'dataset-references.post.'+str(block)+'.ttl'
#         if not(os.path.exists(filename)):
#            print filename
#            post = open(filename, 'w')
#         else:
#            print filename + " already exists. Not modifying."
#      count += 1
#      post.write('<' + bindings + '> a <http://purl.org/twc/vocab/datafaqs#CKANDataset> .\n')
#      if count == size:
#         count = 0
#         block += 1

else: # faqt-selectors and dataset-selectors and dataset-augmenters
   for bindings in results:
      if len(bindings) == 2:
         print bindings[0] + ' ' + bindings[1]
      else:
         print bindings

