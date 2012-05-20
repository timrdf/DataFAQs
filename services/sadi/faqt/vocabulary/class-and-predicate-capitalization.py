#3> <> prov:specializationOf <https://github.com/timrdf/DataFAQs/raw/master/services/sadi/faqt/vocabulary/class-and-predicate-capitalization.py>;
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
ns.register(conversion='http://purl.org/twc/vocab/conversion/')
ns.register(datafaqs='http://purl.org/twc/vocab/datafaqs#')

def getHEAD(url):
    # Ripped from https://github.com/timrdf/csv2rdf4lod-automation/blob/master/bin/util/pcurl.py
    o = urlparse(str(url))
    print o
    connections = {'http' :httplib.HTTPConnection,
                   'https':httplib.HTTPSConnection}
    connection = connections[o.scheme](o.netloc)
    fullPath = urlunparse([None,None,o.path,o.params,o.query,o.fragment])
    connection.request('HEAD',fullPath)
    return connection.getresponse()

# The Service itself
class ClassAndPredicatCapitalization(faqt.Service):

   # Service metadata.
   label                  = ''
   serviceDescriptionText = 'Class local names should be capitalized, predicate local names should not.'
   comment                = '<http://www.mygrid.org.uk/mygrid-moby-service#serviceDescription> a owl:Class FAILS;'
   serviceNameText        = 'class-and-predicate-capitalization' # Convention: Match 'name' below.
   name                   = 'class-and-predicate-capitalization' # This value determines the service URI relative to http://localhost:9090/
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
resource = ClassAndPredicatCapitalization()

# Used when this service is manually invoked from the command line (for testing).
if __name__ == '__main__':
   sadi.publishTwistedService(resource, port=9094)
