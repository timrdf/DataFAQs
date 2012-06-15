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
ns.register(http='http://www.w3.org/2011/http#')

# The Service itself
class VoIDdataDump(faqt.Service):

   # Service metadata.
   label                  = 'void-datadump'
   serviceDescriptionText = 'Checks the availablity (HTTP HEAD == 404?) of the void:dataDump asserted.'
   comment                = ''
   serviceNameText        = 'void-datadump' # Convention: Match 'name' below.
   name                   = 'void-datadump' # This value determines the service URI relative to http://localhost:9090/
                                            # Convention: Use the name of this file for this value.
   dev_port = 9227

   def __init__(self):
      # DATAFAQS_PROVENANCE_CODE_RAW_BASE                   +  servicePath  +  '/'  + self.serviceNameText
      # DATAFAQS_PROVENANCE_CODE_PAGE_BASE                  +  servicePath  +  '/'  + self.serviceNameText
      #
      # ^^ The source code location
      #    aligns with the deployment location \/
      #
      #                 DATAFAQS_BASE_URI  +  '/datafaqs/'  +  servicePath  +  '/'  + self.serviceNameText
      faqt.Service.__init__(self, servicePath = 'services/sadi/faqt/access')

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

      if len(input.void_dataDump) > 0:
         print input.void_dataDump.first

         Thing = output.session.get_class(ns.RDFS['Resource'])
         dump = Thing(input.void_dataDump.first)
         output.void_dataDump = dump

         # http://stackoverflow.com/questions/107405/how-do-you-send-a-head-http-request-in-python
         response = self.getResponse(input.void_dataDump.first)
         dump.http_statusCodeValue = response.status
         dump.save()
         print response.status
         if response.status == 200:
            output.rdf_type.append(ns.DATAFAQS['Satisfactory'])
 
      if ns.DATAFAQS['Satisfactory'] not in output.rdf_type:
         output.rdf_type.append(ns.DATAFAQS['Unsatisfactory'])

      # TODO: string match URL extension and Content-Type returned.
      #       add content-length and last-modified

      # curl -LI http://logd.tw.rpi.edu/source/bcn-cat/file/catalog/version/2012-Jan-31/conversion/bcn-cat-catalog-2012-Jan-31.ttl
      # HTTP/1.1 200 OK
      # Date: Fri, 15 Jun 2012 13:46:39 GMT
      # Server: Apache/2.2.14 (Ubuntu)
      # Last-Modified: Thu, 14 Jun 2012 11:29:33 GMT
      # ETag: "1a8c02f6-113fb5-4c26d0388a37a"
      # Accept-Ranges: bytes
      # Content-Length: 1130421
      # Vary: Accept-Encoding
      # Access-Control-Allow-Origin: *
      # Content-Type: text/turtle

      output.save()

# Used when Twistd invokes this service b/c it is sitting in a deployed directory.
resource = VoIDdataDump()

# Used when this service is manually invoked from the command line (for testing).
if __name__ == '__main__':
   print resource.name + ' running on port ' + str(resource.dev_port) + '. Invoke it with:'
   print 'curl -H "Content-Type: text/turtle" -d @my.ttl http://localhost:' + str(resource.dev_port) + '/' + resource.name
   sadi.publishTwistedService(resource, port=resource.dev_port)
