# 
# See https://github.com/timrdf/DataFAQs/wiki/FAqT-Service
#

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
ns.register(sd='http://www.w3.org/ns/sparql-service-description#')
ns.register(conversion='http://purl.org/twc/vocab/conversion/')
ns.register(datafaqs='http://purl.org/twc/vocab/datafaqs#')

# The Service itself
class InSPARQLEndpoint(sadi.Service):

   # Service metadata.
   label                  = 'in-sparql-endpoint'
   serviceDescriptionText = ''
   comment                = ''
   serviceNameText        = 'in-sparql-endpoint' # Convention: Match 'name' below.
   name                   = 'in-sparql-endpoint' # This value determines the service URI relative to http://localhost:9109/
                                            # Convention: Use the name of this file for this value.
   dev_port = 9109 # TEMPLATE: 

   def __init__(self): 
      sadi.Service.__init__(self)

   def getOrganization(self):
      result                      = self.Organization()
      result.mygrid_authoritative = True
      result.protegedc_creator    = 'lebot@rpi.edu'
      result.save()
      return result

   def getInputClass(self):
      return ns.DCAT['Dataset']

   def getOutputClass(self):
      return ns.DATAFAQS['EvaluatedDataset']

   def process(self, input, output):
      print 'processing ' + input.subject

      if input.void_sparqlEndpoint:
         output.void_sparqlEndpoint = input.void_sparqlEndpoint.first
         result = {}
         try:
            print '          ',
            print input.void_sparqlEndpoint.first
            queries = [ 'select distinct ?type where {[] a ?type} limit 1',
                        'select distinct ?type where { graph ?g { [] a ?type } } limit 1']
            for query in queries:
               if ns.DATAFAQS['Satisfactory'] not in output.rdf_type:
                  store   = Store(reader = 'sparql_protocol', endpoint = input.void_sparqlEndpoint.first)
                  session = Session(store)
                  session.enable_logging = False
                  result = session.default_store.execute_sparql(query)
                  if result['results'] != None:
                     for binding in result['results']['bindings']:
                        type = binding['type']['value']
                        output.rdf_type.append(ns.DATAFAQS['Satisfactory'])
                        print '          ',
                        print type
         except:
            print '           BAD ENDPOINT'
            output.rdf_type.append(ns.DATAFAQS['Unsatisfactory'])
            output.datafaqs_error = result.read()
      else:
         print '           NO ENDPOINT'
         output.rdf_type.append(ns.DATAFAQS['Unsatisfactory'])
         output.datafaqs_error = 'Dataset was not described with predicate void:sparqlEndpoint.'

      if ns.DATAFAQS['Satisfactory'] not in output.rdf_type:
         output.rdf_type.append(ns.DATAFAQS['Unsatisfactory'])

      output.save()

# Used when Twistd invokes this service b/c it is sitting in a deployed directory.
resource = InSPARQLEndpoint()

# Used when this service is manually invoked from the command line (for testing).
if __name__ == '__main__':
   print resource.name + ' running on port ' + str(resource.dev_port) + '. Invoke it with:'
   print 'curl -H "Content-Type: text/turtle" -d @my.ttl http://localhost:' + str(resource.dev_port) + '/' + resource.name
   sadi.publishTwistedService(resource, port=resource.dev_port)
