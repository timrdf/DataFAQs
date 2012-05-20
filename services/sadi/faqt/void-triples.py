#3> <> prov:specializationOf <https://github.com/timrdf/DataFAQs/blob/master/services/sadi/faqt/void-triples.py>;
#3>    rdfs:seeAlso <https://github.com/timrdf/DataFAQs/wiki/FAqT-Service> .

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
class VoIDTriplesGiven(faqt.Service):

   # Service metadata.
   label                  = 'void-triples'
   serviceDescriptionText = 'Evaluates the given datast based on whether its dereferenced annotations assert the void:triples property.'
   comment                = 'Giving the size of a dataset is useful.'
   serviceNameText        = 'void-triples' # Convention: Match 'name' below.
   name                   = 'void-triples' # This value determines the service URI relative to http://localhost:9090/
                                           # Convention: Use the name of this file for this value.
   def __init__(self):
      faqt.Service.__init__(self, servicePath = 'services/sadi/faqt')

   def getOrganization(self):
      result                      = self.Organization()
      result.mygrid_authoritative = True
      result.protegedc_creator    = 'lebot@rpi.edu'
      result.save()
      return result

   def getInputClass(self):
      return ns.VOID['Dataset']

   def getOutputClass(self):
      return ns.DATAFAQS['EvaluatedDataset']

   def process(self, input, output):
    
      store = surf.Store(reader = 'rdflib', writer = 'rdflib', rdflib_store = 'IOMemory')
      session = surf.Session(store) 
      store.load_triples(source = input.subject)
      output.datafaqs_resolved_triples = store.size();

      query = select('?triples').where((input.subject, ns.VOID['triples'], '?triples'))
      for count in store.execute(query):
         output.void_triples.append(count)
         output.rdf_type.append(ns.DATAFAQS['Satisfactory'])
         print str(store.size()) + ' dereferenced RDF triples asserted that ' + input.subject + ' has ' + str(count) + ' triples.'

      if ns.DATAFAQS['Satisfactory'] not in output.rdf_type:
         output.rdf_type.append(ns.DATAFAQS['Unsatisfactory'])
         print str(store.size()) + ' dereferenced RDF triples, but no void:triples asserted for ' + input.subject

      output.save()

# Used when Twistd invokes this service b/c it is sitting in a deployed directory.
resource = VoIDTriplesGiven()

# Used when this service is manually invoked from the command line (for testing).
if __name__ == '__main__':
   sadi.publishTwistedService(resource, port=9091)
