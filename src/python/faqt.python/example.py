import faqt
import sadi
from rdflib import *
from surf import *

ns.register(hello="http://sadiframework.org/examples/hello.owl#")

class ExampleService(sadi.Service):

   label           = "by-ckan-tag"
   serviceDescriptionText = 'A simple "Hello, World" service that reads a name and attaches a greeting.'
   comment         = 'A simple "Hello, World" service that reads a name and attaches a greeting.'
   serviceNameText = "by-ckan-tag"
   name            = "by-ckan-tag"

   # These are used by faqt.py annotateServiceDescription
   rawBase  = 'https://raw.github.com/timrdf/DataFAQs/master/services/sadi/core/select-datasets/'
   pageBase = 'https://github.com/timrdf/DataFAQs/blob/master/services/sadi/core/select-datasets/'
    
   def getOrganization(self):
      result = self.Organization("")
      result.mygrid_authoritative = False
      result.protegedc_creator = 'lebot@rpi.edu'
      result.save()
      return result

   def getInputClass(self):
      return ns.HELLO["NamedIndividual"]

   def getOutputClass(self):
      return ns.HELLO["GreetedIndividual"]

   def process(self, input, output):
      output.hello_greeting = "Hello, "+input.foaf_name[0]
      output.save()

resource = ExampleService()

if __name__ == "__main__":
   sadi.publishTwistedService(resource, port=9090)
