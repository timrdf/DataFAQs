'''
Created on Jan 27, 2012

@author: yanningchen
'''
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
class vocabulary_count(sadi.Service):
    
   # Service metadata.
   label = 'vocabulary-count'
   serviceDescriptionText = 'Determines how many different predicates are there in the dataset.'
   comment = ''
   serviceNameText = 'vocabulary-count' # Convention: Match 'name' below.
   name = 'vocabulary-count' # This value determines the service URI relative to http://localhost:9090/
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
      
      temp_ns_list = []
      possible_temp_ns = ""
      temp_ns = ""
      
      for each_pred in predicate_set:
          pred_str_one = str(each_pred)
          min_len = len(pred_str_one)
          
          for each_other_pred in predicate_set:
              
              i = 0
              
              while(each_pred[i] == each_other_pred[i]):
                  temp_ns += each_other_pred[i] 
                  i = i + 1
                  if(i == len(each_pred) or i == len(each_other_pred)):
                      break
              i = 0
              
              if len(temp_ns) > 8: #meaningful
                  if len(temp_ns) < min_len:
                      possible_temp_ns = temp_ns
                      min_len = len(temp_ns)
              
          # find the highest index with / which indicate the end
          temp_ns = ""
          if(len(possible_temp_ns) > 0):
              tuple = possible_temp_ns.rpartition('/')
              temp_ns_list.append(tuple[0])
          possible_temp_ns = ""
          
      predicate_set = set(temp_ns_list)
      for row in predicate_set:
          print row
          output.datafaqs_namespaces.append("<" + row + ">")
                 
      output.save()

# Used when Twistd invokes this service b/c it is sitting in a deployed directory.
resource = vocabulary_count()

# Used when this service is manually invoked from the command line (for testing).
if __name__ == '__main__':
   sadi.publishTwistedService(resource, port=9110)
