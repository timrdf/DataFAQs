#!/usr/bin/env python
#
# https://github.com/timrdf/DataFAQs/blob/master/bin/df-core.py
#
# Enumerate the FAqTSelector(s) and DatasetSelector(s) involved in the epoch described in the given RDF file (i.e. "epoch configuration file").
#    (optionally, include the URIs of the inputs that should be given to the Selectors)
#
# Enumerate the datasets returned by the DatasetSelector
#
# Usage:
#
#   df-core.py epoch.ttl.rdf faqt-selectors
#      Returns <selector-service> <input-to-selector-service>
#
#      http://sparql.tw.rpi.edu/services/datafaqs/core/select-faqts/identity https://raw.github.com/timrdf/DataFAQs/master/services/sadi/faqt/access/in-sparql-endpoint-materials/in-sparql-endpoint.ttl
#      http://sparql.tw.rpi.edu/services/datafaqs/core/select-faqts/identity https://raw.github.com/timrdf/DataFAQs/master/services/sadi/faqt/discuss/contributor-email/contributor-email.ttl
#
#   df-core.py epoch.ttl.rdf faqt-selector-inputs http://sparql.tw.rpi.edu/services/datafaqs/core/select-faqts/identity
#      Returns <input-to-selector-service>
#      https://raw.github.com/timrdf/DataFAQs/master/services/sadi/faqt/access/in-sparql-endpoint-materials/in-sparql-endpoint.ttl
#      https://raw.github.com/timrdf/DataFAQs/master/services/sadi/faqt/discuss/contributor-email/contributor-email.ttl
#
#   df-core.py epoch.ttl.rdf dataset-selectors
#      Returns <selector-service> <input-to-selector-service>
#
#      http://sparql.tw.rpi.edu/services/datafaqs/core/select-datasets/identity https://raw.github.com/timrdf/DataFAQs/master/services/sadi/faqt/access/in-sparql-endpoint-materials/sample-inputs/1-good-1-bad-from-lodstat.ttl
#
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

if len(sys.argv) < 3 or len(sys.argv) > 4:
   print "usage: df-core.py epoch.rdf  {faqt-selectors,       dataset-selectors,       dataset-referencers} | "
   print "                            ({faqt-selector-inputs, dataset-selector-inputs, dataset-referencer-inputs} <selector-uri>)"
   print
   print "  epoch.rdf               - an RDF description of the services to invoke with which inputs (RDF/XML only)."
   print ""
   print "  faqt-selectors          - print <service_uri> <input_uri> (one per line)."
   print "  dataset-selectors       - print <service_uri> <input_uri> (one per line)."
   print "  dataset-referencers     - print <service_uri> <input_uri> (one per line)."
   print ""
   print "  faqt-selector-inputs    - print               <input_uri> (one per line)."
   print "  dataset-selector-inputs - print               <input_uri> (one per line)."
   print "  faqt-services           - "
   print "  datasets                - "
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

prefixes = dict(prov=str(ns.PROV), datafaqs=str(ns.DATAFAQS),
                dcat=str(ns.DCAT), void=str(ns.VOID))

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

   'dataset-referencers' : '''
select distinct ?service where {
   ?service a datafaqs:DatasetReferencer .
}
''',

   'faqt-selector-input' : '''
select distinct ?dataset where {
   ?dataset a dcat:Dataset .
}
''',

   'faqt-services' : '''
select distinct ?service where {
   ?service a datafaqs:FAqTService .
}
''',

   'datasets' : '''
select distinct ?dataset where {
   ?dataset a dcat:Dataset .
}
'''
}

graph = Graph()
#graph.parse(epoch, format="n3") # :: sigh ::
graph.parse(epoch)

if type in [ 'faqt-selectors'          'dataset-selectors'        'dataset-referencers'  'faqt-services']:
   results = graph.query(queries[type], initNs=prefixes)
   for bindings in results:
      if len(bindings) == 2:
         print bindings[0] + ' ' + bindings[1]
      else:
         print bindings[0]
elif type in [ 'faqt-selector-inputs', 'dataset-selector-inputs', 'dataset-referencer-inputs']: 
   query = '''
select distinct ?input where {
   [] 
      a prov:Activity;
      prov:used            ?input;
      prov:wasAttributedTo <'''+sys.argv[3]+'''>
   .
}
'''
   results = graph.query(query, initNs=prefixes)
   for input in results:
      print input[0] # [0] is not needed for Ubuntu /usr/local/lib/python2.6/dist-packages/rdflib-3.2.0-py2.6.egg
                     # but it is for Mac /Library/Python/2.7/site-packages/rdflib-3.2.1-py2.7.egg
elif type == 'services':
   results = graph.query(queries[type], initNs=prefixes)
   for input in results:
      print input
elif type == 'datasets':

   if len(sys.argv) > 3 and sys.argv[3] == 'df:individual':
      print 'TODO: implement df:individual'
      query = '''select distinct ?a ?b ?dataset where { ?a ?b ?dataset . ?dataset a dcat:Dataset . }'''
      results = graph.query(query, initNs=prefixes)
      for bindings in results:
         print bindings[0] + ' ' + bindings[1] + ' ' + bindings[2]

      query = '''select distinct ?dataset ?y ?z where { ?dataset a dcat:Dataset; ?y ?z . }'''
      results = graph.query(query, initNs=prefixes)
      for bindings in results:
         print bindings[0] + ' ' + bindings[1] + ' ' + bindings[2]
   else:
      query = '''select distinct ?dataset where { ?dataset a dcat:Dataset . }'''
      # To make this easier to read, do this:
      #def split_by(sequence, length):
      #   iterable = iter(sequence)
      #   def yield_length():
      #       for i in xrange(length):
      #            yield iterable.next()
      #   while True:
      #       res = list(yield_length())
      #       if not res:
      ##           raise StopIteration
      #       yield res
      results = graph.query(query, initNs=prefixes)
      block = 1
      count = 0
      size = 50
      post = None
      for bindings in results:
         if len(sys.argv) > 3 and sys.argv[3] == 'df:chunk':
            if count == 0:
               if block > 1:
                  post.close()
               filename = 'dataset-references.post.'+str(block)+'.ttl' # Separating into separate files to avoid GET timeout.
               if not(os.path.exists(filename)):
                  print filename
                  post = open(filename, 'w')
               else:
                  print filename + " already exists. Not modifying."
            count += 1
            post.write('<' + bindings[0] + '> a <http://www.w3.org/ns/dcat#Dataset> .\n')
            if count == size:
               count = 0
               block += 1
         else:
            print bindings[0]
else: # faqt-selectors and dataset-selectors and dataset-referencers
   # DEPRECATED use above
   results = graph.query(queries[type], initNs=prefixes)
   for bindings in results:
      if len(bindings) == 2:
         print bindings[0] + ' ' + bindings[1]
      else:
         print bindings[0]
