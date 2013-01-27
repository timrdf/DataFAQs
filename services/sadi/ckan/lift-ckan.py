#3> <> prov:specializationOf <https://github.com/timrdf/DataFAQs/raw/master/services/sadi/ckan/lift-ckan.py>;
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

import ckanclient
import os
import hashlib
import re

# These are the namespaces we are using beyond those already available
# (see http://packages.python.org/SuRF/modules/namespace.html#registered-general-purpose-namespaces)
ns.register(moat='http://moat-project.org/ns#')
ns.register(ov='http://open.vocab.org/terms/')
ns.register(void='http://rdfs.org/ns/void#')
ns.register(con='http://www.w3.org/2000/10/swap/pim/contact#')
ns.register(dcat='http://www.w3.org/ns/dcat#')
ns.register(sd='http://www.w3.org/ns/sparql-service-description#')
ns.register(conversion='http://purl.org/twc/vocab/conversion/')
ns.register(datafaqs='http://purl.org/twc/vocab/datafaqs#')
ns.register(prov='http://www.w3.org/ns/prov#')

# The Service itself
class LiftCKAN(faqt.CKANReader):

   # Service metadata.
   label                  = 'lift-ckan'
   serviceDescriptionText = 'Accesses the current CKAN listing for the given datasets and returns a well-designed* RDF form of the same.'
   comment                = 'Thanks to Will Wates\' https://bitbucket.org/okfn/gockan for some modeling guidance.'
   serviceNameText        = 'lift-ckan' # Convention: Match 'name' below.
   name                   = 'lift-ckan' # This value determines the service URI relative to http://localhost:9090/
                                        # Convention: Use the name of this file for this value.
   dev_port = 9225

   def __init__(self):
      # DATAFAQS_PROVENANCE_CODE_RAW_BASE                   +  servicePath  +  '/'  + self.serviceNameText
      # DATAFAQS_PROVENANCE_CODE_PAGE_BASE                  +  servicePath  +  '/'  + self.serviceNameText
      #
      # ^^ The source code location
      #    aligns with the deployment location \/
      #
      #                 DATAFAQS_BASE_URI  +  '/datafaqs/'  +  servicePath  +  '/'  + self.serviceNameText
      faqt.CKANReader.__init__(self, servicePath = 'services/sadi/ckan') # TEMPLATE: change to something like 'services/sadi/faqt/connected/' to get free provenance.

      # Instantiate the CKAN client.
      # http://docs.python.org/library/configparser.html (could use this technique)
      #key = os.environ['X_CKAN_API_Key'] # See https://github.com/timrdf/DataFAQs/wiki/Missing-CKAN-API-Key
      #self.ckan = ckanclient.CkanClient(api_key=key)
      #self.ckan = ckanclient.CkanClient()

   def getOrganization(self):
      result                      = self.Organization()
      result.mygrid_authoritative = True
      result.protegedc_creator    = 'lebot@rpi.edu'
      result.save()
      return result

   def getInputClass(self):
      return ns.DATAFAQS['CKANDataset']

   def getOutputClass(self):
      return ns.DATAFAQS['CKANDataset']

   def process(self, input, output):

      print 'processing ' + input.subject

      ckan    = self.getCKANAPI(input)
      ckan_id = self.getCKANIdentiifer(input)
      print 'ckan_id ' + ckan_id

      #
      # GET the current dataset metadata listing from CKAN.
      dataset = {}
      try:
         ckan.package_entity_get(ckan_id)
         dataset = ckan.last_message

         print dataset.keys()
         print
         print dataset

         #
         # Process Attributes
         #
         if 'title' in dataset:
            output.dcterms_title = dataset['title']

         if 'notes' in dataset:
            output.dcterms_description = dataset['notes']

         #
         # Process Resources
         #
         Thing   = output.session.get_class(ns.OWL['Thing'])
         Service = output.session.get_class(ns.SD['Service'])
         sparqlEndpoint = None
         for resource in dataset['resources']:
            if resource['format'] == u'api/sparql':
               #
               # <dataset> void:sparqlEndpoint <endpoint> .
               #
               endpoint = Thing(resource['url'])
               endpoint.dcterms_title = resource['description']
               endpoint.save()
               service  = Service('#service-'+hashlib.sha224(resource['url']).hexdigest())
               service.sd_endpoint = endpoint
               service.save()
               sparqlEndpoint = {'url': Thing(resource['url']), # Saved for processing sparql_named_graph below.
                                 'id' : resource['id']} 
               output.void_sparqlEndpoint.append(Service(resource['url']))
            if resource['format'] == u'example/turtle':
               #
               # <dataset> void:exampleResource <> .
               #
               output.void_sparqlEndpoint.append(Thing(resource['url']))
               # TODO: elaborate this description.
            else:
               print 'TODO: handle resource: ' + resource['format']

         #
         # Process Groups
         #
         Group = output.session.get_class(ns.DATAFAQS['CKANGroup'])
         for group in dataset['groups']:
            groupR = Group(re.sub('/dataset/.*$','/group/'+group,str(input.subject)))
            print 'group: ' + group + ' -> ' + groupR.subject
            groupR.rdf_type.append(ns.DATAFAQS['CKANGroup'])
            groupR.dcterms_identifier.append(group)
            groupR.rdfs_label.append(group)
            groupR.foaf_name.append(group)
            groupR.save()
            output.dcterms_isPartOf.append(groupR)

         #
         # Process Extras
         #
         DCATDataset  = output.session.get_class(ns.DCAT['Dataset'])
         Distribution = output.session.get_class(ns.DCAT['Distribution'])
         Linkset      = output.session.get_class(ns.VOID['Linkset'])
         links_regex  = re.compile("^links:(.*)$")
         NamedGraph   = output.session.get_class(ns.SD['NamedGraph'])
         CKANDataset  = output.session.get_class(ns.DATAFAQS['CKANDataset'])
         for extra in dataset['extras']:
            if extra == u'triples':
               try:
                  print str(dataset['extras'][extra])
                  triples = int(re.sub('\D','',str(dataset['extras'][extra])))
                  print '     -> ' + str(triples)
                  #
                  # <dataset> void:triples 1000 .
                  #
                  output.void_triples = triples
               except ValueError:
                  # e.g. invalid literal for int() with base 10: '' from rdf-book-mashup
                  print 
            elif extra == u'shortname':
               #
               # <dataset> ov:shortName "DBPedia" .
               #
               output.ov_shortName = dataset['extras'][extra]
            elif links_regex.match(str(extra)):
               #
               # <dataset> void:subset [ a void:Linkset; void:target <dataset>, <target>; void:size 50 ] .
               #
               for target in links_regex.findall(str(extra)):
                  target = target.replace(' ','-')
                  print 'found link to ' + target
                  print '           from ' + output.subject
                  print '                revision_id ' + dataset['revision_id']
                  linkset = Linkset('#linkset-'+target+'-'+hashlib.sha224(output.subject+target+dataset['revision_id']).hexdigest())
                  linkset.void_target.append(output)
                  linkset.void_target.append(CKANDataset('http://thedatahub.org/dataset/'+target))
                  try:
                     linkset.void_triples = int(dataset['extras'][extra])
                  except ValueError:
                     # e.g. invalid literal for int() with base 10: '???' from scotland-statistical-geography
                     print
                  linkset.save()
                  output.void_subset.append(linkset)
            elif extra == u'preferred_uri':
               #
               # <dataset> con:preferrredURI <another> .
               #
               output.con_preferredURI.append(DCATDataset(dataset['extras'][extra]))
            elif extra == u'namespace':
               #
               # <dataset> void:uriSpace "http://dbpedia.org/resource/" .
               #
               output.void_uriSpace = dataset['extras'][extra]
            elif extra == u'sparql_graph_name':
               #
               # <dataset> dcat:distribution [
               #    a sd:NamedGraph;
               #    sd:name  <http://purl.org/twc/arrayexpress/E-MTAB-104>;
               #    sd:graph <http://thedatahub.org/en/dataset/arrayexpress-e-afmx-1>;
               #    prov:atLocation <sparqlEndpoint>
               # ];
               #
               if sparqlEndpoint is not None:
                  ng = NamedGraph('#named-graph-'+sparqlEndpoint['id'])
                  ng.sd_name         = Thing(dataset['extras'][extra])
                  ng.prov_atLocation = sparqlEndpoint['url']
                  ng.save()
                  output.dcat_distribution.append(ng)
            else:
               print extra + ' = ' 
               print dataset['extras'][extra]
               print dataset['revision_id']
               print
               print 

         output.rdf_type.append(ns.DCAT['Dataset'])
         output.save()
      except ckanclient.CkanApiNotFoundError:
         print 'Error: could not get ckan dataset ' + ckan_id

# Used when Twistd invokes this service b/c it is sitting in a deployed directory.
resource = LiftCKAN()

# Used when this service is manually invoked from the command line (for testing).
if __name__ == '__main__':
   print resource.name + ' running on port ' + str(resource.dev_port) + '. Invoke it with:'
   print 'curl -H "Content-Type: text/turtle" -d @my.ttl http://localhost:' + str(resource.dev_port) + '/' + resource.name
   sadi.publishTwistedService(resource, port=resource.dev_port)
