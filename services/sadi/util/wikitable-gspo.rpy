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

from BeautifulSoup import BeautifulSoup          # For processing HTML

# These are the namespaces we are using beyond those already available
# (see http://packages.python.org/SuRF/modules/namespace.html#registered-general-purpose-namespaces)
ns.register(moat='http://moat-project.org/ns#')
ns.register(ov='http://open.vocab.org/terms/')
ns.register(void='http://rdfs.org/ns/void#')
ns.register(dcat='http://www.w3.org/ns/dcat#')
ns.register(sd='http://www.w3.org/ns/sparql-service-description#')
ns.register(conversion='http://purl.org/twc/vocab/conversion/')
ns.register(datafaqs='http://purl.org/twc/vocab/datafaqs#')

PREFIX = 0
LOCAL  = 1

# The Service itself
class WikiTableGSPO(sadi.Service):

   # Service metadata.
   label                  = 'wikitable-gpso'
   serviceDescriptionText = 'Scrapes a mediawiki page for tables created with mediawiki markup to list the RDF classes and properties listed.'
   comment                = ''
   serviceNameText        = 'wikitable-gpso' # Convention: Match 'name' below.
   name                   = 'wikitable-gpso' # This value determines the service URI relative to http://localhost:9090/
                                             # Convention: Use the name of this file for this value.
   dev_port = 9115

   def __init__(self): 
      sadi.Service.__init__(self)
      self.regex = re.compile("([a-zA-Z0-9]+):([a-zA-Z0-9]+)")
      self.namespaces = {}

   def getOrganization(self):
      result                      = self.Organization()
      result.mygrid_authoritative = True
      result.protegedc_creator    = 'lebot@rpi.edu'
      result.save()
      return result

   def getInputClass(self):
      return ns.FOAF['Document']

   def getOutputClass(self):
      return ns.FOAF['Document']

   def process(self, input, output):

      print 'processing ' + input.subject

      page = urllib2.urlopen(input.subject)
      soup = BeautifulSoup(page)

      Thing = output.session.get_class(ns.OWL['Thing'])

      for table in soup('table'):
         for tr in table.findAll('tr'):
            for td in tr.findAll('td'):
               for curie in self.regex.findall(str(td.string)):
                  print '   document contained curie ' + curie[PREFIX] + ':' + curie[LOCAL]
                  if not curie[PREFIX] in self.namespaces:
                     # Need to find namespace for this prefix, since we haven't seen it before.
                     # http://prefix.cc/prov.file.txt
                     prefixcc = urllib2.urlopen('http://prefix.cc/'+curie[PREFIX]+'.file.txt')
                     namespace = prefixcc.read().split()[1]
                     self.namespaces[curie[PREFIX]] = namespace
                     print '      FETCHED prefix.cc namespace for ' + curie[PREFIX] + ' : ' + self.namespaces[curie[PREFIX]]
                  else:
                     print '      reusing prefix.cc cached namespace for ' + curie[PREFIX] + ' : ' + self.namespaces[curie[PREFIX]]
                  topic = Thing(self.namespaces[curie[PREFIX]] + curie[LOCAL])
                  output.dcterms_subject.append(topic)
                  output.rdf_type.append(ns.DATAFAQS['Satisfactory'])

      if ns.DATAFAQS['Satisfactory'] not in output.rdf_type:
         output.rdf_type.append(ns.DATAFAQS['Unsatisfactory'])

      output.save()

      # <table class="wikitable" cellpadding="10" style="background: #E8E8E8">
      #    <tr>
      #       <th rowspan="1" colspan="1">PROV-N</th>
      #       <th rowspan="1" colspan="1">sd:name</th>
      #       <th rowspan="1" colspan="1">Subject</th>
      #       <th rowspan="1" colspan="1">Predicate</th>
      #       <th rowspan="1" colspan="1">Object</th>
      #    </tr>
      #    <tr>
      #       <td rowspan="1" colspan="1">entity(id,[attr_1=val_1,...,attr_n=val_n])</td>
      #       <td rowspan="1" colspan="1"/>
      #       <td rowspan="1" colspan="1"/>
      #       <td rowspan="1" colspan="1"/>
      #       <td rowspan="1" colspan="1"/>
      #    </tr>
      #    <tr>
      #       <td rowspan="1" colspan="1"/>
      #       <td rowspan="1" colspan="1"/>
      #       <td rowspan="1" colspan="1">:id</td>
      #       <td style="background: white" rowspan="1" colspan="1">a</td>
      #       <td style="background: PapayaWhip" rowspan="1" colspan="1">prov:Entity</td>
      #    </tr>
      #    <tr>
      #       <td rowspan="1" colspan="1"/>
      #       <td rowspan="1" colspan="1"/>
      #       <td rowspan="1" colspan="1">:id</td>
      #       <td rowspan="1" colspan="1">attr_1</td>
      #       <td rowspan="1" colspan="1">val_1</td>
      #    </tr>
      #    <tr>
      #       <td rowspan="1" colspan="1"/>
      #       <td rowspan="1" colspan="1"/>
      #       <td rowspan="1" colspan="1">...</td>
      #       <td rowspan="1" colspan="1"/>
      #       <td rowspan="1" colspan="1"/>
      #    </tr>
      #    <tr>
      #       <td rowspan="1" colspan="1"/>
      #       <td rowspan="1" colspan="1"/>
      #       <td rowspan="1" colspan="1">:id</td>
      #       <td rowspan="1" colspan="1">attr_n</td>
      #       <td rowspan="1" colspan="1">val_n</td>
      #    </tr>
      # </table>

# Used when Twistd invokes this service b/c it is sitting in a deployed directory.
resource = WikiTableGSPO()

# Used when this service is manually invoked from the command line (for testing).
if __name__ == '__main__':
   print resource.name + ' running on port ' + str(resource.dev_port) + '. Invoke it with:'
   print 'curl -H "Content-Type: text/turtle" -d @my.ttl http://localhost:' + str(resource.dev_port) + '/' + resource.name
   sadi.publishTwistedService(resource, port=resource.dev_port)
