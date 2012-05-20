#3> <> prov:specializationOf <#TEMPLATE/path/to/public/source-code.rpy>;
#3>    rdfs:seeAlso <https://github.com/timrdf/DataFAQs/wiki/FAqT-Service> .

import faqt

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
class TowardsCKANTag(faqt.Service):

   # Service metadata.
   label                  = 'ckan-group'
   serviceDescriptionText = 'List FAqT services that guide a set of datasets towards acceptance to a given CKAN group.'
   comment                = 'The CKAN tag "lodcloud" is the primary example, but this could be used for other situations.'
   serviceNameText        = 'ckan-group' # Convention: Match 'name' below.
   name                   = 'ckan-group' # This value determines the service URI relative to http://localhost:9090/
                                         # Convention: Use the name of this file for this value.
   dev_port = 9121

   def __init__(self):
      faqt.Service.__init__(self, servicePath = 'services/sadi/core/select-faqts/towards')

   def getOrganization(self):
      result                      = self.Organization()
      result.mygrid_authoritative = True
      result.protegedc_creator    = 'lebot@rpi.edu'
      result.save()
      return result

   def getInputClass(self):
      return ns.DATAFAQS['CKANGroup']

   def getOutputClass(self):
      return ns.DATAFAQS['FAqTServiceCollection']

   def process(self, input, output):

      print 'processing ' + input.subject

      if len(input.datafaqs_ckan_identifier) > 0:
         FAqTService = output.session.get_class(ns.DATAFAQS['FAqTService'])
         faqts = [ 'http://sparql.tw.rpi.edu/services/datafaqs/faqt/lodcloud/max-1-topic-tag',
                   'http://sparql.tw.rpi.edu/services/datafaqs/faqt/datascape/size-deprecated' ]
         if input.datafaqs_ckan_identifier.first == 'lodcloud':
            for faqt in faqts:
               faqt = FAqTService(faqt)
               faqt.save()
               output.dcterms_hasPart.append(faqt)

      ####
      # Query a SPARQL endpoint
#      store = Store(reader = 'sparql_protocol', endpoint = 'http://dbpedia.org/sparql')
#      session = Session(store)
#      session.enable_logging = False
#      result = session.default_store.execute_sparql('select distinct ?type where {[] a ?type} limit 2')
#      if result:
#         for binding in result['results']['bindings']:
#            type  = binding['type']['value']
#            print type
      ####

#      if True:
#         output.rdf_type.append(ns.DATAFAQS['Unsatisfactory'])
# 
#      if ns.DATAFAQS['Unsatisfactory'] not in output.rdf_type:
#         output.rdf_type.append(ns.DATAFAQS['Satisfactory'])

      output.save()

# Used when Twistd invokes this service b/c it is sitting in a deployed directory.
resource = TowardsCKANTag()

# Used when this service is manually invoked from the command line (for testing).
if __name__ == '__main__':
   print resource.name + ' running on port ' + str(resource.dev_port) + '. Invoke it with:'
   print 'curl -H "Content-Type: text/turtle" -d @my.ttl http://localhost:' + str(resource.dev_port) + '/' + resource.name
   sadi.publishTwistedService(resource, port=resource.dev_port)
