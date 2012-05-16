import re
import sadi
from rdflib import *
import surf

from surf import *
from surf.query import select

# These are the namespaces we are using beyond those already available
# (see http://packages.python.org/SuRF/modules/namespace.html#registered-general-purpose-namespaces)
ns.register(void='http://rdfs.org/ns/void#')
ns.register(dcat='http://www.w3.org/ns/dcat#')
ns.register(datafaqs='http://purl.org/twc/vocab/datafaqs#')

# The Service itself
class IdentityDatasetSelector(sadi.Service):

   # Service metadata.
   label                  = 'dataset-identity'
   serviceDescriptionText = 'Return the same dcat:Datasets given to this service (the identity function).'
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
      return ns.DCAT['Dataset']

   def getOutputClass(self):
      return ns.DCAT['Dataset']

   def process(self, input, output):
  
      print input.subject

      for type in input.rdf_type:
         output.rdf_type.append(type)

      output.save()

# Used when Twistd invokes this service b/c it is sitting in a deployed directory.
resource = IdentityDatasetSelector()

# Used when this service is manually invoked from the command line (for testing).
if __name__ == '__main__':
   print resource.name + ' running on port ' + str(resource.dev_port) + '. Invoke it with:'
   print 'curl -H "Content-Type: text/turtle" -d @my.ttl http://localhost:' + str(resource.dev_port) + '/' + resource.name
   sadi.publishTwistedService(resource, port=resource.dev_port)
