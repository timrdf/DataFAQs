#3> <> prov:specializationOf <https://raw.github.com/timrdf/DataFAQs/master/services/sadi/core/select-datasets/by-ckan-installation.rpy> .
#
#3> <http://sparql.tw.rpi.edu/services/datafaqs/core/select-datasets/by-ckan-installation>
#3>    a datafaqs:DatasetSelector .
#3> []
#3>   a prov:Activity;
#3>   prov:hadQualifiedAttribution [
#3>      a prov:Attribution;
#3>      prov:hadQualifiedEntity <http://sparql.tw.rpi.edu/services/datafaqs/core/select-datasets/by-ckan-installation>;
#3>      prov:adoptedPlan        <https://raw.github.com/timrdf/DataFAQs/master/services/sadi/core/select-datasets/by-ckan-installation.rpy>;
#3>   ];
#3> .

import faqt

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

import json

import datetime

# These are the namespaces we are using beyond those already available
# (see http://packages.python.org/SuRF/modules/namespace.html#registered-general-purpose-namespaces)
ns.register(moat='http://moat-project.org/ns#')
ns.register(ov='http://open.vocab.org/terms/')
ns.register(dcat='http://www.w3.org/ns/dcat#')
ns.register(void='http://rdfs.org/ns/void#')
ns.register(conversion='http://purl.org/twc/vocab/conversion/')
ns.register(datafaqs='http://purl.org/twc/vocab/datafaqs#')
ns.register(prov='http://www.w3.org/ns/prov#')
ns.register(foaf='http://xmlns.com/foaf/0.1/')

# The Service itself
class DatasetsByCKANInstallation(faqt.Service):

   # Service metadata.
   label                  = 'by-ckan-installation'
   serviceDescriptionText = 'Return the datasets that are listed in the given CKAN installation.'
   comment                = 'e.g. CKAN installations: http://hub.healthdata.gov/ or http://thedatahub.org/'
   serviceNameText        = 'by-ckan-installation' # Convention: Match 'name' below.
   name                   = 'by-ckan-installation' # This value determines the service URI relative to http://localhost:9090/
                                          # Convention: Use the name of this file for this value.
   dev_port = 9233
   startedLifeAt = None

   def __init__(self):
      faqt.Service.__init__(self, servicePath = 'services/sadi/core/select-datasets')
      self.startedLifeAt = datetime.datetime.now()

   def getOrganization(self):
      result                      = self.Organization()
      result.mygrid_authoritative = True
      result.protegedc_creator    = 'lebot@rpi.edu'
      result.save()
      return result

   def getInputClass(self):
      return ns.DATAFAQS['CKAN']

   def getOutputClass(self):
      return ns.DATAFAQS['CKAN']

   #def annotateServiceDescription(self, desc):
   #   print 'annotate ' + desc.subject
   #   Thing       = desc.session.get_class(ns.OWL['Thing'])
   #   Attribution = desc.session.get_class(ns.PROV['Attribution'])
   #   Entity      = desc.session.get_class(ns.PROV['Entity'])
   #   Plan        = desc.session.get_class(ns.PROV['Plan'])
   #   Agent       = desc.session.get_class(ns.PROV['Agent'])
   #   Page        = desc.session.get_class(ns.FOAF['Page'])
   #   plan = Plan('https://raw.github.com/timrdf/DataFAQs/master/services/sadi/core/select-datasets/by-ckan-installation.rpy')
   #   plan.foaf_homepage.append(Thing('https://github.com/timrdf/DataFAQs/blob/master/services/sadi/core/select-datasets/by-ckan-installation.rpy')) 
   #   plan.save()
   #   attr = Attribution()
   #   attr.prov_entity  = Agent('') #Entity('http://sparql.tw.rpi.edu/services/datafaqs/core/select-datasets/by-ckan-installation')
   #   attr.prov_hadPlan = plan
   #   attr.dcterms_date.append(str(self.startedLifeAt))
   #   attr.save()
   #   desc.dcterms_subject.append(Agent(''))
   #   desc.save()

   def process(self, input, output):

      Dataset = output.session.get_class(ns.DATAFAQS['CKANDataset'])
      Agent   = output.session.get_class(ns.PROV['Agent'])

      print 'processing ' + input.subject
      base = input.subject.replace('/$','') 
      api  = base

      ckan = ckanclient.CkanClient(input.subject+'/api')

      for identifier in ckan.package_register_get():
         dataset = Dataset(base + '/dataset/' + identifier)
         print dataset.subject
         dataset.dcterms_identifier = identifier
         dataset.rdf_type.append(ns.DATAFAQS['CKANDataset'])
         dataset.rdf_type.append(ns.DCAT['Dataset'])
         attribution = Agent(re.sub('(http://[^/]*)/.*$','\\1',dataset.subject))
         dataset.prov_wasAssociatedWith.append(attribution)
         dataset.save()
         output.dcterms_hasPart.append(dataset)
         output.save()

# Used when Twistd invokes this service b/c it is sitting in a deployed directory.
resource = DatasetsByCKANInstallation()

# Used when this service is manually invoked from the command line (for testing).
if __name__ == '__main__':
   print resource.name + ' running on port ' + str(resource.dev_port) + '. Invoke it with:'
   print 'curl -H "Content-Type: text/turtle" -d @my.ttl http://localhost:' + str(resource.dev_port) + '/' + resource.name
   sadi.publishTwistedService(resource, port=resource.dev_port)
