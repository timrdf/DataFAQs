import re
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
import ckanclient

import httplib
from urlparse import urlparse, urlunparse
import urllib
import urllib2

# These are the namespaces we are using beyond those already available
# (see http://packages.python.org/SuRF/modules/namespace.html#registered-general-purpose-namespaces)
ns.register(moat='http://moat-project.org/ns#')
ns.register(ov='http://open.vocab.org/terms/')
ns.register(dcat='http://www.w3.org/ns/dcat#')
ns.register(void='http://rdfs.org/ns/void#')
ns.register(conversion='http://purl.org/twc/vocab/conversion/')
ns.register(datafaqs='http://purl.org/twc/vocab/datafaqs#')

# The Service itself
class DatasetsByCKANGroup(sadi.Service):

   # Service metadata.
   label                  = 'by-ckan-group'
   serviceDescriptionText = 'Return the datasets in the given CKAN group.'
   comment                = ''
   serviceNameText        = 'by-ckan-group' # Convention: Match 'name' below.
   name                   = 'by-ckan-group' # This value determines the service URI relative to http://localhost:9090/
                                            # Convention: Use the name of this file for this value.
   def __init__(self): 
      sadi.Service.__init__(self)

      # Instantiate the CKAN client.
      # http://docs.python.org/library/configparser.html (could use this technique)
      key = os.environ['X_CKAN_API_Key'] # See https://github.com/timrdf/DataFAQs/wiki/Missing-CKAN-API-Key'
      if len(key) <= 1:
          print 'ERROR: https://github.com/timrdf/DataFAQs/wiki/Missing-CKAN-API-Key'
          sys.exit(1)
      self.ckan = ckanclient.CkanClient(api_key=key)

   def getOrganization(self):
      result                      = self.Organization()
      result.mygrid_authoritative = True
      result.protegedc_creator    = 'lebot@rpi.edu'
      result.save()
      return result

   def getInputClass(self):
      return ns.DATAFAQS['CKANGroup']

   def getOutputClass(self):
      return ns.DATAFAQS['DatasetCollection']

   def process(self, input, output):
   
      ckan_instance = re.sub('group/.*','group/',input.subject)
      ckan_group_id = re.sub(ckan_instance,'',input.subject)

      Dataset = output.session.get_class(ns.DATAFAQS['CKANDataset'])
      for dataset_id in self.ckan.group_entity_get(ckan_group_id)['packages']:
         ckan_uri = 'http://thedatahub.org/dataset/' + dataset_id
         dataset = Dataset(ckan_uri)
         dataset.rdf_type.append(ns.DATAFAQS['CKANDataset'])
         dataset.rdf_type.append(ns.DCAT['Dataset'])
         dataset.save()
         output.dcterms_hasPart.append(dataset)

      output.save()

# Used when Twistd invokes this service b/c it is sitting in a deployed directory.
resource = DatasetsByCKANGroup()

# Used when this service is manually invoked from the command line (for testing).
if __name__ == '__main__':
   port = 9098
   print 'curl -H "Content-Type: text/turtle" -d @my.ttl http://localhost:' + str(port) + '/' + resource.name
   sadi.publishTwistedService(resource, port=port)
