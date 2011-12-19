# https://github.com/timrdf/DataFAQs/blob/master/services/sadi/faqt/internet-domain.rpy

from urlparse import urlparse
from surf import *
import sadi

# These are the namespaces we are using beyond those already available
# (see http://packages.python.org/SuRF/modules/namespace.html#registered-general-purpose-namespaces)
ns.register(void='http://rdfs.org/ns/void#')
#ns.register(datafaqs='http://purl.org/twc/vocab/datafaqs#')
ns.register(datafaqs='http://sparql.tw.rpi.edu/test/datafaqs.owl#')

# The Service itself
class InternetDomain(sadi.Service):

   # Service metadata.
   label                  = 'internet-domain'
   serviceDescriptionText = 'Reports the internet domain of the URIs for the datasets given.'
   comment                = ''
   serviceNameText        = 'internet-domain' # Convention: Match 'name' below.
   name                   = 'internet-domain' # This value determines the service URI relative to http://localhost:9090/
                                              # Convention: Use the name of this file for this value.
   def __init__(self): 
      sadi.Service.__init__(self)

   def getOrganization(self):
      result                      = self.Organization('http://tw.rpi.edu')
      result.mygrid_authoritative = True
      result.protegedc_creator    = 'lebot@rpi.edu'
      result.save()
      return result

   def getInputClass(self):
      return ns.VOID['Dataset']

   def getOutputClass(self):
      return ns.DATAFAQS['DatasetWithInternetDomain']

   def process(self, input, output):
      parsed = urlparse(input.subject)
      output.datafaqs_internet_domain = parsed.scheme + parsed.netloc
      output.save()

# Used when Twistd invokes this service b/c it is sitting in a deployed directory.
resource = InternetDomain()

# Used when this service is manually invoked from the command line (for testing).
if __name__ == '__main__':
   sadi.publishTwistedService(resource, port=9092)
