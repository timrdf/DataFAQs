# 
# See https://github.com/timrdf/DataFAQs/wiki/FAqT-Service
#

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
import re
import exceptions

# These are the namespaces we are using beyond those already available
# (see http://packages.python.org/SuRF/modules/namespace.html#registered-general-purpose-namespaces)
ns.register(moat='http://moat-project.org/ns#')
ns.register(ov='http://open.vocab.org/terms/')
ns.register(void='http://rdfs.org/ns/void#')
ns.register(sd='http://www.w3.org/ns/sparql-service-description#')
ns.register(conversion='http://purl.org/twc/vocab/conversion/')
ns.register(datafaqs='http://purl.org/twc/vocab/datafaqs#')

# The Service itself
class SDNamedGraphs(sadi.Service):

   # Service metadata.
   label                  = 'named-graphs'
   serviceDescriptionText = 'Describes the given sd:Service with the sd:NamedGraphs it offers.'
   comment                = 'Provides global URIs for the named graphs that are contextualized by the sd:Service.'
   serviceNameText        = 'named-graphs' # Convention: Match 'name' below.
   name                   = 'named-graphs' # This value determines the service URI relative to http://localhost:9090/
                                           # Convention: Use the name of this file for this value.
   dev_port = 9106

   query = 'select distinct ?graph where { graph ?graph { [] a [] } }'

   def __init__(self): 
      sadi.Service.__init__(self)
      print self.serviceDescription

   def getOrganization(self):
      result                      = self.Organization()
      result.mygrid_authoritative = True
      result.protegedc_creator    = 'lebot@rpi.edu'
      result.save()
      return result

   def getInputClass(self):
      return ns.SD['Service']

   def getOutputClass(self):
      return ns.DATAFAQS['Evaluated']

   def process(self, input, output):

      print 'processing ' + input.subject

      try:
         store = Store(reader = 'sparql_protocol', endpoint = input.subject)
         session = Session(store)
         session.enable_logging = False
         result = session.default_store.execute_sparql(self.query) # TODO: fails if not valid response.

         if result['results']:
            print '  sd:Service responded with results'
            self.describe_result(output, input.subject, result)
         elif input.sd_url:
            print '  falling back to sd:url ' + input.sd_url.first
            store = Store(reader = 'sparql_protocol', endpoint = input.sd_url.first)
            session = Session(store)
            session.enable_logging = False
            result = session.default_store.execute_sparql(query)
            if result:
               self.describe_result(output, input.sd_url.first, result)
         else:
            output.rdf_type.append(ns.DATAFAQS['Unsatisfactory'])

      except:
         print "Unexpected error:", sys.exc_info()[0]
         output.rdf_type.append(ns.DATAFAQS['Unsatisfactory'])
         output.datafaqs_evaluation_error = sys.exc_info()[0]

      finally:
         if ns.DATAFAQS['Unsatisfactory'] not in output.rdf_type:
            output.rdf_type.append(ns.DATAFAQS['Satisfactory'])
         output.save()

   def describe_result(self, output, endpoint, result):

      Thing           = output.session.get_class(ns.OWL['Thing'])
      GraphCollection = output.session.get_class(ns.SD['GraphCollection'])
      NamedGraph      = output.session.get_class(ns.SD['NamedGraph'])

      dataset = GraphCollection()
      output.sd_url.append(endpoint)
      output.sd_availableGraphDescriptions = dataset
      output.save()

      count = 0
      for binding in result['results']['bindings']:
         count += 1
         print str(count) + ' named graphs'
         gname = binding['graph']['value']
         namedgraph = NamedGraph()
         ng = self.name_sparql_endpoints_named_graph(endpoint, gname)
         #print '|' + ng + '|'
         namedgraph = NamedGraph(ng)
         namedgraph.sd_name = Thing(gname)
         namedgraph.save()
         dataset.sd_namedGraph.append(namedgraph)
      if ns.DATAFAQS['Unsatisfactory'] not in output.rdf_type:
         output.rdf_type.append(ns.DATAFAQS['Satisfactory'])
      dataset.save() # Moving save() out of loop saves a lot of time.
      output.save()
 
   def name_sparql_endpoints_named_graph(self, endpoint, named_graph):
      # XSLT implementation: sparql-service-descriptions.xsl
      query = '''PREFIX sd: <http://www.w3.org/ns/sparql-service-description#> CONSTRUCT { ?endpoints_named_graph ?p ?o } WHERE { GRAPH <'''+named_graph+'''> { [] sd:url <'''+endpoint+'''>; sd:defaultDatasetDescription [ sd:namedGraph ?endpoints_named_graph ] . ?endpoints_named_graph sd:name <'''+named_graph+'''>; ?p ?o . } }'''
      return endpoint + '?' + urllib.urlencode({'query': query})

   def annotateServiceDescription(self, desc):

      desc.rdfs_comment.append('https://github.com/timrdf/DataFAQs/wiki')

      Thing = desc.session.get_class(ns.OWL['Thing'])

      wiki = Thing('https://github.com/timrdf/DataFAQs/wiki')
      desc.rdfs_seeAlso.append(wiki)

      #code = Thing('https://github.com/timrdf/DataFAQs/blob/master/services/sadi/faqt/sparql-service-description/named-graphs.rpy')
      #desc.rdfs_seeAlso.append(code)
      wiki.save()
      #code.save()
      desc.save()

      # Desired description:
      #
      #  mygrid:hasUnitTest [ 
      #     a mygrid:testCase ;
      #     mygrid:exampleInput  test:hello-param-input.rdf ;
      #     mygrid:exampleOutput test:hello-param-output.rdf
      #  ] 

#         unitTests = [ ['https://raw.github.com/timrdf/DataFAQs/master/services/sadi/faqt/sparql-service-description/named-graphs-materials/sample-inputs/mondeca.ttl',''],
#                       ['https://raw.github.com/timrdf/DataFAQs/master/services/sadi/faqt/sparql-service-description/named-graphs-materials/sample-inputs/logd.ttl',''] ]
#         self.Thing    = self.getClass(ns.OWL['Thing'])
#         self.TestCase = self.getClass(ns.MYGRID['testCase'])
#         for io in unitTests:
#            print io[0]
            #testCase = self.TestCase()
            #testCase.mygrid_exampleInput  = self.Thing(io[0])
            #if len(io[1]):
            #   testCase.mygrid_exampleOutput = self.Thing(io[1])
            #testCase.save()
            #desc.mygrid_hasUnitTest.append(testCase)

# Used when Twistd invokes this service b/c it is sitting in a deployed directory.
resource = SDNamedGraphs()

# Used when this service is manually invoked from the command line (for testing).
if __name__ == '__main__':
   print 'curl -H "Content-Type: text/turtle" -d @my.ttl http://localhost:' + str(resource.dev_port) + '/' + resource.name
   sadi.publishTwistedService(resource, port=resource.dev_port)
