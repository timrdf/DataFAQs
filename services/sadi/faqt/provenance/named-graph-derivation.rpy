#3> <> prov:specializationOf <https://raw.github.com/timrdf/DataFAQs/master/services/sadi/faqt/provenance/named-graph-derivation.rpy>;
#3>    rdfs:seeAlso <https://github.com/timrdf/DataFAQs/wiki/FAqT-Service> .
#3>
#3> <http://sparql.tw.rpi.edu/services/datafaqs/faqt/provenance/named-graph-derivation>
#3>    a datafaqs:FAqTService .
#3> []
#3>    a prov:Activity;
#3>    prov:hadQualifiedAttribution [
#3>       a prov:Attribution;
#3>       prov:hadQualifiedEntity <http://sparql.tw.rpi.edu/services/datafaqs/faqt/provenance/named-graph-derivation>;
#3>       prov:adoptedPlan        <https://raw.github.com/timrdf/DataFAQs/master/services/sadi/faqt/provenance/named-graph-derivation.rpy>;
#3>    ];
#3> .
#3> <https://raw.github.com/timrdf/DataFAQs/master/services/sadi/faqt/provenance/named-graph-derivation.rpy>
#3>    foaf:homepage <https://github.com/timrdf/DataFAQs/blob/master/services/sadi/faqt/provenance/named-graph-derivation.rpy> .

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
ns.register(dcat='http://www.w3.org/ns/dcat#')
ns.register(sd='http://www.w3.org/ns/sparql-service-description#')
ns.register(prov='http://www.w3.org/ns/prov#')
ns.register(conversion='http://purl.org/twc/vocab/conversion/')
ns.register(datafaqs='http://purl.org/twc/vocab/datafaqs#')

# The Service itself
class NamedGraphDerivation(sadi.Service):

   # Service metadata.
   label                  = 'named-graph-derivation'
   serviceDescriptionText = 'Finds provenance assertions in the same triple store as a given sd:NamedGraph, to find what led to the RDF graph it provides.'
   comment                = 'see https://github.com/timrdf/csv2rdf4lod-automation/wiki/Named-graphs-that-know-where-they-came-from'
   serviceNameText        = 'named-graph-derivation' # Convention: Match 'name' below.
   name                   = 'named-graph-derivation' # This value determines the service URI relative to http://localhost:9090/
                                                     # Convention: Use the name of this file for this value.
   dev_port = 9120

   def __init__(self): 
      sadi.Service.__init__(self)

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

   # NOTE: This query should stay in sync with https://raw.github.com/timrdf/prov-lodspeakr/master/components/services/publishings/queries/pvloads.query
   sourcesQuery = '''
prefix dcterms:    <http://purl.org/dc/terms/>
prefix sd:         <http://www.w3.org/ns/sparql-service-description#>
prefix sioc:       <http://rdfs.org/sioc/ns#>
prefix skos:       <http://www.w3.org/2004/02/skos/core#>
prefix pmlj:       <http://inference-web.org/2.0/pml-justification.owl#>
prefix hartigprov: <http://purl.org/net/provenance/ns#>
prefix conversion: <http://purl.org/twc/vocab/conversion/>

select ?graphName ?user ?person ?when ?engineType ?rule ?firstGraph ?secondGraph
where {
   # e.g. graph <http://logd.tw.rpi.edu/source/lebot/dataset/golfers/version/2012-Mar-15>  {

   # TODO: should relax constraint that provenance be in its own named graph.
   graph <NAMED_GRAPH> {

      [] pmlj:hasConclusion  [ skos:broader [ sd:name ?graphName ] ]; # TODO: <{{lodspk.args.all|deurifier}}>
         pmlj:isConsequentOf ?infstep .
      filter( str(?graphName) = "NAMED_GRAPH" ) # TODO: shouldn't have to squash to string.

      optional { # Determine the two operands
         ?infstep
            pmlj:hasAntecedentList [
               rdf:first [ pmlj:hasConclusion ?firstGraph ];
                           rdf:rest           ?second;
            ]
      }
      optional {
         ?second rdf:first [ pmlj:hasConclusion ?secondGraph ]
      }

      optional { ?infstep dcterms:date             ?when       }
      optional { ?infstep pmlj:hasInferenceRule    ?rule       }

      optional { ?infstep hartigprov:involvedActor ?user       }
      optional { ?user    sioc:account_of          ?person     }

      optional { ?infstep pmlj:hasInferenceEngine  ?engine     }
      optional { ?engine  a                        ?engineType }
  }
} order by ?when
'''

   def process(self, input, output):

      print 'processing ' + input.subject
      VOIDGraph = output.session.get_class(ns.VOID['Graph'])

      for ng in input.sd_namedGraph:
         for gname in ng.sd_name:
            for service in input.is_sd_availableGraphDescriptions_of:
               print service.subject + ' GRAPH <' + gname + '> {}'
 
               loc = service.subject
               if service.sd_url:
                  loc = service.sd_url.first
               ####
               # Query a SPARQL endpoint
               store = Store(reader = 'sparql_protocol', endpoint = loc)
               session = Session(store)
               session.enable_logging = False
               result = session.default_store.execute_sparql(self.sourcesQuery.replace('NAMED_GRAPH',gname))
               if result:
                  for binding in result['results']['bindings']:
                     print
                     if 'firstGraph' in binding and 'secondGraph' in binding:
                        orig  = binding['firstGraph']['value']
                        print 'ORIG: ' + orig
                        print
                        file  = binding['secondGraph']['value']
                        print 'FILE: ' + file
                        g = VOIDGraph(file)
                        output.prov_wasDerivedFrom.append(g)
                        output.save()
                     elif 'firstGraph' in binding:
                        file = binding['firstGraph']['value']
                        print 'FILE: ' + file
                        g = VOIDGraph(file)
                        output.prov_wasDerivedFrom.append(g)
                        output.save()
               ####

      if True:
         output.rdf_type.append(ns.DATAFAQS['Unsatisfactory'])
 
      if ns.DATAFAQS['Unsatisfactory'] not in output.rdf_type:
         output.rdf_type.append(ns.DATAFAQS['Satisfactory'])

      output.save()

# Used when Twistd invokes this service b/c it is sitting in a deployed directory.
resource = NamedGraphDerivation()

# Used when this service is manually invoked from the command line (for testing).
if __name__ == '__main__':
   print resource.name + ' running on port ' + str(resource.dev_port) + '. Invoke it with:'
   print 'curl -H "Content-Type: text/turtle" -d @my.ttl http://localhost:' + str(resource.dev_port) + '/' + resource.name
   sadi.publishTwistedService(resource, port=resource.dev_port)
