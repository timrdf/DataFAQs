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

connections = {'http' :httplib.HTTPConnection,
             'https':httplib.HTTPSConnection}

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
class DatasetsByCKANTag(faqt.Service):

   # Service metadata.
   label                  = 'by-ckan-tag'
   serviceDescriptionText = 'Return the datasets that are tagged with ALL of the moat:Tags given.'
   comment                = 'This service provides the INTERSECTION of tags. To obtain the UNION, call it multiple times with the individual tags.'
   serviceNameText        = 'by-ckan-tag' # Convention: Match 'name' below.
   name                   = 'by-ckan-tag' # This value determines the service URI relative to http://localhost:9090/
                                          # Convention: Use the name of this file for this value.
   dev_port = 9110
   startedLifeAt = None
   lastCalled    = None
   intersected   = None

   def __init__(self):
      faqt.Service.__init__(self, servicePath = 'services/sadi/core/select-datasets')
      # Instantiate the CKAN client.
      # http://docs.python.org/library/configparser.html (could use this technique)
      #key = os.environ['X_CKAN_API_Key'] # See https://github.com/timrdf/DataFAQs/wiki/Missing-CKAN-API-Key'
      #if len(key) <= 1:
      #    print 'ERROR: https://github.com/timrdf/DataFAQs/wiki/Missing-CKAN-API-Key'
      #    sys.exit(1)
      #self.ckan = ckanclient.CkanClient(api_key=key)
      self.ckan = ckanclient.CkanClient()
      self.startedLifeAt = datetime.datetime.now()

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

   def annotateServiceDescription(self, desc):
      print 'annotate ' + desc.subject
      Thing       = desc.session.get_class(ns.OWL['Thing'])
      Attribution = desc.session.get_class(ns.PROV['Attribution'])
      Entity      = desc.session.get_class(ns.PROV['Entity'])
      Plan        = desc.session.get_class(ns.PROV['Plan'])
      Agent       = desc.session.get_class(ns.PROV['Agent'])
      Page        = desc.session.get_class(ns.FOAF['Page'])
      plan = Plan('https://raw.github.com/timrdf/DataFAQs/master/services/sadi/core/select-datasets/by-ckan-tag.rpy')
      plan.foaf_homepage.append(Thing('https://github.com/timrdf/DataFAQs/blob/master/services/sadi/core/select-datasets/by-ckan-tag.rpy')) 
      plan.save()
      attr = Attribution()
      attr.prov_entity  = Agent('') #Entity('http://sparql.tw.rpi.edu/services/datafaqs/core/select-datasets/by-ckan-tag')
      attr.prov_hadPlan = plan
      attr.dcterms_date.append(str(self.startedLifeAt))
      attr.save()
      desc.dcterms_subject.append(Agent(''))
      desc.save()

   def process(self, input, output):
      print 'processing ' + input.subject
     
      # TODO: handle case where moat_name is not present - parse the URI (yuck).
 
      if input.moat_name:
         print '   ' + input.moat_name.first

         #if self.lastCalled is None:
         #   self.lastCalled = datetime.datetime.now()

         #else:
         #   sinceLast = datetime.datetime.now() - self.lastCalled
         #   if sinceLast.seconds < 60:
         #      print ' was called before ' + str(sinceLast.seconds) + ' seconds ago (< 60); skipping'
               #self.doIt(output)
               #return
         #   else:
         #      print 'need to refresh'
      
         Dataset = output.session.get_class(ns.DATAFAQS['CKANDataset'])

         # Original: This does union, but we want intersection.

         # ORIG: self.ckan.package_search('tags:'+input.moat_name.first)
         # WORKS: self.ckan.package_search('tags:helpme')
         # DOES NOT WORK: self.ckan.package_search('tags:helpme&tags:lod')
         # DOES NOT WORK: self.ckan.package_search('tags:helpme&amp;tags:lod')
         # DOES NOT WORK: self.ckan.package_search(['tags:helpme','tags:lod'])
#         tagged = self.ckan.last_message
#         print dir(tagged)
#         for dataset in tagged['results']:
#            ckan_uri = 'http://thedatahub.org/dataset/' + dataset
#            dataset = Dataset(ckan_uri)
#            dataset.rdf_type.append(ns.DATAFAQS['CKANDataset'])
#            dataset.rdf_type.append(ns.DCAT['Dataset'])
#            dataset.save()
#            output.dcterms_hasPart.append(dataset)
#         output.save()
         # FWIW, http://thedatahub.org/api/search/dataset?tags=helpme&amp;tags=lod 
         # and
         #       http://thedatahub.org/api/search/dataset?q=tags:helpme&amp;tags:lod
         #       searches intersection of tags.

         # Take 2 (failed)
#
         Tag     = input.session.get_class(ns.MOAT['Tag'])
#
#         query = 'http://thedatahub.org/api/search/dataset?'
#         amp = ''
#         for tag in Tag.all():
#            print 'all: ' + tag.moat_name.first
#            query = query + amp + 'tags=' + tag.moat_name.first
#            amp = '&amp;'
#         print 'query: ' + query
#
#         response = self.getResponse('http://thedatahub.org/api/search/dataset?tags=helpme&amp;tags=lod')
#         if response.status == 200:
#            print '200!'
#            print response.msg.dict
#            text = response.read()
#            print text
#            data = json.loads(text)
#            print 'data! ' + str(data['count'])
#            print data
#            for dataset in data['results']:
#               print '  -> ' + dataset

         # Take 3 - ckan doesn't accept multiple tags in search. (or is too poorly documented)
         Tag = input.session.get_class(ns.MOAT['Tag'])
#         sets = {}
#         for tag in Tag.all():
#            self.ckan.package_search('tags:'+tag.moat_name.first)
#            tagged = self.ckan.last_message
#
         #   sets[tag.moat_name.first] = set()
         #   for dataset in tagged['results']:
         #      #print tag.moat_name.first + ' : ' + dataset
         #      sets[tag.moat_name.first].add(dataset)
         #self.intersected = reduce(lambda x,y: x & y, sets.values())
         #self.doIt(output)

         # Take 4 - from Sean Hammond
         query = ''
         plus = ''
         for tag in Tag.all():
            query = query + plus + 'tags:' + tag.moat_name.first
            plus = '+'
         self.ckan.package_search(query) #self.ckan.package_search('tags:lod+tags:helpme')
         tagged = self.ckan.last_message
         for dataset in tagged['results']:
            ckan_uri = 'http://thedatahub.org/dataset/' + dataset
            dataset = Dataset(ckan_uri)
            dataset.rdf_type.append(ns.DATAFAQS['CKANDataset'])
            dataset.rdf_type.append(ns.DCAT['Dataset'])
            dataset.save()
            output.dcterms_hasPart.append(dataset)
         output.save()

   def doIt(self, output):
      Dataset = output.session.get_class(ns.DATAFAQS['CKANDataset'])
      for dataset in self.intersected:
         ckan_uri = 'http://thedatahub.org/dataset/' + dataset
         dataset = Dataset(ckan_uri)
         dataset.rdf_type.append(ns.DATAFAQS['CKANDataset'])
         dataset.rdf_type.append(ns.DCAT['Dataset'])
         dataset.save()
         output.dcterms_hasPart.append(dataset)
      output.save()

   def getResponse(self, url):
      # Ripped from https://github.com/timrdf/csv2rdf4lod-automation/blob/master/bin/util/pcurl.py
      o = urlparse(str(url))
      #print o
      connection = connections[o.scheme](o.netloc)
      fullPath = urlunparse([None,None,o.path,o.params,o.query,o.fragment])
      connection.request('GET',fullPath)
      return connection.getresponse()

# Used when Twistd invokes this service b/c it is sitting in a deployed directory.
resource = DatasetsByCKANTag()

# Used when this service is manually invoked from the command line (for testing).
if __name__ == '__main__':
   print resource.name + ' running on port ' + str(resource.dev_port) + '. Invoke it with:'
   print 'curl -H "Content-Type: text/turtle" -d @my.ttl http://localhost:' + str(resource.dev_port) + '/' + resource.name
   sadi.publishTwistedService(resource, port=resource.dev_port)
