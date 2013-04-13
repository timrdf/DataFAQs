#3> <> prov:specializationOf <https://raw.github.com/timrdf/DataFAQs/master/services/sadi/core/select-faqts/identity0.py>;
#3>    rdfs:seeAlso <https://github.com/timrdf/DataFAQs/wiki/DataFAQs-Core-Services> .

import faqt

import re
import sadi
from rdflib import *
import surf

from surf import *
from surf.query import select

# These are the namespaces we are using beyond those already available
# (see http://packages.python.org/SuRF/modules/namespace.html#registered-general-purpose-namespaces)
ns.register(datafaqs='http://purl.org/twc/vocab/datafaqs#')
ns.register(mygrid='http://www.mygrid.org.uk/mygrid-moby-service#')

# The Service itself
class IdentityFAqTService(faqt.Service):

   # Service metadata.
   label                  = 'identity0'
   serviceDescriptionText = 'Return the FAqT services given.'
   comment                = ''
   serviceNameText        = 'identity0' # Convention: Match 'name' below.
   name                   = 'identity0' # This value determines the service URI relative to http://localhost:9090/
                                       # Convention: Use the name of this file for this value.
   def __init__(self): 
      faqt.Service.__init__(self, servicePath = 'services/sadi/core/select-faqts')

   def getOrganization(self):
      result                      = self.Organization()
      result.mygrid_authoritative = True
      result.protegedc_creator    = 'lebot@rpi.edu'
      result.save()
      return result

   def getInputClass(self):
      return ns.MYGRID['serviceDescription']

   def getOutputClass(self):
      return ns.DATAFAQS['FAqTServiceCollection']

   def process(self, input, output):
  
      print input.subject

      #FAqTService = output.session.get_class(ns.DATAFAQS['FAqTService'])
      #faqt_service = output.session.get_resource(output.subject,ns.DATAFAQS['FAqTService']) #FAqTService(output.subject)
      #faqt_service.rdf_type.append(ns.DATAFAQS['FAqTService'])
      #faqt_service.save()

      output.rdf_type.append(ns.DATAFAQS['FAqTService'])
      output.dcterms_hasPart.append(output)

      output.save()

# Used when Twistd invokes this service b/c it is sitting in a deployed directory.
resource = IdentityFAqTService()

# Used when this service is manually invoked from the command line (for testing).
if __name__ == '__main__':
   port = 9105
   print 'curl -H "Content-Type: text/turtle" -d @my.ttl http://localhost:' + str(port) + '/' + resource.name
   sadi.publishTwistedService(resource, port=port)
