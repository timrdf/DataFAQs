'''
Created on Jan 27, 2012

@author: yanningchen
'''

#3> <> prov:specializationOf <https://github.com/timrdf/DataFAQs/raw/master/services/sadi/faqt/resolvability.py>;
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

import ckanclient
import httplib
from urlparse import urlparse, urlunparse
import urllib

import httplib

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
    #print o
    connections = {'http' :httplib.HTTPConnection,
                   'https':httplib.HTTPSConnection}
    connection = connections[o.scheme](o.netloc)
    fullPath = urlunparse([None, None, o.path, o.params, o.query, o.fragment])
    connection.request('HEAD', fullPath)
    return connection.getresponse()

   # Get distinct result
def query_with_diff_results(query_graph, query_word):
    result = query_graph.query(query_word)
    result_list = []
    counter = 0
    for row in result:
        counter = counter + 1
        result_list.append(row)
      
    result_set = set(result_list)
    return result_set

def geomean(numbers):
    product = 1
    length = len(numbers)
    for n in numbers:
        product *= n ** (1.0 / length)
    return product 

def arthmean(numbers):
    sum = 0.0
    for n in numbers:
        sum += n
    return sum / float(len(numbers))

# The Service itself
class resolvability(faqt.Service):
    
   # Service metadata.
   label = 'resolvability'
   serviceDescriptionText = 'Determines how many different predicates are there in the dataset.'
   comment = ''
   serviceNameText = 'resolvability' # Convention: Match 'name' below.
   name = 'resolvability' # This value determines the service URI relative to http://localhost:9090/
   # Convention: Use the name of this file for this value.

   def __init__(self):
      faqt.Service.__init__(self, servicePath = 'services/sadi/faqt')
      #key = os.environ['X_CKAN_API_Key']
      #key = "45d9d0d5-2ae7-405f-a4dc-04560be5ace1"
      #if len(key) <= 1:
      #      print 'ERROR: https://github.com/timrdf/DataFAQs/wiki/Missing-CKAN-API-Key'
      #      sys.exit(1)
      #self.ckan = ckanclient.CkanClient(api_key=key)
      self.ckan = ckanclient.CkanClient()

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
      
      print 'processing ' + input.void_dataDump.first
      
      download_url = input.void_dataDump.first
      temp_graph = Graph()
        
      if(download_url.endswith(".nt")):
          temp_graph.parse(download_url, format='nt')
      elif(download_url.endswith(".rdf")):
          temp_graph.parse(download_url, format='rdf')
      elif(download_url.endswith(".n3")):
          temp_graph.parse(download_url, format='n3')

      if len(temp_graph) > 0:
        output.rdf_type.append(ns.DATAFAQS['Satisfactory'])
    
      # Find distinctive predicate
      query = "SELECT ?p WHERE {?s ?p ?o}"
      predicate_set = query_with_diff_results(temp_graph, query)
      print "Total number of " + str(len(predicate_set)) + " predicate"
      
      
      # Find distinctive subject
      query = "SELECT ?s WHERE {?s ?p ?o}"
      subject_set = query_with_diff_results(temp_graph, query)
      print "Total number of " + str(len(subject_set)) + " subject"
      
      # See if each element is resolvable
      unresolved = 0
      for element in subject_set:
          if(getHEAD(element).status == 404):
              unresolved = unresolved + 1
      
      resolvability = (len(subject_set) - unresolved) / float(len(subject_set))   
      output.datafaqs_resolvability.append(resolvability)
      
      #output.append(completeness_index)
  
      output.save()
      
# Used when Twistd invokes this service b/c it is sitting in a deployed directory.
resource = resolvability()

# Used when this service is manually invoked from the command line (for testing).
if __name__ == '__main__':
   sadi.publishTwistedService(resource, port=9111)
