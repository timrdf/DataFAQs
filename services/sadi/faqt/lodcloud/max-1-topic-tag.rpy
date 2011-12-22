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
class MaxOneTopicTag(sadi.Service):

   # Service metadata.
   label                  = 'max-1-topic-tag'
   serviceDescriptionText = 'Fails void:Datasets that are tagged with more than one thedatahub.org/group/lodcloud tag for "topic information".'
   comment                = 'http://www.w3.org/wiki/TaskForces/CommunityProjects/LinkingOpenData/DataSets/CKANmetainformation states "One of" {media, geographic, lifesciences, publications, government, ecommerce, socialweb, usergeneratedcontent, schemata, crossdomain}'
   serviceNameText        = 'max-1-topic-tag' # Convention: Match 'name' below.
   name                   = 'max-1-topic-tag' # This value determines the service URI relative to http://localhost:9090/
                                              # Convention: Use the name of this file for this value.
   def __init__(self): 
      sadi.Service.__init__(self)

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

   topics = ['media', 'geographic', 'lifesciences', 'publications', 'government', 'ecommerce', 'socialweb', 'usergeneratedcontent', 'schemata', 'crossdomain']

   def process(self, input, output):
 
      tags = []
      for tag_uri in input.moat_taggedWithTag:
         tag = re.sub('http://.*tag/','',tag_uri)
         print tag_uri + ' -> ' + tag
         tags.append(tag)

      count = 0
      for topic in self.topics:
         print input.subject + ' have ' + topic + ' ?'
         if topic in tags:
            print input.subject + ' has ' + topic
            count += 1

      if count > 1:
         output.rdf_type.append(ns.DATAFAQS['Unsatisfactory'])
      else:
         output.rdf_type.append(ns.DATAFAQS['Satisfactory'])

      output.save()

# Used when Twistd invokes this service b/c it is sitting in a deployed directory.
resource = MaxOneTopicTag()

# Used when this service is manually invoked from the command line (for testing).
if __name__ == '__main__':
   sadi.publishTwistedService(resource, port=9104)
