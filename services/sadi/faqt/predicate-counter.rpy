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

import ckanclient
import httplib
from urlparse import urlparse, urlunparse
import urllib

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
    fullPath = urlunparse([None, None, o.path, o.params, o.query, o.fragment])
    connection.request('HEAD', fullPath)
    return connection.getresponse()

# The Service itself
class VoIDProperties(sadi.Service):

   # Service metadata.
   label = 'predicate-counter'
   serviceDescriptionText = 'Determines how many different predicates are there in the dataset.'
   comment = ''
   serviceNameText = 'predicate-counter' # Convention: Match 'name' below.
   name = 'predicate-counter' # This value determines the service URI relative to http://localhost:9090/
                                           # Convention: Use the name of this file for this value.
   def __init__(self): 
      key = os.environ['X_CKAN_API_Key'] 
      #key = "45d9d0d5-2ae7-405f-a4dc-04560be5ace1"
      sadi.Service.__init__(self)
      if len(key) <= 1:
            print 'ERROR: https://github.com/timrdf/DataFAQs/wiki/Missing-CKAN-API-Key'
            sys.exit(1)
      self.ckan = ckanclient.CkanClient(api_key=key)

   def getOrganization(self):
      result = self.Organization()
      result.mygrid_authoritative = True
      result.protegedc_creator = 'cheny18@rpi.edu'
      result.save()
      return result

   def getInputClass(self):
      return ns.VOID['Dataset']

   def getOutputClass(self):
      return ns.DATAFAQS['EvaluatedDataset']

   def process(self, input, output):
      
      print 'processing ' + input

      if input.void_dataDump:
         print 'processing ' + input.void_dataDump.first
     
       
         download_url = input.void_dataDump.first
         temp_graph = Graph()
           
         if(download_url.endswith(".nt")):
             temp_graph.parse(download_url, format='nt')
         elif(download_url.endswith(".rdf")):
             temp_graph.parse(download_url, format='rdf')
         elif(download_url.endswith(".n3")):
             temp_graph.parse(download_url, format='n3')

         #if len(temp_graph) > 0:
         #  output.rdf_type.append(ns.DATAFAQS['Satisfactory'])
         result = temp_graph.query("SELECT DISTINCT ?p WHERE {[] ?p []} LIMIT 20")
         
         predicate_counter = 0
         for row in result:
             predicate_counter = predicate_counter + 1
             print row
             
         if predicate_counter > 10:
             output.rdf_type.append(ns.DATAFAQS['Satisfactory'])
    
      if ns.DATAFAQS['Satisfactory'] not in output.rdf_type:
         output.rdf_type.append(ns.DATAFAQS['Unsatisfactory'])
         print "Too few predicate in " + input.subject + ", only " + str(predicator_counter) + " spotted"

      output.save()

# Used when Twistd invokes this service b/c it is sitting in a deployed directory.
resource = VoIDProperties()

# Used when this service is manually invoked from the command line (for testing).
if __name__ == '__main__':
   sadi.publishTwistedService(resource, port=9103)

