#!/usr/bin/env python

# Creates a stub Turtle file for each term in the given ontology.
# Useful for documenting the ontology.
#
# Author: Timothy Lebo
#
# To install dependencies, see https://github.com/timrdf/DataFAQs/wiki/Errors

import sys, urllib2
from surf import * # easy_install surf

if len(sys.argv) < 3:
   print "usage: stub-ontology-examples.py http://some.owl namespace [prefix]*"
   print
   print "  http://some.owl - web URL of the OWL    e.g. http://dvcs.w3.org/hg/prov/raw-file/default/ontology/ProvenanceOntology.owl"
   print "                                               https://raw.github.com/timrdf/pml/master/ontology/pml-3.0.owl"
   print
   print "  namespace       - namespace of ontology e.g. http://www.w3.org/ns/prov#"
   print "                                               http://provenanceweb.org/ontology/pml#"
   print
   print "  prefix          - prefix to include in default examples (will expand using prefix.cc) e.g. prov, pml, dcterms, pmlj"
   print "                    already includes: rdfs, xsd, owl, dcterms"
   sys.exit(1)

ont_url = sys.argv[1] # http://dvcs.w3.org/hg/prov/raw-file/default/ontology/ProvenanceOntology.owl
                      # https://raw.github.com/timrdf/pml/master/ontology/pml-3.0.owl
ont_ns  = sys.argv[2] # http://www.w3.org/ns/prov#
                      # http://provenanceweb.org/ontology/pml#

prefixes = 'http://prefix.cc/rdfs,xsd,owl,dcterms'
for arg in range(3,len(sys.argv)):
   prefixes = prefixes + ',' + sys.argv[arg]
prefixes = urllib2.urlopen(prefixes+'.file.ttl').read()

# as SuRF
store = Store(reader='rdflib', writer='rdflib', rdflib_store = 'IOMemory')
session = Session(store)
store.load_triples(source=ont_url) # From URL
DatatypeProperties = session.get_class(ns.OWL["DatatypeProperty"])
ObjectProperties   = session.get_class(ns.OWL["ObjectProperty"])
Classes            = session.get_class(ns.OWL["Class"])

defaultExample = '''@prefix ex:      <http://example.com/vocab#> .
@prefix :        <http://example.com/> .

# TODO
'''

def handle(term,pre):
   qname = term.split('#') # Note: will not work on slash URIs.
   if qname[0] + '#' == ont_ns:

      #fileName = 'rdf/'+pre+qname[1]+'.ttl'
      fileName = pre+qname[1]+'.ttl'

      #if not os.path.exists(os.path.dirname(fileName)): # TODO: add -od param
      #   os.makedirs(os.path.dirname(fileName))

      if os.path.exists(fileName):
         print fileName + ': exists. Not modifying.'
      else:
         print fileName
         example = open(fileName, 'w')
         example.write(prefixes + defaultExample)
         example.close()
   
for owlClass in Classes.all():
   handle(owlClass.subject,'class_')
for owlProperty in DatatypeProperties.all():
   handle(owlProperty.subject,'property_')
for owlProperty in ObjectProperties.all():
   handle(owlProperty.subject,'property_')
