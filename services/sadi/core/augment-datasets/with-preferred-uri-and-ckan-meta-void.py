#3> <> prov:specializationOf <https://raw.github.com/timrdf/DataFAQs/master/services/sadi/core/augment-datasets/with-preferred-uri-and-ckan-meta-void.py> .
#3>    rdfs:seeAlso <https://github.com/timrdf/DataFAQs/wiki/DataFAQs-Core-Services> .

import faqt

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
ns.register(dcat='http://www.w3.org/ns/dcat#')
ns.register(conversion='http://purl.org/twc/vocab/conversion/')
ns.register(datafaqs='http://purl.org/twc/vocab/datafaqs#')

# The Service itself
class WithPreferredURIAndCKANMetaVoid(faqt.CKANReader):

   # Service metadata.
   label                  = 'with-preferred-uri-and-ckan-meta-void'
   serviceDescriptionText = 'Augment void:Datasets with references to other resources that describe the dataset.'
   comment                = 'References CKAN extra "preferred_uri" and resource "meta/void".'
   serviceNameText        = 'with-preferred-uri-and-ckan-meta-void' # Convention: Match 'name' below.
   name                   = 'with-preferred-uri-and-ckan-meta-void' # This value determines the service URI relative to http://localhost:9090/
                                                                    # Convention: Use the name of this file for this value.
   dev_port = 9099

   def __init__(self):
      faqt.CKANReader.__init__(self, servicePath = 'services/sadi/core/augment-datasets')

   def getOrganization(self):
      result                      = self.Organization()
      result.mygrid_authoritative = True
      result.protegedc_creator    = 'lebot@rpi.edu'
      result.save()
      return result

   def getInputClass(self):
      return ns.DCAT['Dataset']

   def getOutputClass(self):
      return ns.DATAFAQS['WithReferences']

   def process(self, input, output):
   
      print 'processing ' + input.subject

      Thing = input.session.get_class(surf.ns.OWL.Thing)

      # Fetch the dataset description (no API key required for read-only)
      ckan_id = self.getCKANIdentiifer(input)
      if ckan_id is not None:
         self.ckan.package_entity_get(self.getCKANIdentiifer(input))
         dataset = self.ckan.last_message
         #print dataset

         if 'preferred_uri' in dataset['extras']:
            output.rdfs_seeAlso.append(Thing(dataset['extras']['preferred_uri']))

         for resource in dataset['resources']:
            if resource['format'] == u'meta/void':
               output.rdfs_seeAlso.append(Thing(resource['url']))

         output.save()

      # Dereference (e.g., from thedatahub.org)
      if False:
         # OLD from back when CKAN let you dereference URIs and get RDF...
         store   = surf.Store(reader = 'rdflib', writer = 'rdflib', rdflib_store = 'IOMemory')
         session = surf.Session(store)
         store.load_triples(source = input.subject)
         print str(store.size()) + ' triples from ' + input.subject

     
         # TODO: add in directly asserted PreferredURIs, now that we are accepting any dcat:Dataset
    
         # Dereference the preferred URI (denoted via a CKAN "extra")
         prefixes = "prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> "
         query = 'select ?uri where { <'+input.subject+'> <http://semantic.ckan.net/schema#extra> [ rdf:value ?uri; rdfs:label "preferred_uri"; ] }'
         for row in store.execute_sparql(prefixes+query)['results']['bindings']:
            preferred_uri = row['uri']['value']
            print '  preferred uri: ' + preferred_uri
            output.rdfs_seeAlso.append(Thing(preferred_uri))


         # Include the CKAN "resource" with "format" "meta/void"
         prefixes = 'prefix dc: <http://purl.org/dc/terms/> prefix dcat: <http://www.w3.org/ns/dcat#> prefix moat: <http://moat-project.org/ns#> '
         query = 'select ?uri where { <'+input.subject+'> dcat:distribution [ dcat:accessURL ?uri; dc:format [ moat:taggedWithTag [ moat:name "meta/void" ]]] }'
         for row in store.execute_sparql(prefixes+query)['results']['bindings']:
            void_uri = row['uri']['value']
            print '  void uri: ' + void_uri
            output.rdfs_seeAlso.append(Thing(void_uri))
         output.save()

# Used when Twistd invokes this service b/c it is sitting in a deployed directory.
resource = WithPreferredURIAndCKANMetaVoid()

# Used when this service is manually invoked from the command line (for testing).
if __name__ == '__main__':
   print resource.name + ' running on port ' + str(resource.dev_port) + '. Invoke it with:'
   print 'curl -H "Content-Type: text/turtle" -d @my.ttl http://localhost:' + str(resource.dev_port) + '/' + resource.name
   sadi.publishTwistedService(resource, port=resource.dev_port)
