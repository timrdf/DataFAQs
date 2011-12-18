import sadi
from rdflib import *
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
connections = {'http' :httplib.HTTPConnection,
               'https':httplib.HTTPSConnection}

# These are the namespaces we are using beyond those already available
# (see http://packages.python.org/SuRF/modules/namespace.html#registered-general-purpose-namespaces)
ns.register(moat='http://moat-project.org/ns#')
ns.register(ov='http://open.vocab.org/terms/')
ns.register(datafaqs='http://purl.org/twc/vocab/datafaqs#')
ns.register(void='http://rdfs.org/ns/void#')

THEDATAHUB = 'http://thedatahub.org/dataset/'

def getResponse(url):
    # Ripped from https://github.com/timrdf/csv2rdf4lod-automation/blob/master/bin/util/pcurl.py
    o = urlparse(str(url))
    #print o
    connection = connections[o.scheme](o.netloc)
    fullPath = urlunparse([None,None,o.path,o.params,o.query,o.fragment])
    connection.request('GET',fullPath)
    return connection.getresponse()

# The Service itself
class VoIDTriplesGiven(sadi.Service):

    # Service metadata.
    label                  = 'void:Dataset has void:triples asserted.'
    serviceDescriptionText = 'Reports the void:triples of the given dataset.'
    comment                = 'Giving the size of a dataset is useful.'
    serviceNameText        = 'VoIDTriplesGiven'
    name                   = 'VoIDTriplesGiven' # This value determines the service URI relative to http://localhost:9090/

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
        return ns.DATAFAQS['SizedDataset']

    def process(self, input, output):
        ckan_id = input.dcterms_identifier.first
        print 'processing ' + input.subject + ' ckan_id ' + ckan_id
     
        response = getResponse(input.subject)
        print response.status 
        print response.getheaders()
 
        lodlinks = Graph()
        lodlinks.parse(input.subject, format="xml")
        input.void_triples = len(lodlinks)

        output.save()

# Used when Twistd invokes this service b/c it is sitting in a deployed directory.
resource = VoIDTriplesGiven()

# Used when this service is manually invoked from the command line (for testing).
# The service listens on port 9090
if __name__ == '__main__':
    sadi.publishTwistedService(resource, port=9090)
