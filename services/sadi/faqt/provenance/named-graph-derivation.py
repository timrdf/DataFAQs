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

   publishingsQuery = '''
#3> <> prov:specializationOf <https://raw.github.com/timrdf/prov-lodspeakr/master/components/services/publishings/queries/pvloads.query> .

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
   graph <{{lodspk.args.all|deurifier}}> {

      [] pmlj:hasConclusion  [ skos:broader [ sd:name ?graphName ] ]; # TODO: <{{lodspk.args.all|deurifier}}>
         pmlj:isConsequentOf ?infstep .
      filter( str(?graphName) = "{{lodspk.args.all|deurifier}}" ) # TODO: shouldn't have to squash to string.

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

   conversionQuery = '''
#3> <> prov:specializationOf <https://raw.github.com/timrdf/prov-lodspeakr/master/components/services/conversions/queries/dumps.query> .

prefix dcterms:    <http://purl.org/dc/terms/>
prefix sd:         <http://www.w3.org/ns/sparql-service-description#>
prefix sioc:       <http://rdfs.org/sioc/ns#>
prefix skos:       <http://www.w3.org/2004/02/skos/core#>
prefix doap:       <http://usefulinc.com/ns/doap#>
prefix pmlj:       <http://inference-web.org/2.0/pml-justification.owl#>
prefix pmlx:       <http://inference-web.org/2.1exper/pml-provenance.owl#>
prefix hartigprov: <http://purl.org/net/provenance/ns#>
prefix conversion: <http://purl.org/twc/vocab/conversion/>

select distinct ?dump ?dataset ?engine ?engineL ?revision ?input ?params

where {
  graph <{{lodspk.args.all|deurifier}}> {

    ?dataset void:dataDump ?dump .
    optional { ?dataset dcterms:modified ?modified }

    [] pmlj:hasConclusion  ?dump;
       pmlj:isConsequentOf [ 
          pmlj:hasInferenceEngine ?engine;
          pmlj:hasAntecedentList [ 
             rdf:first [             pmlj:hasConclusion ?input    ];
             rdf:rest  [ rdf:first [ pmlj:hasConclusion ?params ] ];
          ];
          pmlx:hasAntecedentRole [
             pmlx:hasAntecedent ?input;
             pmlx:hasRole <http://inference-web.org/registry/ROLE/Input.owl#Input>
          ];
          pmlx:hasAntecedentRole [
             pmlx:hasAntecedent ?params;
             pmlx:hasRole <http://inference-web.org/registry/ROLE/Parameters.owl#Parameters>
          ];
       ] .

    ?engine
       dcterms:identifier ?engineL;
       doap:revision      ?revision .
  }
}
'''
   xls2csvQuery = '''
#3> <> prov:specializationOf <https://raw.github.com/timrdf/prov-lodspeakr/master/components/services/preparations/queries/xls2csv.query> .

prefix conversion: <http://purl.org/twc/vocab/conversion/>
prefix pmlp:       <http://inference-web.org/2.0/pml-provenance.owl#>
prefix pmlj:       <http://inference-web.org/2.0/pml-justification.owl#>
prefix httpget:    <http://inference-web.org/registry/MPR/HTTP_1_1_GET.owl#> 
prefix hartigprov: <http://purl.org/net/provenance/ns#>
prefix nfo:        <http://www.semanticdesktop.org/ontologies/nfo/#>

select distinct ?time ?source ?rule ?engine ?conclusion ?actor ?hashAlgorithm ?hashValue
where {
   # e.g. graph <http://logd.tw.rpi.edu/source/lebot/dataset/golfers/version/2012-Mar-15> {
   graph <{{lodspk.args.all|deurifier}}> {
      ?nodeset
         pmlj:isConsequentOf ?step;
         pmlj:hasConclusion ?conclusion
      .
      ?conclusion
         pmlp:hasModificationDateTime ?time;
         nfo:hasHash [
            nfo:hashAlgorithm ?hashAlgorithm;
            nfo:hashValue     ?hashValue
         ]
      .
      ?step
         a pmlj:InferenceStep;
         pmlj:hasInferenceEngine  ?engine;
         pmlj:hasInferenceRule   conversion:csv2rdf4lod_xls2csv_sh_Method;
         pmlj:hasInferenceRule    ?rule;
         pmlj:hasAntecedentList   ?antList;
         hartigprov:involvedActor ?actor
      .
      ?antList 
         rdf:first ?antFirst
      .
      ?antFirst
         pmlj:hasConclusion ?source
      .
   }
} order by ?time
'''

   unzipQuery = '''
#3> <> prov:specializationOf <https://raw.github.com/timrdf/prov-lodspeakr/master/components/services/preparations/queries/unzip.query> .

prefix conversion: <http://purl.org/twc/vocab/conversion/>
prefix pmlp:       <http://inference-web.org/2.0/pml-provenance.owl#>
prefix pmlj:       <http://inference-web.org/2.0/pml-justification.owl#>
prefix httpget:    <http://inference-web.org/registry/MPR/HTTP_1_1_GET.owl#> 
prefix conv:       <http://purl.org/twc/vocab/conversion/> 
prefix hartigprov: <http://purl.org/net/provenance/ns#>
prefix nfo:        <http://www.semanticdesktop.org/ontologies/nfo/#>

select distinct ?engine ?source ?time ?actor ?conclusion ?rule ?alg ?hashValue
where {
   # e.g. graph <http://logd.tw.rpi.edu/source/lebot/dataset/golfers/version/2012-Mar-15> {
   graph <{{lodspk.args.all|deurifier}}> {
      []
         pmlj:isConsequentOf ?step;
         pmlj:hasConclusion  ?conclusion.
      ?step
         a pmlj:InferenceStep;
         pmlj:hasInferenceEngine  ?engine;
         pmlj:hasInferenceRule    conv:spaceless_unzip; #ASSUME we know the inference rule or iterate over the set of rules supported
         pmlj:hasInferenceRule    ?rule;
         pmlj:hasSourceUsage      ?sUsage;
         hartigprov:involvedActor ?actor.
      ?sUsage 
         pmlp:hasSource        ?source;
         pmlp:hasUsageDateTime ?time.
      ?conclusion
         nfo:hasHash ?hash.
      ?hash
         nfo:hashAlgorithm ?alg;
         nfo:hashValue ?hashValue.
  }
} order by desc(?time)
'''

   retrievalQuery = '''
#3> <> prov:specializationOf <https://raw.github.com/timrdf/prov-lodspeakr/master/components/services/retrievals/queries/pcurls.query>

prefix conversion: <http://purl.org/twc/vocab/conversion/>
prefix pmlp:       <http://inference-web.org/2.0/pml-provenance.owl#>
prefix pmlj:       <http://inference-web.org/2.0/pml-justification.owl#>
prefix httpget:    <http://inference-web.org/registry/MPR/HTTP_1_1_GET.owl#> 
prefix hartigprov: <http://purl.org/net/provenance/ns#>
prefix irw:        <http://www.ontologydesignpatterns.org/ont/web/irw.owl#> 
prefix nfo:        <http://www.semanticdesktop.org/ontologies/nfo/#>

select distinct ?engine ?source ?time ?actor ?conclusion ?rule ?fromUrl ?alg ?hashValue 
where {
   # e.g. graph <http://logd.tw.rpi.edu/source/lebot/dataset/golfers/version/2012-Mar-15> {
   graph <{{lodspk.args.all|deurifier}}> {
      [] 
         pmlj:isConsequentOf ?step;
         pmlj:hasConclusion  ?conclusion.
      ?step
         a pmlj:InferenceStep;
         pmlj:hasInferenceEngine  ?engine;
         pmlj:hasInferenceRule   httpget:HTTP_1_1_GET; # ASSUME we know the rule or we can iterate over the set of rules supported
         pmlj:hasInferenceRule    ?rule;
         pmlj:hasSourceUsage      ?sUsage;
         hartigprov:involvedActor ?actor.
      ?sUsage 
         pmlp:hasSource        ?source;
         pmlp:hasUsageDateTime ?time.
      ?conclusion
         nfo:hasHash ?hash.
      ?hash
         nfo:hashAlgorithm ?alg;
         nfo:hashValue     ?hashValue.
      optional {
         ?fromUrl irw:redirectsTo ?source.
      }
  }
  #assume know the version of the dataset
  #filter regex(?conclusion, "/version/2012-Mar-15/source") 
} order by ?time
'''

   def process(self, input, output):

      print 'processing ' + input.subject

      VOIDGraph  = output.session.get_class(ns.VOID['Graph'])
      Service    = output.session.get_class(ns.SD['Service'])
      NamedGraph = output.session.get_class(ns.SD['NamedGraph'])
      Document   = output.session.get_class(ns.FOAF['Document'])
      Agent      = output.session.get_class(ns.PROV['Agent'])

      output.rdf_type.append(ns.SD['GraphCollection'])
      for ng in input.sd_namedGraph:
         ngR = NamedGraph(ng.subject)
         output.sd_namedGraph.append(ngR)
         for gname in ng.sd_name:
            ngR.sd_name.append(gname)
            ngR.save()
            for service in input.is_sd_availableGraphs_of:
               print service.subject + ' GRAPH <' + gname + '> {}'
               serviceR = Service(service.subject)
               serviceR.sd_availableGraphs.append(output)
               loc = service.subject
               if service.sd_endpoint:
                  loc = service.sd_endpoint.first
               serviceR.sd_endpoint.append(NamedGraph(loc))
               serviceR.save() 
               ####
               # Query a SPARQL endpoint
               store = Store(reader = 'sparql_protocol', endpoint = loc)
               session = Session(store)
               session.enable_logging = False
               result = session.default_store.execute_sparql(self.publishingsQuery.replace('{{lodspk.args.all|deurifier}}',gname))
               if result:
                  for binding in result['results']['bindings']:
                     print
                     dump = False
                     if 'firstGraph' in binding and 'secondGraph' in binding:
                        orig  = binding['firstGraph']['value']
                        #print 'ORIG: ' + orig
                        #print
                        dump  = binding['secondGraph']['value']
                     elif 'firstGraph' in binding:
                        dump = binding['firstGraph']['value']

                     if dump != False:
                        print 'published: ' + dump
                        dumpR = VOIDGraph(dump)
                        ngR.prov_wasDerivedFrom.append(dumpR)
                        ngR.save()

                        result2 = session.default_store.execute_sparql(self.conversionQuery.replace('{{lodspk.args.all|deurifier}}',gname)
                                                                                           .replace('distinct ?dump','distinct')
                                                                                           .replace('?dump','<'+dump+'>'))
                        if result2:
                           for binding2 in result2['results']['bindings']:
                              if 'input' in binding2:
                                 csv = binding2['input']['value']
                                 csvR = Document(csv)
                                 dumpR.prov_wasDerivedFrom.append(csvR)
                                 dumpR.save()
                                 print 'converted: ' + csv
                                 print

                                 result3 = session.default_store.execute_sparql(self.xls2csvQuery.replace('{{lodspk.args.all|deurifier}}',gname)
                                                                                                 .replace('?conclusion ?actor','?actor')
                                                                                                 .replace('?conclusion','<'+csv+'>'))
                                 for binding3 in result3['results']['bindings']:
                                    if 'source' in binding3:
                                       xls = binding3['source']['value']
                                       print 'xls: ' + xls
                                       xlsR = Document(xls)
                                       csvR.prov_wasDerivedFrom.append(xlsR)
                                       csvR.save()
                                       print

                                       #print self.unzipQuery.replace('{{lodspk.args.all|deurifier}}',gname) .replace('?conclusion ?rule','?rule') .replace('?conclusion','<'+xls+'>')
                                       result4 = session.default_store.execute_sparql(self.unzipQuery.replace('{{lodspk.args.all|deurifier}}',gname)
                                                                                                     .replace('?conclusion ?rule','?rule')
                                                                                                     .replace('?conclusion','<'+xls+'>'))
                                       if result4:
                                          for binding4 in result4['results']['bindings']:
                                             if 'source' in binding4:
                                                zip = binding4['source']['value']
                                                zipR = Document(zip)
                                                xlsR.prov_wasDerivedFrom.append(zipR)
                                                xlsR.save()
                                                print 'zip: ' + zip
                                                print
                                                #print self.retrievalQuery.replace('{{lodspk.args.all|deurifier}}',gname) .replace('?conclusion ?rule','?rule') .replace('?conclusion','<'+zip+'>')
                                                result5 = session.default_store.execute_sparql(self.retrievalQuery.replace('{{lodspk.args.all|deurifier}}',gname)
                                                                                                              .replace('?conclusion ?rule','?rule')
                                                                                                              .replace('?conclusion','<'+zip+'>'))
                                                if result5:
                                                   for binding5 in result5['results']['bindings']:
                                                      if 'source' in binding5:
                                                         source = binding5['source']['value']
                                                         print 'source: ' + source
                                                         sourceR = Document(source)
                                                         zipR.prov_alternateOf.append(sourceR)
                                                         zipR.prov_wasDerivedFrom.append(sourceR)
                                                         agent = Agent('http://'+urllib2.Request(url=source).get_host())
                                                         agent.save()
                                                         sourceR.prov_wasAttributedTo.append(agent)
                                                         ngR.prov_wasAttributedTo.append(agent)
                                                         ngR.save()
                                                         xlsR.save()
                                                         zipR.save()
                                                         output.rdf_type.append(ns.DATAFAQS['Satisfactory'])
                                                         output.save()
                                                         if 'fromUrl' in binding5:
                                                            orig = binding5['fromUrl']['value']
                                                            print 'orig: ' + orig
                                                            origR = Document(orig)
                                                            agent = Agent('http://'+urllib2.Request(url=orig).get_host())
                                                            agent.save()
                                                            origR.prov_wasAttributedTo.append(agent)
                                                            sourceR.prov_alternateOf.append(origR)
                                                            origR.save()
                                                            sourceR.save()
                                                            ngR.prov_wasAttributedTo.append(agent)
                                                            ngR.save()
               ####

 
      if ns.DATAFAQS['Satisfactory'] not in output.rdf_type:
         output.rdf_type.append(ns.DATAFAQS['Unsatisfactory'])

      output.save()

# Used when Twistd invokes this service b/c it is sitting in a deployed directory.
resource = NamedGraphDerivation()

# Used when this service is manually invoked from the command line (for testing).
if __name__ == '__main__':
   print resource.name + ' running on port ' + str(resource.dev_port) + '. Invoke it with:'
   print 'curl -H "Content-Type: text/turtle" -d @my.ttl http://localhost:' + str(resource.dev_port) + '/' + resource.name
   sadi.publishTwistedService(resource, port=resource.dev_port)
