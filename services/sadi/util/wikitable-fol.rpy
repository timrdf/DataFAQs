#3> <> prov:specializationOf <https://raw.github.com/timrdf/DataFAQs/master/services/sadi/util/wikitable-fol.rpy>;
#3>    rdfs:seeAlso <https://github.com/timrdf/DataFAQs/wiki/FAqT-Service> .
#3>
#3> <http://sparql.tw.rpi.edu/services/datafaqs/util/wikitable-fol>
#3>    a moby:serviceDescription .
#3> []
#3>    a prov:Activity;
#3>    prov:hadQualifiedAttribution [
#3>       a prov:Attribution;
#3>       prov:hadQualifiedEntity <http://sparql.tw.rpi.edu/services/datafaqs/util/wikitable-fol>;
#3>       prov:adoptedPlan        <https://raw.github.com/timrdf/DataFAQs/master/services/sadi/util/wikitable-fol.rpy>;
#3>    ];
#3> .
#3> <https://raw.github.com/timrdf/DataFAQs/master/services/sadi/util/wikitable-fol.rpy>
#3>    foaf:homepage <https://github.com/timrdf/DataFAQs/blob/master/services/sadi/util/wikitable-fol.rpy> .

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
from urllib2 import Request, urlopen, URLError, HTTPError

from BeautifulSoup import BeautifulSoup          # For processing HTML

# These are the namespaces we are using beyond those already available
# (see http://packages.python.org/SuRF/modules/namespace.html#registered-general-purpose-namespaces)
ns.register(moat='http://moat-project.org/ns#')
ns.register(ov='http://open.vocab.org/terms/')
ns.register(void='http://rdfs.org/ns/void#')
ns.register(dcat='http://www.w3.org/ns/dcat#')
ns.register(vann='http://purl.org/vocab/vann/')
ns.register(sd='http://www.w3.org/ns/sparql-service-description#')
ns.register(conversion='http://purl.org/twc/vocab/conversion/')
ns.register(datafaqs='http://purl.org/twc/vocab/datafaqs#')
ns.register(prov='http://www.w3.org/ns/prov#')
ns.register(example='http://example.org/ns#')

PREFIX = 0
LOCAL  = 1

# The Service itself
class WikiTableFOL(sadi.Service):

   # Service metadata.
   label                  = 'wikitable-fol'
   serviceDescriptionText = 'Scrapes a mediawiki page for tables created with mediawiki markup to list FOL-like expressions.'
   comment                = 'e.g. FOL-like expression: entity(id,[attr_1=val_1,...,attr_n=val_n])'
   serviceNameText        = 'wikitable-fol' # Convention: Match 'name' below.
   name                   = 'wikitable-fol' # This value determines the service URI relative to http://localhost:9090/
                                            # Convention: Use the name of this file for this value.
   dev_port = 9116

   def __init__(self): 
      sadi.Service.__init__(self)
      self.regex = re.compile("([a-zA-Z0-9]+\([^)]*\))")
      self.namespaces = {}
      self.errors = {}

   def getOrganization(self):
      result                      = self.Organization()
      result.mygrid_authoritative = True
      result.protegedc_creator    = 'lebot@rpi.edu'
      result.save()
      return result

   def getInputClass(self):
      return ns.FOAF['Document']

   def getOutputClass(self):
      return ns.FOAF['Document']

   def process(self, input, output):

      print 'processing ' + input.subject

      page = urllib2.urlopen(input.subject)
      soup = BeautifulSoup(page)

      Thing = output.session.get_class(ns.EXAMPLE['Expression'])
      Error = output.session.get_class(ns.DATAFAQS['Error'])

      count = 0
      #for table in soup('table'):
      #   for tr in table.findAll('tr'):
      for td in soup('td'):
         for expression in self.regex.findall(str(td.string)):
            count = count + 1
            print '   document contained expression ' + expression
            topic = Thing()
            topic.rdf_value = expression
            topic.prov_hadLocation = count
            topic.save()
            output.dcterms_subject.append(topic)
            output.rdf_type.append(ns.DATAFAQS['Satisfactory'])
            output.save()

      for span in soup('span'):
         for expression in self.regex.findall(str(span.string)):
            count = count + 1
            print '   document contained expression ' + expression
            topic = Thing()
            topic.rdf_value = str(expression).strip()
            topic.prov_hadLocation = count
            topic.save()
            output.dcterms_subject.append(topic)
            output.rdf_type.append(ns.DATAFAQS['Satisfactory'])
            try:
               output.save()
            except:
               print 'caught exception'

      if ns.DATAFAQS['Satisfactory'] not in output.rdf_type:
         output.rdf_type.append(ns.DATAFAQS['Unsatisfactory'])


# Used when Twistd invokes this service b/c it is sitting in a deployed directory.
resource = WikiTableFOL()

# Used when this service is manually invoked from the command line (for testing).
if __name__ == '__main__':
   print resource.name + ' running on port ' + str(resource.dev_port) + '. Invoke it with:'
   print 'curl -H "Content-Type: text/turtle" -d @my.ttl http://localhost:' + str(resource.dev_port) + '/' + resource.name
   sadi.publishTwistedService(resource, port=resource.dev_port)
