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

# These are the namespaces we are using beyond those already available
# (see http://packages.python.org/SuRF/modules/namespace.html#registered-general-purpose-namespaces)
ns.register(moat='http://moat-project.org/ns#')
ns.register(ov='http://open.vocab.org/terms/')
ns.register(void='http://rdfs.org/ns/void#')
ns.register(dcat='http://www.w3.org/ns/dcat#')
ns.register(sd='http://www.w3.org/ns/sparql-service-description#')
ns.register(conversion='http://purl.org/twc/vocab/conversion/')
ns.register(datafaqs='http://purl.org/twc/vocab/datafaqs#')

# The Service itself
class VisKoPlanner(faqt.Service):

   # Service metadata.
   label                  = 'viko-planner'
   serviceDescriptionText = 'Return a PROV-O description of the service invocation chain to use to produce the requested visualization.'
   comment                = ''
   serviceNameText        = 'viko-planner' # Convention: Match 'name' below.
   name                   = 'viko-planner' # This value determines the service URI relative to http://localhost:9228/
                                           # Convention: Use the name of this file for this value.
   dev_port = 9228

   def __init__(self):
      # DATAFAQS_PROVENANCE_CODE_RAW_BASE                   +  servicePath  +  '/'  + self.serviceNameText
      # DATAFAQS_PROVENANCE_CODE_PAGE_BASE                  +  servicePath  +  '/'  + self.serviceNameText
      #
      # ^^ The source code location
      #    aligns with the deployment location \/
      #
      #                 DATAFAQS_BASE_URI  +  '/datafaqs/'  +  servicePath  +  '/'  + self.serviceNameText
      faqt.Service.__init__(self, servicePath = 'services/sadi/core/select-faqts')

   def getOrganization(self):
      result                      = self.Organization()
      result.mygrid_authoritative = True
      result.protegedc_creator    = 'lebot@rpi.edu'
      result.save()
      return result

   def getInputClass(self):
      return ns.DCAT['Dataset']

   def getOutputClass(self):
      return ns.DATAFAQS['EvaluatedDataset']

   def process(self, input, output):

      print 'processing ' + input.subject

      # Example output:
      #
      #<service-invocation-2>   # Do this one second.
      #  a prov:Activity;
      #  prov:wasAttributedTo <https://raw.github.com/nicholasdelrio/visko/master/rdf/ps2pdf.owl#ps2pdfService-as-sadi>;
      #  prov:wasInformedBy <service-invocation-1>;
      #.
      #<service-invocation-1>   # Do this one first
      #   a prov:Activity;
      #     prov:wasAttributedTo <https://raw.github.com/nicholasdelrio/visko/master/rdf/pdf-to-png.owl#pdf-to-png-as-sadi>; 
      #     prov:used <http://www.adobetutorialz.com/content_images/AdobeTechnologies/PostScript/manylines.ps>;
      #.
      #<https://raw.github.com/nicholasdelrio/visko/master/rdf/pdf-to-png.owl#pdf-to-png-as-sadi>        
      #  a datafaqs:SADIService, OWLS:Service, prov:Agent;
      #  .
      #<https://raw.github.com/nicholasdelrio/visko/master/rdf/ps2pdf.owl#ps2pdfService-as-sadi>
      #  a datafaqs:SADIService, OWLS:Service, prov:Agent;
      #.

      ####
      # Query a SPARQL endpoint
      store = Store(reader = 'sparql_protocol', endpoint = 'http://dbpedia.org/sparql')
      session = Session(store)
      session.enable_logging = False
      result = session.default_store.execute_sparql('select distinct ?type where {[] a ?type} limit 2')
      if result:
         for binding in result['results']['bindings']:
            type  = binding['type']['value']
            print type
      ####

      # Query the RDF graph POSTed: input.session.default_store.execute

      # Walk through all Things in the input graph (using SuRF):
      # Thing = input.session.get_class(ns.OWL['Thing'])
      # for person in Thing.all():

      if True:
         output.rdf_type.append(ns.DATAFAQS['Unsatisfactory'])
 
      if ns.DATAFAQS['Unsatisfactory'] not in output.rdf_type:
         output.rdf_type.append(ns.DATAFAQS['Satisfactory'])

      output.save()

# Used when Twistd invokes this service b/c it is sitting in a deployed directory.
resource = VisKoPlanner()

# Used when this service is manually invoked from the command line (for testing).
if __name__ == '__main__':
   print resource.name + ' running on port ' + str(resource.dev_port) + '. Invoke it with:'
   print 'curl -H "Content-Type: text/turtle" -d @my.ttl http://localhost:' + str(resource.dev_port) + '/' + resource.name
   sadi.publishTwistedService(resource, port=resource.dev_port)
