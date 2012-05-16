#3> <> prov:specializationOf <#TEMPLATE/path/to/public/source-code.rpy>;
#3>    rdfs:seeAlso <https://github.com/timrdf/DataFAQs/wiki/FAqT-Service> .
#3>
#3> <#TEMPLATE/path/to/where/source-code.rpy/is/deployed/for/invocation>
#3>    a datafaqs:FAqTService .
#3> []
#3>    a prov:Activity;
#3>    prov:hadQualifiedAttribution [
#3>       a prov:Attribution;
#3>       prov:hadQualifiedEntity <#TEMPLATE/path/to/where/source-code.rpy/is/deployed/for/invocation>;
#3>       prov:adoptedPlan        <#TEMPLATE/path/to/public/source-code.rpy>;
#3>    ];
#3> .
#3> <#TEMPLATE/path/to/public/source-code.rpy>
#3>    foaf:homepage <#TEMPLATE/path/to/public/HOMEPAGE-FOR/source-code.rpy> .

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
ns.register(prov='http://www.w3.org/ns/prov#')
ns.register(asn='dvcs.w3.org/hg/prov/raw-file/default/model/working-copy/prov-asn.html#')

# The Service itself
class RDF2ASN(sadi.Service):

   # Service metadata.
   label                  = 'rdf2asn'
   serviceDescriptionText = 'Produces PROV-DM ASN expressions from RDF encodings of the same conceptual model.'
   comment                = ''
   serviceNameText        = 'rdf2asn' # Convention: Match 'name' below.
   name                   = 'rdf2asn' # This value determines the service URI relative to http://localhost:9090/
                                      # Convention: Use the name of this file for this value.
   dev_port = 9117

   def __init__(self): 
      sadi.Service.__init__(self)

   def getOrganization(self):
      result                      = self.Organization()
      result.mygrid_authoritative = True
      result.protegedc_creator    = 'lebot@rpi.edu'
      result.save()
      return result

   def getInputClass(self):
      return ns.OWL['Thing']

   def getOutputClass(self):
      return ns.ASN['Expression']

   def processGraph(self,content, type):

      inputStore   = Store(reader="rdflib", writer="rdflib", rdflib_store='IOMemory')
      inputSession = Session(inputStore)
      self.deserialize(inputStore.reader.graph, content, type)

      outputStore   = Store(reader="rdflib", writer="rdflib", rdflib_store='IOMemory')
      outputSession = Session(outputStore)
      OutputClass = outputSession.get_class(self.getOutputClass())


      Entity   = inputSession.get_class(ns.PROV['Entity'])
      Activity = inputSession.get_class(ns.PROV['Activity'])
      Agent    = inputSession.get_class(ns.PROV['Agent'])

      Expression = outputSession.get_class(ns.ASN['Expression'])

      for entity in Entity.all():
         print entity.prov_identifier.first
         entityO = outputSession.get_resource(entity.subject, ns.PROV['Entity'])
         expression = Expression()
         expression.rdf_value = 'entity(' + entity.prov_identifier.first + ')'
         expression.save()
         entityO.dcterms_isReferencedBy = expression
         entityO.save()

      for activity in Activity.all():
         print activity.prov_identifier.first
         activityO = outputSession.get_resource(activity.subject, ns.PROV['Activity'])
         expression = Expression()
         expression.rdf_value = 'activity(' + activity.prov_identifier.first + ')'
         expression.save()
         activityO.dcterms_isReferencedBy = expression
         activityO.save()

      return outputStore.reader.graph

#   def process(self, input, output):
#
#      print 'processing ' + input.subject
#
#      ####
#      # Query a SPARQL endpoint
#      store = Store(reader = 'sparql_protocol', endpoint = 'http://dbpedia.org/sparql')
#      session = Session(store)
#      session.enable_logging = False
#      result = session.default_store.execute_sparql('select distinct ?type where {[] a ?type} limit 2')
#      if result:
#         for binding in result['results']['bindings']:
#            type  = binding['type']['value']
#            print type
#      ####
#
#      if True:
#         output.rdf_type.append(ns.DATAFAQS['Unsatisfactory'])
# 
#      if ns.DATAFAQS['Unsatisfactory'] not in output.rdf_type:
#         output.rdf_type.append(ns.DATAFAQS['Satisfactory'])
#
#      output.save()

# Used when Twistd invokes this service b/c it is sitting in a deployed directory.
resource = RDF2ASN()

# Used when this service is manually invoked from the command line (for testing).
if __name__ == '__main__':
   print resource.name + ' running on port ' + str(resource.dev_port) + '. Invoke it with:'
   print 'curl -H "Content-Type: text/turtle" -d @my.ttl http://localhost:' + str(resource.dev_port) + '/' + resource.name
   sadi.publishTwistedService(resource, port=resource.dev_port)
