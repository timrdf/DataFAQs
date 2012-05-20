# <> prov:specializationOf <https://raw.github.com/timrdf/DataFAQs/master/services/sadi/faqt/vocabulary/vocabulary-resolves-to-description.py> .

import faqt

from urlparse import urlparse
from surf import *
import sadi

# These are the namespaces we are using beyond those already available
# (see http://packages.python.org/SuRF/modules/namespace.html#registered-general-purpose-namespaces)
ns.register(void='http://rdfs.org/ns/void#')
ns.register(datafaqs='http://purl.org/twc/vocab/datafaqs#')
#ns.register(datafaqs='http://sparql.tw.rpi.edu/test/datafaqs.owl#')

# The Service itself
class VocabularyResolvesToDescription(faqt.Service):

   # Service metadata.
   label                  = 'vocabulary-resolves-to-description'
   serviceDescriptionText = 'Number of predicate and class URIs that resolve to an RDF description that types them.'
   comment                = 'http://semantic.ckan.net/record/91d2c0de-75a4-4bb6-b260-bc2946e1be8b.rdf files with moat:taggedWithTag'
   serviceNameText        = 'vocabulary-resolves-to-description' # Convention: Match 'name' below.
   name                   = 'vocabulary-resolves-to-description' # This value determines the service URI relative to http://localhost:9090/
                                                                 # Convention: Use the name of this file for this value.
   def __init__(self):
      faqt.Service.__init__(self, servicePath = 'services/sadi/faqt/vocabulary')

   def getOrganization(self):
      result                      = self.Organization('http://tw.rpi.edu')
      result.mygrid_authoritative = True
      result.protegedc_creator    = 'lebot@rpi.edu'
      result.save()
      return result

   def getInputClass(self):
      return ns.VOID['Dataset']

   def getOutputClass(self):
      return ns.DATAFAQS['EvaluatedDataset']

   def process(self, input, output):
      output.save()

# Used when Twistd invokes this service b/c it is sitting in a deployed directory.
resource = VocabularyResolvesToDescription()

# Used when this service is manually invoked from the command line (for testing).
if __name__ == '__main__':
   sadi.publishTwistedService(resource, port=9100)
