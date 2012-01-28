import re
import sadi
from rdflib import *
import surf

from surf import *
from surf.query import select

# These are the namespaces we are using beyond those already available
# (see http://packages.python.org/SuRF/modules/namespace.html#registered-general-purpose-namespaces)
ns.register(void='http://rdfs.org/ns/void#')
ns.register(datafaqs='http://purl.org/twc/vocab/datafaqs#')

# The Service itself
class IdentityCKANDataset(sadi.Service):

   # Service metadata.
   label                  = 'dataset-identity'
   serviceDescriptionText = 'Return the void:CKANDataset FAqT services given.'
   comment                = ''
   serviceNameText        = 'identity-dataset' # Convention: Match 'name' below.
   name                   = 'identity-dataset' # This value determines the service URI relative to http://localhost:9090/
                                               # Convention: Use the name of this file for this value.
   dev_port = 9108

   def __init__(self): 
      sadi.Service.__init__(self)

   def getOrganization(self):
      result                      = self.Organization()
      result.mygrid_authoritative = True
      result.protegedc_creator    = 'lebot@rpi.edu'
      result.save()
      return result

   def getInputClass(self):
      return ns.DATAFAQS['CKANDataset']

   def getOutputClass(self):
      return ns.DATAFAQS['CKANDataset']

   def process(self, input, output):
  
      print input.subject

      CKANDataset = output.session.get_class(ns.DATAFAQS['CKANDataset'])
      dataset = CKANDataset(input.subject)
      dataset.rdf_type.append(ns.DATAFAQS['CKANDataset'])
      dataset.save()
      output.dcterms_hasPart.append(dataset)

      output.save()

# Used when Twistd invokes this service b/c it is sitting in a deployed directory.
resource = IdentityCKANDataset()

# Used when this service is manually invoked from the command line (for testing).
if __name__ == '__main__':
   print resource.name + ' running on port ' + str(resource.dev_port) + '. Invoke it with:'
   print 'curl -H "Content-Type: text/turtle" -d @my.ttl http://localhost:' + str(resource.dev_port) + '/' + resource.name
   sadi.publishTwistedService(resource, port=resource.dev_port)
