import re
import sadi
from rdflib import *
import surf

from surf import *
from surf.query import select

import rdflib
rdflib.plugin.register('sparql', rdflib.query.Processor,
                       'rdfextras.sparql.processor', 'Processor')
rdflib.plugin.register('sparql', rdflib.query.Result,
                       'rdfextras.sparql.query', 'SPARQLQueryResult')
import ckanclient

import httplib
from urlparse import urlparse, urlunparse
import urllib
import urllib2

# These are the namespaces we are using beyond those already available
# (see http://packages.python.org/SuRF/modules/namespace.html#registered-general-purpose-namespaces)
ns.register(moat='http://moat-project.org/ns#')
ns.register(ov='http://open.vocab.org/terms/')
ns.register(void='http://rdfs.org/ns/void#')
ns.register(conversion='http://purl.org/twc/vocab/conversion/')
ns.register(datafaqs='http://purl.org/twc/vocab/datafaqs#')

# The Service itself
class WithPreferredURIAndCKANMetaVoid(sadi.Service):

   # Service metadata.
   label                  = 'with-preferred-uri-and-ckan-meta-void'
   serviceDescriptionText = 'Reference locations that describe the given void:Datasets.'
   comment                = ''
   serviceNameText        = 'with-preferred-uri-and-ckan-meta-void' # Convention: Match 'name' below.
   name                   = 'with-preferred-uri-and-ckan-meta-void' # This value determines the service URI relative to http://localhost:9090/
                                                                    # Convention: Use the name of this file for this value.
   def __init__(self): 
      sadi.Service.__init__(self)

      # Instantiate the CKAN client.
      # http://docs.python.org/library/configparser.html (could use this technique)
      key = os.environ['X_CKAN_API_Key']
      if len(key) <= 1:
          print 'ERROR: https://github.com/timrdf/DataFAQs/wiki/Missing-CKAN-API-Key'
          sys.exit(1)
      self.ckan = ckanclient.CkanClient(api_key=key)

   def getOrganization(self):
      result                      = self.Organization()
      result.mygrid_authoritative = True
      result.protegedc_creator    = 'lebot@rpi.edu'
      result.save()
      return result

   def getInputClass(self):
      return ns.DATAFAQS['CKANDataset']

   def getOutputClass(self):
      return ns.DATAFAQS['WithReferences']

   def process(self, input, output):
   
      # Dereference via thedatahub
      store   = surf.Store(reader = 'rdflib', writer = 'rdflib', rdflib_store = 'IOMemory')
      session = surf.Session(store)
      store.load_triples(source = input.subject)
      print str(store.size()) + ' triples from ' + input.subject

   
      # Dereference the preferred URI (denoted via a CKAN "extra")
      Thing = session.get_class(surf.ns.OWL.Thing)
      prefixes = "prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> "
      query = 'select ?uri where { <'+input.subject+'> <http://semantic.ckan.net/schema#extra> [ rdf:value ?uri; rdfs:label "sparql_graph_name"; ] }' # TODO: change to preferred_uri when it shows up.
      for row in store.execute_sparql(prefixes+query)['results']['bindings']:
         preferred_uri = row['uri']['value']
         output.rdfs_seeAlso.append(Thing(preferred_uri))


      # Include the CKAN "resource" with "format" "meta/void"
      prefixes = 'prefix dc: <http://purl.org/dc/terms/> prefix dcat: <http://www.w3.org/ns/dcat#> prefix moat: <http://moat-project.org/ns#> '
      query = 'select ?uri where { <'+input.subject+'> dcat:distribution [ a dcat:Distribution; dcat:accessURL ?uri; dc:format [ a dc:IMT; moat:taggedWithTag [ a moat:Tag; moat:name "meta/void" ] ] ] }'
      for row in store.execute_sparql(prefixes+query)['results']['bindings']:
         void_uri = row['uri']['value']
         print 'void uri: ' + void_uri
         output.rdfs_seeAlso.append(Thing(void_uri))
         #store.load_triples(source = void_uri) # TODO: craps out on turtle parsing.
         #print str(store.size()-last_size) + ' triples from ' + void_uri
         #last_size = store.size()

      output.save()

# Used when Twistd invokes this service b/c it is sitting in a deployed directory.
resource = WithPreferredURIAndCKANMetaVoid()

# Used when this service is manually invoked from the command line (for testing).
if __name__ == '__main__':
   sadi.publishTwistedService(resource, port=9099)
