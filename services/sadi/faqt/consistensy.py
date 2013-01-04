'''
Created on Jan 28, 2012

@author: yanningchen
'''

#3> <> prov:specializationOf <https://github.com/timrdf/DataFAQs/raw/master/services/sadi/faqt/consistensy.py>;
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
class consistancy(faqt.Service):
    
   # Service metadata.
   label = 'consistancy'
   serviceDescriptionText = 'Determines how many different predicates are there in the dataset.'
   comment = ''
   serviceNameText = 'consistancy' # Convention: Match 'name' below.
   name = 'consistancy' # This value determines the service URI relative to http://localhost:9090/
   # Convention: Use the name of this file for this value.

   def __init__(self):
      faqt.Service.__init__(self, servicePath = 'services/sadi/faqt')
      #key = os.environ['X_CKAN_API_Key']
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
      
      # Find distinctive object
      query = "SELECT ?p WHERE {?s ?p ?o}"
      predicate_set = query_with_diff_results(temp_graph, query)
      print "Total number of " + str(len(predicate_set)) + " predicate"
      
      overall_index = 0
      datatype_counter = 0
      for row in predicate_set:
          sub_query = "SELECT ?o WHERE {?s <" + str(row) + "> ?o}"
          csp_objs = query_with_diff_results(temp_graph, sub_query)
          temp_element = csp_objs.pop()
          if type(temp_element) is rdflib.Literal:
                  datatype_cache = temp_element.__getstate__()
                  for each_obj in csp_objs:
                      if type(each_obj) is rdflib.Literal:
                          if each_obj.__getstate__() is datatype_cache:
                              datatype_counter += 1
                  if (datatype_counter == (len(csp_objs) - 1)):
                    overall_index += 1    
          datatype_counter = 0
          datatype_cache = None
                  
      consistency_index = float(overall_index) / len(predicate_set)
      
      output.datafaqs_consistency.append(ns.DATAFAQS["" + str(consistency_index)])
      
      output.save()

# Used when Twistd invokes this service b/c it is sitting in a deployed directory.
resource = consistancy()

# Used when this service is manually invoked from the command line (for testing).
if __name__ == '__main__':
   sadi.publishTwistedService(resource, port=9112)
