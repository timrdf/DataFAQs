#3> <> prov:specializationOf <#TEMPLATE/path/to/public/source-code.py>;
#3>    rdfs:seeAlso <https://github.com/timrdf/DataFAQs/wiki/FAqT-Service> .

import faqt

import sadi
from rdflib import *
import surf

from surf import *
from surf.query import a, select

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

connections = {'http' :httplib.HTTPConnection,
               'https':httplib.HTTPSConnection}

def getResponse(url):
   # Ripped from https://github.com/timrdf/csv2rdf4lod-automation/blob/master/bin/util/pcurl.py
   o = urlparse(str(url))
   #print o
   connection = connections[o.scheme](o.netloc)
   fullPath = urlunparse([None,None,o.path,o.params,o.query,o.fragment])
   connection.request('GET',fullPath)
   return connection.getresponse()

# The Service itself
class SameAsOrg(faqt.Service):

   # Service metadata.
   label                  = 'sameas-org'
   serviceDescriptionText = 'Reference other URLs that may provide additional information about the given dcat:Dataset.'
   comment                = 'Exposes the functionality of sameas.org as a SADI service.'
   serviceNameText        = 'sameas-org' # Convention: Match 'name' below.
   name                   = 'sameas-org' # This value determines the service URI relative to http://localhost:9090/
                                         # Convention: Use the name of this file for this value.
   dev_port = 9226

   def __init__(self):
      # DATAFAQS_PROVENANCE_CODE_RAW_BASE                   +  servicePath  +  '/'  + self.serviceNameText
      # DATAFAQS_PROVENANCE_CODE_PAGE_BASE                  +  servicePath  +  '/'  + self.serviceNameText
      #
      # ^^ The source code location
      #    aligns with the deployment location \/
      #
      #                 DATAFAQS_BASE_URI  +  '/datafaqs/'  +  servicePath  +  '/'  + self.serviceNameText
      faqt.Service.__init__(self, servicePath = 'services/sadi/core/augment-datasets')

   def getOrganization(self):
      result                      = self.Organization()
      result.mygrid_authoritative = True
      result.protegedc_creator    = 'lebot@rpi.edu'
      result.save()
      return result

   def getInputClass(self):
      return ns.DCAT['Dataset']

   def getOutputClass(self):
      return ns.DCAT['Dataset']

   def process(self, input, output):

      print 'processing ' + input.subject

      # http://sameas.org/?uri=http://dbpedia.org/resource/Edinburgh
      #   Accept: application/rdf+xml: 303 -> http://sameas.org/rdf?uri=http://dbpedia.org/resource/Edinburgh
      #   Accept: application/json:    303 -> http://sameas.org/json?uri=http://dbpedia.org/resource/Edinburgh

      # Using SuRF
      store   = Store(reader='rdflib', writer='rdflib', rdflib_store = 'IOMemory')
      session = Session(store)
      store.load_triples(source='http://sameas.org/rdf?uri='+input.subject)

      Thing   = session.get_class(ns.OWL['Thing'])
      subject = session.get_resource(input.subject, Thing)
      for same in subject.owl_sameAs:
         if isinstance(same, URIRef):
            output.rdfs_seeAlso.append(same)
         else:
            output.rdfs_seeAlso.append(same.subject)

      # Using json
      #response = getResponse('http://sameas.org/json?uri='+input.subject)

      output.save()

# Used when Twistd invokes this service b/c it is sitting in a deployed directory.
resource = SameAsOrg()

# Used when this service is manually invoked from the command line (for testing).
if __name__ == '__main__':
   print resource.name + ' running on port ' + str(resource.dev_port) + '. Invoke it with:'
   print 'curl -H "Content-Type: text/turtle" -d @my.ttl http://localhost:' + str(resource.dev_port) + '/' + resource.name
   sadi.publishTwistedService(resource, port=resource.dev_port)
