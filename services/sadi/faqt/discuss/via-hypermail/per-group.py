#3> <> prov:specializationOf <#TEMPLATE/path/to/public/source-code.py>;
#3>    rdfs:seeAlso <https://github.com/timrdf/DataFAQs/wiki/FAqT-Service> .

import faqt

import sadi
from rdflib import *
import surf

from surf import *
from surf.query import a, select

import rdflib
rdflib.plugin.register('sparql', rdflib.query.Processor,
                       'rdfextras.sparql.processor', 'Processor')
rdflib.plugin.register('sparql', rdflib.query.Result,
                       'rdfextras.sparql.query', 'SPARQLQueryResult')

import httplib
from urlparse import urlparse, urlunparse
import urllib
import urllib2

from BeautifulSoup import BeautifulSoup

# These are the namespaces we are using beyond those already available
# (see http://packages.python.org/SuRF/modules/namespace.html#registered-general-purpose-namespaces)
ns.register(moat='http://moat-project.org/ns#')
ns.register(ov='http://open.vocab.org/terms/')
ns.register(void='http://rdfs.org/ns/void#')
ns.register(dcat='http://www.w3.org/ns/dcat#')
ns.register(dcterms='http://purl.org/dc/terms/')
ns.register(sd='http://www.w3.org/ns/sparql-service-description#')
ns.register(conversion='http://purl.org/twc/vocab/conversion/')
ns.register(datafaqs='http://purl.org/twc/vocab/datafaqs#')
ns.register(sioc='http://rdfs.org/sioc/ns#')

# The Service itself
class W3CMailingList(faqt.Service):

   # Service metadata.
   label                  = 'per-group'
   serviceDescriptionText = 'Returns an RDF description of the given W3C Mailing List.'
   comment                = ''
   serviceNameText        = 'per-group' # Convention: Match 'name' below.
   name                   = 'per-group' # This value determines the service URI relative to http://localhost:9229/
                                        # Convention: Use the name of this file for this value.
   dev_port = 9229

   def __init__(self):
      # DATAFAQS_PROVENANCE_CODE_RAW_BASE                   +  servicePath  +  '/'  + self.serviceNameText
      # DATAFAQS_PROVENANCE_CODE_PAGE_BASE                  +  servicePath  +  '/'  + self.serviceNameText
      #
      # ^^ The source code location
      #    aligns with the deployment location \/
      #
      #                 DATAFAQS_BASE_URI  +  '/datafaqs/'  +  servicePath  +  '/'  + self.serviceNameText
      faqt.Service.__init__(self, servicePath = 'services/sadi/faqt/discuss/via-hypermail')

   def getOrganization(self):
      result                      = self.Organization()
      result.mygrid_authoritative = True
      result.protegedc_creator    = 'lebot@rpi.edu'
      result.save()
      return result

   # This archive was generated by hypermail 2.2.0+W3C-0.50
   def getInputClass(self):
      return ns.SIOC['Space']

   def getOutputClass(self):
      return ns.DATAFAQS['EvaluatedDataset']

   def process(self, input, output):

      print 'processing ' + input.subject

      Container = output.session.get_class(ns.SIOC['Container'])

      soup = None
      try:
         page  = urllib2.urlopen(input.subject)
         soup  = BeautifulSoup(page)
      except:
         return

      for year in soup.findAll('tbody'):
         for row in year.findAll('tr'):
            cells = row.findAll('td')
            if len(cells[0].findAll('a')) > 0:
               period      = cells[0].findAll('a')[0]['href'].rstrip('/')
               periodLabel = cells[0].findAll('a')[0].string
               count       = cells[4].string              # column 'messages'
               for cell in cells:
                  for a in cell.findAll('a'):
                     if a.string == 'by author':
                        print period + ' ' + count + ' ' + input.subject+'/'+a['href']
                        periodR = Container(input.subject+'/'+period)
                        periodR.sioc_has_space = output
                        periodR.sioc_num_items = int(count)
                        periodR.dcterms_date   = str(periodLabel)
                        periodR.save()
                        output.rdf_type.append(ns.DATAFAQS['Satisfactory'])
                        print '----'

      # Query the RDF graph POSTed: input.session.default_store.execute

      # Walk through all Things in the input graph (using SuRF):
      # Thing = input.session.get_class(ns.OWL['Thing'])
      # for person in Thing.all():

      if ns.DATAFAQS['Satisfactory'] not in output.rdf_type:
         output.rdf_type.append(ns.DATAFAQS['Unsatisfactory'])

      output.save()

# Used when Twistd invokes this service b/c it is sitting in a deployed directory.
resource = W3CMailingList()

# Used when this service is manually invoked from the command line (for testing).
if __name__ == '__main__':
   print resource.name + ' running on port ' + str(resource.dev_port) + '. Invoke it with:'
   print 'curl -H "Content-Type: text/turtle" -d @my.ttl http://localhost:' + str(resource.dev_port) + '/' + resource.name
   sadi.publishTwistedService(resource, port=resource.dev_port)
