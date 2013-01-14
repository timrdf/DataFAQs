#3> <> prov:specializationOf <https://github.com/timrdf/DataFAQs/blob/master/services/sadi/faqt/naming/between-the-edges.py>;
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

# These are the namespaces we are using beyond those already available
# (see http://packages.python.org/SuRF/modules/namespace.html#registered-general-purpose-namespaces)
ns.register(moat='http://moat-project.org/ns#')
ns.register(ov='http://open.vocab.org/terms/')
ns.register(void='http://rdfs.org/ns/void#')
ns.register(dcat='http://www.w3.org/ns/dcat#')
ns.register(sd='http://www.w3.org/ns/sparql-service-description#')
ns.register(conversion='http://purl.org/twc/vocab/conversion/')
ns.register(datafaqs='http://purl.org/twc/vocab/datafaqs#')
ns.register(bte='http://purl.org/twc/vocab/between-the-edges/')

# The Service itself
class BetweenTheEdges(faqt.Service):

   # Service metadata.
   label                  = 'between-the-edges'
   serviceDescriptionText = 'Annotate any rdfs:Resource URI with an RDF description of the URI itself.'
   comment                = 'see https://github.com/timrdf/vsr/wiki/Characterizing-a-list-of-RDF-node-URIs'
   serviceNameText        = 'between-the-edges' # Convention: Match 'name' below.
   name                   = 'between-the-edges' # This value determines the service URI relative to http://localhost:9090/
                                                # Convention: Use the name of this file for this value.
   dev_port = 9235

   def __init__(self):
      # DATAFAQS_PROVENANCE_CODE_RAW_BASE                   +  servicePath  +  '/'  + self.serviceNameText
      # DATAFAQS_PROVENANCE_CODE_PAGE_BASE                  +  servicePath  +  '/'  + self.serviceNameText
      #
      # ^^ The source code location
      #    aligns with the deployment location \/
      #
      #                 DATAFAQS_BASE_URI  +  '/datafaqs/'  +  servicePath  +  '/'  + self.serviceNameText
      faqt.Service.__init__(self, servicePath = 'services/sadi/faqt/naming')
                                                                 # Use: pwd | sed 's/^.*services/services/'
   def getOrganization(self):
      result                      = self.Organization()
      result.mygrid_authoritative = True
      result.protegedc_creator    = 'lebot@rpi.edu'
      result.save()
      return result

   def getInputClass(self):
      return ns.RDFS['Resource']

   def getOutputClass(self):
      return ns.BTE['RDFNode']

   @staticmethod
   def length(input,output):
      output.bte_length = len(input.subject)
      
   @staticmethod
   def scheme(url6,output):
      if len(url6.scheme):
         output.bte_scheme = url6.scheme
      
   @staticmethod
   def netloc(url6,output):
      if len(url6.netloc):
         output.bte_netloc = url6.netloc
      
   @staticmethod
   def path(url6,output):
      if len(url6.path):
         output.bte_path = url6.path
      
   @staticmethod
   def fragment(url6,output):
      if len(url6.fragment):
         output.bte_fragment = url6.fragment
      
   def process(self, input, output):

      print 'processing ' + input.subject

      length = BetweenTheEdges.length(input,output)

      #
      # Using urlparse
      # e.g. ParseResult(scheme='http', netloc='www.cwi.nl:80', path='/%7Eguido/Python.html', params='', query='', fragment='')
      #
      url6 = urlparse(str(input.subject))
      scheme   = BetweenTheEdges.scheme(url6,output)
      netloc   = BetweenTheEdges.netloc(url6,output)
      path     = BetweenTheEdges.path(url6,output)
      fragment = BetweenTheEdges.fragment(url6,output)

      # <http://dailymed.nlm.nih.gov/dailymed/help.cfm#webservices> 
      #    a bte:RDFNode;
      #    bte:scheme "http";
      #    bte:netloc      "dailymed.nlm.nih.gov";
      #    bte:path                             "/dailymed/help.cfm";
      #    bte:fragment                                            "webservices";
      #    bte:length   57;

      #if scheme in ['http']:
      #   BetweenTheEdges.walkPath(path,outout)

      ####
      # Query a SPARQL endpoint
      #store = Store(reader = 'sparql_protocol', endpoint = 'http://dbpedia.org/sparql')
      #session = Session(store)
      #session.enable_logging = False
      #result = session.default_store.execute_sparql('select distinct ?type where {[] a ?type} limit 2')
      #if result:
      #   for binding in result['results']['bindings']:
      #      type  = binding['type']['value']
      #      print type
      ####

      # Query the RDF graph POSTed: input.session.default_store.execute

      # Walk through all Things in the input graph (using SuRF):
      # Thing = input.session.get_class(ns.OWL['Thing'])
      # for person in Thing.all():

      # Create a calss in the output graph:
      # Document = output.session.get_class(ns.FOAF['Document'])

      output.rdf_type.append(ns.BTE['RDFNode'])
      output.save()

# Used when Twistd invokes this service b/c it is sitting in a deployed directory.
resource = BetweenTheEdges()

# Used when this service is manually invoked from the command line (for testing).
if __name__ == '__main__':
   print resource.name + ' running on port ' + str(resource.dev_port) + '. Invoke it with:'
   print 'curl -H "Content-Type: text/turtle" -d @my.ttl http://localhost:' + str(resource.dev_port) + '/' + resource.name
   sadi.publishTwistedService(resource, port=resource.dev_port)
