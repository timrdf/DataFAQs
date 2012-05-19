#3> <> prov:specializationOf <#TEMPLATE/path/to/public/source-code.rpy>;
#3>    rdfs:seeAlso <https://github.com/timrdf/DataFAQs/wiki/FAqT-Service> .
#3>
#3> <#TEMPLATE/path/to/where/source-code.rpy/is/deployed/for/invocation>
#3>    a datafaqs:FAqTService .
#3> []
#3>    a prov:Activity;
#3>    prov:qualifiedAttribution [
#3>       a prov:Attribution;
#3>       prov:entity  <#TEMPLATE/path/to/where/source-code.rpy/is/deployed/for/invocation>;
#3>       prov:hadPlan <#TEMPLATE/path/to/public/source-code.rpy>;
#3>    ];
#3> .
#3> <#TEMPLATE/path/to/public/source-code.rpy>
#3>    a prov:Plan;
#3>    foaf:homepage <#TEMPLATE/path/to/public/HOMEPAGE-FOR/source-code.rpy> .

import faqt

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
ns.register(void='http://rdfs.org/ns/void#')
ns.register(dcat='http://www.w3.org/ns/dcat#')
ns.register(datafaqs='http://purl.org/twc/vocab/datafaqs#')

# The Service itself
class VoIDLinkset(faqt.Service):

   # Service metadata.
   label                  = 'void-linkset'
   serviceDescriptionText = 'Passes datasets that have void:subset [ a void:Linkset; void:target ?t; void:triples ?x ].'
   comment                = 'Only looks at the metadata give; does not analyze the data elements themselves.'
   serviceNameText        = 'void-linkset' # Convention: Match 'name' below.
   name                   = 'void-linkset' # This value determines the service URI relative to http://localhost:9090/
                                           # Convention: Use the name of this file for this value.
   dev_port = 9224

   def __init__(self): 
      faqt.Service.__init__(self)

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

      # prefix void: <http://rdfs.org/ns/void#>
      #
      # select ?from ?to ?overlap
      # where {
      #    ?from void:subset [ 
      #       a void:Linkset; 
      #       void:target  ?from, 
      #                    ?to; 
      #       void:triples ?overlap;
      #    ] .
      #    filter( ?from != ?to )
      # }
      query = select('?to ?overlap').where((input.subject, ns.VOID['subset'],  '?linkset'),
                                           ('?linkset',    a,                  ns.VOID['Linkset']),
                                           ('?linkset',    ns.VOID['target'],  input.subject),
                                           ('?linkset',    ns.VOID['target'],  '?to'),
                                           ('?linkset',    ns.VOID['triples'], '?overlap')).filter('(?to != <'+input.subject+'>)')
      results = input.session.default_store.execute(query)
      for binding in results:
         target  = binding[0]
         overlap = binding[1]
         #print target + ' ' + overlap
         if overlap >= 50: # "We arbitrarily require at least 50 links." -http://richard.cyganiak.de/2007/10/lod/
            output.rdf_type.append(ns.DATAFAQS['Satisfactory'])

      if ns.DATAFAQS['Satisfactory'] not in output.rdf_type:
         output.rdf_type.append(ns.DATAFAQS['Unsatisfactory'])

      output.save()

# Used when Twistd invokes this service b/c it is sitting in a deployed directory.
resource = VoIDLinkset()

# Used when this service is manually invoked from the command line (for testing).
if __name__ == '__main__':
   print resource.name + ' running on port ' + str(resource.dev_port) + '. Invoke it with:'
   print 'curl -H "Content-Type: text/turtle" -d @my.ttl http://localhost:' + str(resource.dev_port) + '/' + resource.name
   sadi.publishTwistedService(resource, port=resource.dev_port)
