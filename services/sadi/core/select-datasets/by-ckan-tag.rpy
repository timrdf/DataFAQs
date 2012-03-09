#3> <> prov:specializationOf <https://raw.github.com/timrdf/DataFAQs/master/services/sadi/core/select-datasets/by-ckan-tag.rpy> .
#
#3> <http://sparql.tw.rpi.edu/services/datafaqs/core/select-datasets/by-ckan-tag>
#3>    a datafaqs:DatasetSelector .
#3> []
#3>   a prov:Activity;
#3>   prov:hadQualifiedAttribution [
#3>      a prov:Attribution;
#3>      prov:hadQualifiedEntity <http://sparql.tw.rpi.edu/services/datafaqs/core/select-datasets/by-ckan-tag>;
#3>      prov:adoptedPlan        <https://raw.github.com/timrdf/DataFAQs/master/services/sadi/core/select-datasets/by-ckan-tag.rpy>;
#3>   ];
#3> .

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
class DatasetsByCKANTag(sadi.Service):

   # Service metadata.
   label                  = 'by-ckan-tag'
   serviceDescriptionText = 'Return the datasets in the given CKAN group.'
   comment                = ''
   serviceNameText        = 'by-ckan-tag' # Convention: Match 'name' below.
   name                   = 'by-ckan-tag' # This value determines the service URI relative to http://localhost:9090/
                                            # Convention: Use the name of this file for this value.
   dev_port = 9110

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
      return ns.MOAT['Tag']

   def getOutputClass(self):
      return ns.MOAT['Tag']

   def process(self, input, output):
  
      print 'processing ' + input.subject
      if input.moat_name:
         print '   ' + input.moat_name.first
    
         Dataset = output.session.get_class(ns.DATAFAQS['CKANDataset'])

         self.ckan.package_search('tags:'+input.moat_name.first)
         tagged = self.ckan.last_message
         for dataset in tagged['results']:
            ckan_uri = 'http://thedatahub.org/dataset/' + dataset
            dataset = Dataset(ckan_uri)
            dataset.rdf_type.append(ns.DATAFAQS['CKANDataset'])
            dataset.rdf_type.append(ns.DCAT['Dataset'])
            dataset.save()
            output.dcterms_hasPart.append(dataset)
         output.save()

# Used when Twistd invokes this service b/c it is sitting in a deployed directory.
resource = DatasetsByCKANTag()

# Used when this service is manually invoked from the command line (for testing).
if __name__ == '__main__':
   print resource.name + ' running on port ' + str(resource.dev_port) + '. Invoke it with:'
   print 'curl -H "Content-Type: text/turtle" -d @my.ttl http://localhost:' + str(resource.dev_port) + '/' + resource.name
   sadi.publishTwistedService(resource, port=resource.dev_port)
