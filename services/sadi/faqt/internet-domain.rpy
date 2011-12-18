import sadi
from rdflib import *
from surf import *
from surf.query import select

import rdflib
rdflib.plugin.register('sparql', rdflib.query.Processor, 'rdfextras.sparql.processor', 'Processor')
rdflib.plugin.register('sparql', rdflib.query.Result,    'rdfextras.sparql.query',     'SPARQLQueryResult')

from urlparse import urlparse

# These are the namespaces we are using beyond those already available
# (see http://packages.python.org/SuRF/modules/namespace.html#registered-general-purpose-namespaces)
ns.register(moat='http://moat-project.org/ns#')
ns.register(ov='http://open.vocab.org/terms/')
ns.register(datafaqs='http://purl.org/twc/vocab/datafaqs#')
ns.register(void='http://rdfs.org/ns/void#')

# The Service itself
class PayLevelDomain(sadi.Service):

   # Service metadata.
   label                  = 'void:Dataset has void:triples asserted.'
   serviceDescriptionText = 'Reports the void:triples of the given dataset.'
   comment                = 'Giving the size of a dataset is useful.'
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
      print 'processing ' + input.subject
      parsed = urlparse(input.subject)
      output.datafaqs_internet_domain = parsed.scheme + parsed.netloc
      output.save()

# Used when Twistd invokes this service b/c it is sitting in a deployed directory.
resource = PayLevelDomain()

# Used when this service is manually invoked from the command line (for testing).
# The service listens on port 9091
if __name__ == '__main__':
   sadi.publishTwistedService(resource, port=9092)
