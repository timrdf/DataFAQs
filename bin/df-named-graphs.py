#!/usr/bin/env python

import sys
from rdflib import *

from surf import *
from surf.query import a, select

import rdflib
rdflib.plugin.register('sparql', rdflib.query.Processor,
                       'rdfextras.sparql.processor', 'Processor')
rdflib.plugin.register('sparql', rdflib.query.Result,
                       'rdfextras.sparql.query', 'SPARQLQueryResult')

ns.register(prov='http://www.w3.org/ns/prov-o/')
ns.register(dcat='http://www.w3.org/ns/dcat#')
ns.register(void='http://rdfs.org/ns/void#')
ns.register(datafaqs='http://purl.org/twc/vocab/datafaqs#')

if len(sys.argv) < 2:
   print "usage: df-named-graphs.py endpoint"
   sys.exit

endpoint = sys.argv[1]

store = Store( reader = "sparql_protocol",
               writer = "sparql_protocol",
               endpoint = endpoint)
results = store.execute_sparql('select distinct ?g where { graph ?g {[] a ?type}} order by ?g')

for result in results['results']['bindings']:
   print result['g']['value']
