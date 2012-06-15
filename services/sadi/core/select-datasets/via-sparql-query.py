#3> <> prov:specializationOf <https://raw.github.com/timrdf/DataFAQs/master/services/sadi/core/select-datasets/via-sparql-query.rpy>;
#3>    rdfs:seeAlso <https://github.com/timrdf/DataFAQs/wiki/DataFAQs-Core-Services> .
#3>
#3> <http://sparql.tw.rpi.edu/services/datafaqs/core/select-datasets/via-sparql-query>
#3>    a datafaqs:DatasetSelector . # TODO

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
import httplib
from urlparse import urlparse, urlunparse
import urllib
import urllib2

# These are the namespaces we are using beyond those already available
# (see http://packages.python.org/SuRF/modules/namespace.html#registered-general-purpose-namespaces)
ns.register(dcat='http://www.w3.org/ns/dcat#')
ns.register(datafaqs='http://purl.org/twc/vocab/datafaqs#')

# The Service itself
class DatasetsViaSPARQLQuery(faqt.Service):

   # Service metadata.
   label                  = 'via-sparql-query'
   serviceDescriptionText = 'Select datasets by applying the given SPARQL query to the given endpoint.'
   comment                = ''
   serviceNameText        = 'via-sparql-query' # Convention: Match 'name' below.
   name                   = 'via-sparql-query' # This value determines the service URI relative to http://localhost:9090/
                                               # Convention: Use the name of this file for this value.
   dev_port = 9113

   def __init__(self):
      faqt.Service.__init__(self, servicePath = 'services/core/select-datasets')

   def getOrganization(self):
      result                      = self.Organization()
      result.mygrid_authoritative = True
      result.protegedc_creator    = 'lebot@rpi.edu'
      result.save()
      return result

   #def annotateServiceDescription(self, desc):

   def getInputClass(self):
      return ns.DATAFAQS['QueryToApply']

   def getOutputClass(self):
      return ns.DATAFAQS['DatasetCollection']

   whatQueryQuery = '''
prefix rdf:      <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
prefix sd:       <http://www.w3.org/ns/sparql-service-description#>
prefix datafaqs: <http://purl.org/twc/vocab/datafaqs#>

SELECT ?query_string ?endpoint
WHERE {
   ?apply
      a datafaqs:QueryToApply;
      datafaqs:query   [ rdf:value ?query_string ];
      datafaqs:dataset ?dataset;
   .
   ?service
      a sd:Service;
      sd:availableGraphDescriptions ?dataset;
      sd:endpoint                   ?endpoint;
   .
}
'''

   def process(self, input, output):
  
      print input.subject

      Dataset = output.session.get_class(ns.DCAT['Dataset'])
      for queryToApply in input.session.default_store.execute_sparql(self.whatQueryQuery)['results']['bindings']:
         query    = queryToApply['query_string']['value']
         endpoint = queryToApply['endpoint']['value']
      
         #print 'query    = ' + query
         #print 'endpoint = ' + endpoint

         dataset_catalog_store = Store(reader = "sparql_protocol", writer = "sparql_protocol", endpoint = endpoint)

         results = dataset_catalog_store.execute_sparql(query)
         for result in results['results']['bindings']:
            dataset_service = result['dataset']['value']
            type            = result['type']['value']
            #print '   ' + dataset_service + ' ' + type
            typeR = output.session.get_resource(type, output.session.get_class(type))
            dataset_service_r = Dataset(dataset_service)
            dataset_service_r.rdf_type.append(ns.DCAT['Dataset'])
            dataset_service_r.rdf_type.append(typeR)
            dataset_service_r.save()
            output.dcterms_hasPart.append(dataset_service_r)

      output.save()

# Used when Twistd invokes this service b/c it is sitting in a deployed directory.
resource = DatasetsViaSPARQLQuery()

# Used when this service is manually invoked from the command line (for testing).
if __name__ == '__main__':
   print resource.name + ' running on port ' + str(resource.dev_port) + '. Invoke it with:'
   print 'curl -H "Content-Type: text/turtle" -d @my.ttl http://localhost:' + str(resource.dev_port) + '/' + resource.name
   sadi.publishTwistedService(resource, port=resource.dev_port)
