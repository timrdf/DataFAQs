#!/usr/bin/env python
#
#

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
   print "usage: df-core.py epoch.ttl {faqt-services, datasets, dataset-augmenters}"
   print "  epoch.ttl          - an RDF description of the services to invoke with which inputs."
   print "  faqt-services      - print <service_uri> <input_uri> (one per line)."
   print "  datasets           - print <service_uri> <input_uri> (one per line)."
   print "  dataset-augmenters - print <service_uri> <input_uri> (one per line)."
   sys.exit(1)

ns.register(prov='http://www.w3.org/ns/prov-o/')
ns.register(datafaqs='http://purl.org/twc/vocab/datafaqs#')

epoch = sys.argv[1]
type  = sys.argv[2]

#store   = Store(reader='rdflib', writer='rdflib', rdflib_store = 'IOMemory')
#session = Session(store)
#store.load_triples(source=epoch,  format="n3")
#query = select("?service", "?input").where( ("?service", a, surf.ns.DATAFAQS['FAqTService']))
#results = session.default_store.execute(query)

prefixes = dict(prov=str(ns.PROV),datafaqs=str(ns.DATAFAQS))

queries = {
   'faqt-services' : '''
select distinct ?service ?input where {
   [] 
      a prov:Activity;
      prov:used            ?input;
      prov:wasAttributedTo ?service;
   .
   ?service a datafaqs:FAqTSelector .
}
''',

   'datasets' : '''
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
'''
}

graph = Graph()
#graph.parse(epoch, format="n3") # :: sigh ::
graph.parse(epoch)
results = graph.query(queries[type], initNs=prefixes)

for bindings in results:
   if len(bindings) == 2:
      print bindings[0] + ' ' + bindings[1]
   else:
      print bindings
