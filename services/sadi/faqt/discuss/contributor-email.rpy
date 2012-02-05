# 
# See https://github.com/timrdf/DataFAQs/wiki/FAqT-Service
#
#3> <> prov:specializationOf <#TEMPLATE/path/to/public/source-code.rpy> .
#
#3> <#TEMPLATE/path/to/where/source-code.rpy/is/deployed/for/invocation>
#3>    a datafaqs:FAqTService .
#3> []
#3>   a prov:Activity;
#3>   prov:hadQualifiedAttribution [
#3>      a prov:Attribution;
#3>      prov:hadQualifiedEntity <#TEMPLATE/path/to/where/source-code.rpy/is/deployed/for/invocation>;
#3>      prov:adoptedPlan        <#TEMPLATE/path/to/public/source-code.rpy>;
#3>   ];
#3> .

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
ns.register(conversion='http://purl.org/twc/vocab/conversion/')
ns.register(datafaqs='http://purl.org/twc/vocab/datafaqs#')
ns.register(oo='http://purl.org/openorg/')

# The Service itself
class ContributorEmail(sadi.Service):

   # Service metadata.
   label                  = 'contributor-email'
   serviceDescriptionText = 'Passes if the dcat:Dataset has a dcterms:contributor with an foaf:mbox.'
   comment                = 'It it important that datasets have a person to contact if consumers have questions or concerns.'
   serviceNameText        = 'contributor-email' # Convention: Match 'name' below.
   name                   = 'contributor-email' # This value determines the service URI relative to http://localhost:9090/
                                            # Convention: Use the name of this file for this value.
   dev_port = 9111

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

   def process(self, input, output):

      print 'processing ' + input.subject

      ## Check for dcterms:contributor foaf:mbox 
      # <http://thedatahub.org/dataset/aemet>
      #    dc:contributor [
      #       foaf:mbox <mailto:dgarijov@gmail.com>;
      #       foaf:name "Ontology Engineering Group..."
      prefixes = 'prefix foaf: <http://xmlns.com/foaf/0.1/> prefix dcterms: <http://purl.org/dc/terms/> '
      result = input.session.default_store.execute_sparql(prefixes+
               'select distinct ?email where {<'+input.subject+'> dcterms:contributor [ foaf:mbox ?email ]}')
      if result:
         Agent = output.session.get_class(ns.FOAF["Agent"])
         for binding in result['results']['bindings']:
            ag = Agent()
            email = binding['email']['value']
            ag.foaf_mbox = email
            ag.save()
            output.dcterms_contributor = ag
            output.rdf_type.append(ns.DATAFAQS['Satisfactory'])

      ## Check for oo:corrections
      # <http://thedatahub.org/dataset/aemet>
      #       oo:corrections <mailto:dgarijov@gmail.com>;
      prefixes = 'prefix oo: <http://purl.org/openorg/> '
      result = input.session.default_store.execute_sparql(prefixes+
               'select distinct ?email where {<'+input.subject+'> oo:corrections ?email}')
      if result:
         Agent = output.session.get_class(ns.FOAF["Agent"])
         for binding in result['results']['bindings']:
            email = binding['email']['value']
            output.oo_corrections = email 
            output.rdf_type.append(ns.DATAFAQS['Satisfactory'])

      if ns.DATAFAQS['Satisfactory'] not in output.rdf_type:
         output.rdf_type.append(ns.DATAFAQS['Unsatisfactory'])

      output.save()

# Used when Twistd invokes this service b/c it is sitting in a deployed directory.
resource = ContributorEmail()

# Used when this service is manually invoked from the command line (for testing).
if __name__ == '__main__':
   print resource.name + ' running on port ' + str(resource.dev_port) + '. Invoke it with:'
   print 'curl -H "Content-Type: text/turtle" -d @my.ttl http://localhost:' + str(resource.dev_port) + '/' + resource.name
   sadi.publishTwistedService(resource, port=resource.dev_port)
