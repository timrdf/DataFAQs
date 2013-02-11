#3> <> prov:specializationOf <https://github.com/timrdf/DataFAQs/blob/master/services/sadi/faqt/vocabulary/uses/void.py>;
#3>    prov:wasDerivedFrom   <https://github.com/timrdf/DataFAQs/blob/master/services/sadi/faqt/vocabulary/uses/dcat.py>;
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

import xml.dom

# These are the namespaces we are using beyond those already available
# (see http://packages.python.org/SuRF/modules/namespace.html#registered-general-purpose-namespaces)
ns.register(moat='http://moat-project.org/ns#')
ns.register(ov='http://open.vocab.org/terms/')
ns.register(void='http://rdfs.org/ns/void#')
ns.register(dcat='http://www.w3.org/ns/dcat#')
ns.register(sd='http://www.w3.org/ns/sparql-service-description#')
ns.register(conversion='http://purl.org/twc/vocab/conversion/')
ns.register(datafaqs='http://purl.org/twc/vocab/datafaqs#')
ns.register(sio='http://semanticscience.org/resource/')

# The Service itself
class UsesPROV(faqt.Service):

   # Service metadata.
   label                  = 'void'
   serviceDescriptionText = 'Counts the occurrence of the PROV-O predicates and classes in a dcat:Dataset named graph.'
   comment                = ''
   serviceNameText        = 'void' # Convention: Match 'name' below.
   name                   = 'void' # This value determines the service URI relative to http://localhost:9090/
                                   # Convention: Use the name of this file for this value.
   dev_port = 9238

   probes = 'http://rdfs.org/ns/void#'

   predicates = [
      'http://rdfs.org/ns/void#feature',
      'http://rdfs.org/ns/void#subset',
      'http://rdfs.org/ns/void#target',
      'http://rdfs.org/ns/void#sparqlEndpoint',
      'http://rdfs.org/ns/void#linkPredicate',
      'http://rdfs.org/ns/void#exampleResource',
      'http://rdfs.org/ns/void#vocabulary',
      'http://rdfs.org/ns/void#subjectsTarget',
      'http://rdfs.org/ns/void#objectsTarget',
      'http://rdfs.org/ns/void#dataDump',
      'http://rdfs.org/ns/void#uriLookupEndpoint',
      'http://rdfs.org/ns/void#uriRegexPattern',
      'http://rdfs.org/ns/void#class',
      'http://rdfs.org/ns/void#classes',
      'http://rdfs.org/ns/void#classPartition',
      'http://rdfs.org/ns/void#distinctObjects',
      'http://rdfs.org/ns/void#distinctSubjects',
      'http://rdfs.org/ns/void#documents',
      'http://rdfs.org/ns/void#entities',
      'http://rdfs.org/ns/void#inDataset',
      'http://rdfs.org/ns/void#openSearchDescription',
      'http://rdfs.org/ns/void#properties',
      'http://rdfs.org/ns/void#property',
      'http://rdfs.org/ns/void#propertyPartition',
      'http://rdfs.org/ns/void#rootResource',
      'http://rdfs.org/ns/void#triples',
      'http://rdfs.org/ns/void#uriSpace'
   ]

   classes = [
      'http://rdfs.org/ns/void#Dataset',
      'http://rdfs.org/ns/void#Linkset',
      'http://rdfs.org/ns/void#TechnicalFeature',
      'http://rdfs.org/ns/void#DatasetDescription'
   ]

   def __init__(self):
      # DATAFAQS_PROVENANCE_CODE_RAW_BASE                   +  servicePath  +  '/'  + self.serviceNameText
      # DATAFAQS_PROVENANCE_CODE_PAGE_BASE                  +  servicePath  +  '/'  + self.serviceNameText
      #
      # ^^ The source code location
      #    aligns with the deployment location \/
      #
      #                 DATAFAQS_BASE_URI  +  '/datafaqs/'  +  servicePath  +  '/'  + self.serviceNameText
      faqt.Service.__init__(self, servicePath = 'services/sadi/faqt/vocabulary/uses')
                                                                 # Use: pwd | sed 's/^.*services/services/'
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

      endpoint = False

      # TODO: add    dcat:distribution [ a sd:NamedGraph; sd:name ; prov:hadLocation
      # like https://github.com/timrdf/DataFAQs/blob/master/services/sadi/ckan/add-metadata-materials/sample-inputs/arrayexpress-e-afmx-1.ttl#L49

      if len(input.void_sparqlEndpoint) > 0:
         # <http://datahub.io/dataset/dbpedia> 
         #    void:sparqlEndpoint <http://dbpedia.org/sparql> .
         endpoint = self.surfSubject(input.void_sparqlEndpoint.first)
         print 'void:sparqlEndpoint: ' + endpoint
      else:
         # <http://datahub.io/dataset/dbpedia> 
         #    dcat:distribution [
         #       dct:format [
         #          a dct:IMT;
         #          rdf:value  "api/sparql";
         #          rdfs:label "api/sparql"
         #       ];
         #      a dcat:Distribution ;
         #      dcat:accessURL <http://dbpedia.org/sparql>
         #   ]; .

         query = select("?url").where((input.subject, ns.DCAT['distribution'], "?distro"),
                                      ("?distro",     ns.DCTERMS['format'],    "?format"),
                                      ("?format",     ns.RDF['value'],         rdflib.Literal('api/sparql')),
                                      ("?distro",     ns.DCAT['accessURL'],    "?url"))
         for bindings in input.session.default_store.execute(query):
            #print 'creator: ' + bindings[0] + ' ' + bindings[1]
            endpoint = self.surfSubject(bindings[0])
            print 'dcat:distribution dcat:accessURL: ' + endpoint

      if endpoint is False:
         print 'WARNING: could not find SPARQL endpoint to query; skipping ' + input.subject
         output.rdf_type.append(ns.DATAFAQS['Unsatisfactory'])
         return
         
      ng='http://purl.org/twc/health/source/healthdata-tw-rpi-edu/dataset/cr-full-dump/version/latest'

      Class     = output.session.get_class(ns.RDFS['Class'])
      Predicate = output.session.get_class(ns.RDF['Property'])

      ####
      # Query a SPARQL endpoint
      store = Store(reader = 'sparql_protocol', endpoint = endpoint)
      session = Session(store)
      session.enable_logging = False
      for predicate in self.predicates:
         results = session.default_store.execute_sparql( # TODO: handle optional named graph.
            '''
            select (count(*) as ?count)
            where {
                [] <'''+predicate+'''> []
            }'''
         )
              #graph <'''+ng+'''> {
         count = False
         if isinstance(results, xml.dom.minidom.Document):
            for result in results.getElementsByTagName('result'):
               for binding in result.getElementsByTagName('binding'):
                  for value in result.getElementsByTagName('literal'):
                     count = int(value.firstChild.data)
                     predR = output.session.get_resource(predicate, Predicate)
                     predR.sio_count = count
                     predR.save()
                     output.rdf_type.append(ns.DATAFAQS['Satisfactory'])
                     print str(count) + ' ' + predicate
         elif results:
            print results
            for binding in results['results']['bindings']:
               count = binding['count']['value']
               print count
      for classU in self.classes:
         results = session.default_store.execute_sparql( # TODO: handle optional named graph.
            '''
            select (count(*) as ?count)
            where {
                [] a <'''+classU+'''>
            }'''
         )
              #graph <'''+ng+'''> {
         count = False
         if isinstance(results, xml.dom.minidom.Document):
            for result in results.getElementsByTagName('result'):
               for binding in result.getElementsByTagName('binding'):
                  for value in result.getElementsByTagName('literal'):
                     count = int(value.firstChild.data)
                     classR = output.session.get_resource(classU, Class)
                     classR.sio_count = count
                     classR.save()
                     output.rdf_type.append(ns.DATAFAQS['Satisfactory'])
                     print str(count) + ' ' + classU
         elif results:
            print results
            for binding in results['results']['bindings']:
               count = binding['count']['value']
               print count
      ####

      # Query the RDF graph POSTed: input.session.default_store.execute

      # Walk through all Things in the input graph (using SuRF):
      # Thing = input.session.get_class(ns.OWL['Thing'])
      # for person in Thing.all():

      # Create a class in the output graph:
      # Document = output.session.get_class(ns.FOAF['Document'])

      if ns.DATAFAQS['Satisfactory'] not in output.rdf_type:
         output.rdf_type.append(ns.DATAFAQS['Unsatisfactory'])
      else:
         Ontology = output.session.get_class(ns.OWL['Ontology'])
         output.void_vocabulary.append(Ontology(self.probes))

      output.save()

# Used when Twistd invokes this service b/c it is sitting in a deployed directory.
resource = UsesPROV()

# Used when this service is manually invoked from the command line (for testing).
if __name__ == '__main__':
   print resource.name + ' running on port ' + str(resource.dev_port) + '. Invoke it with:'
   print 'curl -H "Content-Type: text/turtle" -d @my.ttl http://localhost:' + str(resource.dev_port) + '/' + resource.name
   sadi.publishTwistedService(resource, port=resource.dev_port)
