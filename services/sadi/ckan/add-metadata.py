#3> <> prov:specializationOf <https://github.com/timrdf/DataFAQs/raw/master/services/sadi/ckan/add-metadata.py>;
#3>    rdfs:seeAlso <https://github.com/timrdf/DataFAQs/wiki/FAqT-Service> .

import faqt
from faqt import *

import sadi
from rdflib import *
from surf import *
from surf.query import a, select

import rdflib
rdflib.plugin.register('sparql', rdflib.query.Processor,
                     'rdfextras.sparql.processor', 'Processor')
rdflib.plugin.register('sparql', rdflib.query.Result,
                     'rdfextras.sparql.query', 'SPARQLQueryResult')

import ckanclient
import os

import httplib
from urlparse import urlparse, urlunparse
import urllib
connections = {'http' :httplib.HTTPConnection,
             'https':httplib.HTTPSConnection}

# These are the namespaces we are using beyond those already available
# (see http://packages.python.org/SuRF/modules/namespace.html#registered-general-purpose-namespaces)
ns.register(moat='http://moat-project.org/ns#')
ns.register(con='http://www.w3.org/2000/10/swap/pim/contact#')
ns.register(ov='http://open.vocab.org/terms/')
ns.register(dcat='http://www.w3.org/ns/dcat#')
ns.register(sd='http://www.w3.org/ns/sparql-service-description#')
ns.register(prov='http://www.w3.org/ns/prov#')
ns.register(void='http://rdfs.org/ns/void#')
ns.register(datafaqs='http://purl.org/twc/vocab/datafaqs#')
ns.register(tag='http://www.holygoat.co.uk/owl/redwood/0.1/tags/')

THEDATAHUB = 'http://datahub.io'

def getResponse(url):
   # Ripped from https://github.com/timrdf/csv2rdf4lod-automation/blob/master/bin/util/pcurl.py
   o = urlparse(str(url))
   #print o
   connection = connections[o.scheme](o.netloc)
   fullPath = urlunparse([None,None,o.path,o.params,o.query,o.fragment])
   connection.request('GET',fullPath)
   return connection.getresponse()

# The Service itself
class AddCKANMetadata(faqt.CKANReaderWriter):

   # Service metadata.
   label                  = 'Update CKAN Dataset Metadata'
   serviceDescriptionText = 'Modifies an existing CKAN dataset listing based on the MOAT tags and VoID POSTed to this service.'
   comment                = ''
   serviceNameText        = 'add-metadata' # Convention: same as 'name' below.
   name                   = 'add-metadata' # This value determines the service URI relative to http://localhost:9090/
                                           # Convention: same as filename.
   namespace              = {}
   prefix                 = {}
   dev_port               = 9090

   def __init__(self):
      faqt.Service.__init__(self, servicePath = 'services/sadi/ckan')
      
      # Instantiate the CKAN client.
      key = os.environ['X_CKAN_API_Key']
      if len(key) <= 1:
         print 'ERROR: https://github.com/timrdf/DataFAQs/wiki/Missing-CKAN-API-Key'
         sys.exit(1)
      self.ckan = ckanclient.CkanClient(base_location=THEDATAHUB+'/api', api_key=key)

   def getOrganization(self):
      result                      = self.Organization('http://tw.rpi.edu')
      result.mygrid_authoritative = True
      result.protegedc_creator    = 'lebot@rpi.edu'
      result.save()
      return result

   def getInputClass(self):
      return ns.DATAFAQS['CKANDataset']

   def getOutputClass(self):
      return ns.DATAFAQS['ModifiedCKANDataset']

   def prefixcc(self, prefix, namespace):
      if prefix is not None:
         response = getResponse('http://prefix.cc/' + prefix + '.file.json')
         if response.status == 200:
            ns = response.msg.dict[prefix]
            print prefix + ' -> ' + ns
            self.namespace[pre] = ns
            self.prefix[ns]     = prefix
         else:
            print str(response.status) + ' ' + ns
      elif namespace is not None:
         # http://prefix.cc/?q=http://www.w3.org/2003/01/geo/wgs84_pos 
         # 302s to http://prefix.cc/geo
         response = getResponse('http://prefix.cc/?' + urllib.urlencode({'q':namespace}))
         if response.status == 302:
            pre        = response.msg.dict['location'].replace('http://prefix.cc/','')
            prefix_tag = 'format-' + pre
            print str(response.status) + ' ' + namespace + ' ' + response.msg.dict['location'] + ' ' + prefix_tag
            print pre + ' -> ' + namespace
            self.namespace[pre]    = namespace
            self.prefix[namespace] = pre
         else:
            print str(response.status) + ' ' + namespace

      for p in self.namespace.keys():
         print 'cached ' + self.namespace[p] + ' as ' + p
      for n in self.prefix.keys():
         print 'cached ' + self.prefix[n] + ' as ' + n

      return

   def process(self, input, output):

      print 'processing ' + input.subject

      #
      # identifier

      ckan    = self.getCKANAPI(input)
      ckan_id = self.getCKANIdentiifer(input)
      if ckan_id is not None:
         print 'ckan_id ' + ckan_id
      else:
         print 'Error: cannot determine dataset identifier to create/modify'
      
      #
      # GET the current dataset metadata listing from CKAN.
      dataset = {}
      try:
         ckan.package_entity_get(ckan_id)
         dataset = ckan.last_message
      except ckanclient.CkanApiNotFoundError:
         # If we want to play it safe - only modify existing datasets.
         #output.rdf_type.append(ns.DATAFAQS['NotCKANDataset'])
         #output.save()
         #return

         print 'CKAN dataset id does not exist; registering it on CKAN.' 
         # Register the dataset
         package_entity = { 'name': ckan_id }
         #try:
         ckan.package_register_post(package_entity)

         # GET the new dataset metadata listing from CKAN.
         ckan.package_entity_get(ckan_id)
         dataset = ckan.last_message
         #except ckanclient.CkanApiNotAuthorizedError as e:
         #   print e.message
         #   return
 
      print dataset

      #                   lodcloud Level 1 "Title"
      # dcterms:title ==> ckan:title
      if len(input.dcterms_title) > 0:
         dataset['title'] = input.dcterms_title.first

      #
      # dcterms:description ?description
      if len(input.dcterms_description) > 0:
         dataset['notes'] = input.dcterms_description.first

      #                                                                lodcloud Level 3 "License"
      # dcterms:license                                           ==>  ckan:license
      #
      # These are taken from CKAN directly:
      #   http://www.opendefinition.org/licenses/odc-pddl         ==> 'Open Data Commons Public Domain Dedication and Licence (PDDL)' (OPEN)
      #   http://www.opendefinition.org/licenses/odc-odbl         ==> 'Open Data Commons Open Database License (ODbL)'                (OPEN)
      #   http://www.opendefinition.org/licenses/odc-by           ==> 'Open Data Commons Attribution License'                         (OPEN)
      #   http://www.opendefinition.org/licenses/cc-zero          ==> 'Creative Commons CCZero'                                       (OPEN)
      #   http://www.opendefinition.org/licenses/cc-by            ==> 'Creative Commons Attribution'                                  (OPEN)
      #   http://www.opendefinition.org/licenses/cc-by-sa         ==> 'Creative Commons Attribution Share-Alike'                      (OPEN)
      #   http://www.opendefinition.org/licenses/gfdl             ==> 'GNU Free Documentation License'                                (OPEN)
      #                                                           ==> 'Other (Open)'                                                  (OPEN) 
      #                                                           ==> 'Other (Public Domain)'                                         (OPEN) 
      #                                                           ==> 'Other (Attribution)'                                           (OPEN) 
      #   http://reference.data.gov.uk/id/open-government-licence ==> 'UK Open Government Licence (OGL)'                              (OPEN)
      #   http://creativecommons.org/licenses/by-nc/2.0/          ==> 'Creative Commons Non-Commercial (Any)'                        (CLOSED)
      #                                                           ==> 'Other (Non-Commercial)'                                       (CLOSED) 
      #                                                           ==> 'Other (Not Open)'                                             (CLOSED) 
      # VoID spec mentions some at http://www.w3.org/TR/void/#license

      if len(input.dcterms_license) > 0:
         license = self.surfSubject(input.dcterms_license.first)
         licenses = { 
            'http://www.opendefinition.org/licenses/odc-pddl':          {'label':'Open Data Commons Public Domain Dedication and Licence (PDDL)'},
            'http://www.opendefinition.org/licenses/odc-odbl':          {'label':'Open Data Commons Open Database License (ODbL)'},
            'http://www.opendefinition.org/licenses/odc-by':            {'label':'Open Data Commons Attribution License'},
            'http://www.opendefinition.org/licenses/cc-zero':           {'label':'Creative Commons CCZero'},
            'http://www.opendefinition.org/licenses/cc-by':             {'label':'Creative Commons Attribution',
                                                                         'id':'cc-by'},
            'http://www.opendefinition.org/licenses/cc-by-sa':          {'label':'Creative Commons Attribution Share-Alike'},
            'http://www.opendefinition.org/licenses/gfdl':              {'label':'GNU Free Documentation License'},
            'http://reference.data.gov.uk/id/open-government-licence':  {'label':'UK Open Government Licence (OGL)'},
            'http://creativecommons.org/licenses/by-nc/2.0/':           {'label':'Creative Commons Non-Commercial (Any)'}}
         print 'license: ' + license + ' ' + licenses[license]['label']

         dataset['license_url']   = license
         dataset['license_id']    = licenses[license]['id']
         dataset['license']       = licenses[license]['label']
         dataset['license_title'] = licenses[license]['label']
         print dataset['license']

      #                   lodcloud Level 1: "URL"
      # foaf:homepage ==> {ckan:source, ckan:homepage, ckan:url}
      if len(input.foaf_homepage) > 0:
         dataset['url'] = input.foaf_homepage.first

      #                                              lodcloud Level 1 "Author"
      # dcterms:creator [ foaf:mbox, foaf:name ] ==> ckan:author
      query = select("?name ?mbox").where((input.subject, ns.DCTERMS['creator'], "?creator"),
                                          ("?creator",    ns.FOAF['mbox'],       "?mbox"),
                                          ("?creator",    ns.FOAF['name'],       "?name"))
      for bindings in input.session.default_store.execute(query):
         #print 'creator: ' + bindings[0] + ' ' + bindings[1]
         dataset['author']       = re.sub('^mailto:','',bindings[0])
         dataset['author_email'] = re.sub('^mailto:','',bindings[1])

      #
      # dcterms:contributor ==> ckan:maintainer
      query = select("?name ?mbox").where((input.subject,  ns.DCTERMS['contributor'], "?contributor"),
                                          ("?contributor", ns.FOAF['mbox'],           "?mbox"),
                                          ("?contributor", ns.FOAF['name'],           "?name"))
      for bindings in input.session.default_store.execute(query):
         #print 'contributor: ' + bindings[0] + ' ' + bindings[1]
         dataset['maintainer']       = re.sub('^mailto:','',bindings[0])
         dataset['maintainer_email'] = re.sub('^mailto:','',bindings[1])

      #
      # Core: groups
      # ?d dc:isPartOf <http://ckan.net/group/datafaqs> . <http://ckan.net/group/datafaqs> a datafaqs:CKANGroup .
      #for ckan_group in input.dcterms_isPartOf:
      #   if ns.DATAFAQS['CKANGroup'] in ckan_group.rdf_type and \
      #      str(ckan_group) != 'http://ckan.net/group/lodcloud':
      #      dataset['groups'].append(ckan_group.replace('http://ckan.net/group/','')
      # ^^ Not sure why this is commented out - 2012 May 4 lebot
      #
      query = select("?group").where((input.subject, ns.DCTERMS['isPartOf'], "?group"),
                                                                            ("?group", a, ns.DATAFAQS['CKANGroup']))
      results = input.session.default_store.execute(query)
      if 'groups' not in dataset:
         dataset['groups'] = []
      for binding in results:
         ckan_group = binding[0] # e.g. http://thedatahub.org/group/arrayexpress
         ckan_group_id = re.sub('http.*/group/','',str(ckan_group))
         if ckan_group_id != 'lodcloud': # Prevent spamming of the manually curated set.
            dataset['groups'].append(ckan_group_id) 

      if 'extras' not in dataset:
         dataset['extras'] = {}

      # Extra: shortName
      if input.ov_shortName:
         dataset['extras']['shortname'] = input.ov_shortName.first

      # Extra: namespace
      if input.datafaqs_namespace:
         dataset['extras']['namespace'] = self.surfSubject(input.datafaqs_namespace.first)
      if input.void_uriSpace:
         dataset['extras']['namespace'] = self.surfSubject(input.void_uriSpace.first)

      # Extra: triples
      if input.void_triples:
         dataset['extras']['triples'] = str(input.void_triples.first)

      # Extra: preferred_uri
      if input.con_preferredURI:
          dataset['extras']['preferred_uri'] = input.con_preferredURI.first

      linksQuery = '''
prefix owl:  <http://www.w3.org/2002/07/owl#>
prefix void: <http://rdfs.org/ns/void#>

select distinct ?subset ?size ?other
where {

  {<''' + input.subject + '''> void:subset ?subset .
  ?subset
    a void:Linkset;
    void:target  <''' + input.subject + '''>,
                 ?other;
    void:triples ?size}

  union

  {<''' + input.subject + '''> owl:sameAs ?ckan;
    void:subset ?subset .
  ?subset
    a void:Linkset;
    void:target  ?ckan,
                 ?other;
    void:triples ?size}
}
'''
      #
      # Extra: link:*

      #results = input.session.default_store.execute_sparql(linksQuery)
      #if results is not None:
      #   for bindings in results['results']['bindings']:
      #       otherbubble = str(bindings['otherbubble']['value'])
      #       if otherbubble != str(input.subject): # TODO: why is input.subject appearing?
      #          attribute = 'links:' + otherbubble.replace('http://thedatahub.org/dataset/','')
      #          print attribute + ' = ' + bindings['triples']['value']
      #          dataset['extras'][attribute] = bindings['triples']['value']

      # ^ done before (string queries broke in SuRF API); \/ done Jan 2013

      # 
      # links between this bubble and others on the LOD Cloud diagram.
      # 
      # <http://datahub.io/dataset/twc-healthdata>
      #    a datafaqs:CKANDataset;
      #    void:subset :linkset_396c515e06a9f050327af7e61a0ca50b .
      # 
      # :linkset_396c515e06a9f050327af7e61a0ca50b 
      #      void:target 
      #        <http://datahub.io/dataset/twc-healthdata>, 
      #        <http://datahub.io/dataset/2000-us-census-rdf>;
      #      void:triples     1535;
      # .
      query = select("?other ?size").where((input.subject, ns.VOID['subset'],  "?linkset"),
                                           ("?linkset",    ns.VOID['target'],  input.subject),
                                           ("?linkset",    ns.VOID['target'],  "?other"),
                                           ("?linkset",    ns.VOID['triples'], "?size"))
      linkedTo = []
      for bindings in input.session.default_store.execute(query):
         if str(bindings[0]) != str(input.subject):
            other = re.sub('^.*/dataset/','',str(bindings[0]))
            print linkedTo
            if other not in linkedTo:
               linkedTo.append(other)
               attribute = u'links:'+other
               print attribute + ' = ' + bindings[1]
               dataset['extras'][attribute] = int(bindings[1])
            else:
               print 'WARNING: ' + other + ' already had an assertion'

      # Tags
      if 'tags' not in dataset:
         dataset['tags'] = []
      for tag_uri in input.moat_taggedWithTag:
         tag = None
         try:
            # When tag_uri is typed to _anything_
            tag = tag_uri.moat_name.first 
         except:
            # SuRF returns URIRefs when they are not typed...
            # Or, the moat_name wasn't there (Hack the URI: naughty)
            tag = re.sub('^.*tag/','',str(tag_uri))

         if tag is not None:
            dataset['tags'].append(tag)

      for tag_uri in input.tag_taggedWithTag:
         tag = None
         try:
            # When tag_uri is typed to _anything_
            tag = tag_uri.tag_name.first 
         except:
            # SuRF returns URIRefs when they are not typed...
            # Or, the moat_name wasn't there (Hack the URI: naughty)
            tag = re.sub('^.*tag/','',str(tag_uri))

         if tag is not None:
            dataset['tags'].append(tag)

      #
      # Tags: format-*
      namespace = {}
      for vocab in input.void_vocabulary:
          # http://prefix.cc/?q=http://www.w3.org/2003/01/geo/wgs84_pos 
          # 302s to http://prefix.cc/geo
          response = getResponse('http://prefix.cc/?' + urllib.urlencode({'q':vocab}))
          if response.status == 302:
             prefix     = response.msg.dict['location'].replace('http://prefix.cc/','')
             prefix_tag = 'format-' + prefix
             print str(response.status) + ' ' + vocab + ' ' + response.msg.dict['location'] + ' ' + prefix_tag
             namespace[prefix] = vocab
             dataset['tags'].append(prefix_tag)
          else:
             print str(response.status) + ' ' + vocab

      # Index the dataset's resources by url
      if 'resources' not in dataset:
         dataset['resources'] = []
      dataset_resources = {}
      for resource in dataset['resources']:
         print 'indexing ' + resource['url']
         dataset_resources[URIRef(resource['url'])] = resource

      #
      # SPARQL Endpoint (two ways)
      sparqlEndpoint = False
      if len(input.void_sparqlEndpoint) > 0:
         sparqlEndpoint = input.void_sparqlEndpoint.first # This gets overridden if more elaborate
                                                          # description provides the named graph.

      query = select("?endpoint ?name").where((input.subject,  ns.DCAT['distribution'], "?ng"),
                                              ("?ng",          ns.SD['name'],           "?name"),
                                              ("?ng",          ns.PROV['atLocation'],   "?service"),
                                              ("?service",     ns.SD['endpoint'],       "?endpoint"))
      for bindings in input.session.default_store.execute(query):
         sparqlEndpoint                         = bindings[0]
         dataset['extras']['sparql_graph_name'] = bindings[1] # overwrites void:sparqlEndpoint

      if sparqlEndpoint is not False and URIRef(self.surfSubject(sparqlEndpoint)) not in dataset_resources:
         # Resource with this URL did not exist.
         print 'brand new sparql endpoint ' + self.surfSubject(sparqlEndpoint)
         dataset['resources'].append( { 'name':   'SPARQL Endpoint',
                                        'url':    self.surfSubject(sparqlEndpoint), 
                                        'format': 'api/sparql' } )
      #
      # void:vocabulary
      for vocab in input.void_vocabulary:
         print 'used ' + vocab 
         if vocab not in dataset_resources:
            print 'not stated'
            self.prefixcc(None,vocab)
            title = 'a'
            if vocab in self.prefix:
               title = self.prefix[vocab]
            dataset['resources'].append( { 'name':   title+' RDF Schema',
                                           'url':    self.surfSubject(vocab), 
                                           'format': 'meta/rdf-schema' } )
      #
      # void:exampleResource (lodcloud Level 2 "example URI")
      for egResource in input.void_exampleResource:
         if URIRef(self.surfSubject(egResource)) not in dataset_resources:
            print 'eg resource ' + egResource 
            dataset['resources'].append( { 'url':     self.surfSubject(egResource), 
                                           'resource_type': 'file',
                                           'format':        'example/rdf+xml', # Their demand for the format is nonsensical for true conneg Linked Data.
                                           'name':          'Example URI',
                                           'mimetype':       '',
                                           'mimetype_inner': '',
                                           'description':    '' } )            # DO NOT provide a description, since you'd be describing the wrong thing.
         else:
            print 'repeat eg resource ' + egResource 
   
      #
      # lodcloud Level 3 "VoID or Semantic Sitemap"
      #
      query = select("?void").where(("?void", a,                       ns.VOID['DatasetDescription']),
                                    ("?void", ns.FOAF['primaryTopic'], input.subject))
      for bindings in input.session.default_store.execute(query):
         void = bindings[0]
         if void not in dataset_resources:
            print 'void: ' + void
            dataset['resources'].append( { 'url':     void, 
                                           'resource_type': 'file',
                                           'format':        'meta/void',
                                           'name':          'VoID Listing',
                                           'mimetype':       'text/turtle',
                                           'mimetype_inner': 'text/turtle',
                                           'description':    'Listing of all RDF datasets available, using the Vocabulary of Interlinked Datasets (VoID)' } )
         else:
            print 'repeat void: ' + void
         #dataset['author_email'] = re.sub('^mailto:','',bindings[1])
 
     

      # POST the new details of the dataset.
      print dataset
      ckan.package_entity_put(dataset)

      # GET the timestamp of the change we just submitted.
      ckan.package_entity_get(ckan_id)
      dataset = ckan.last_message
      output.dcterms_modified = dataset['metadata_modified']
      output.rdfs_seeAlso = output.session.get_resource(THEDATAHUB + '/dataset/' + ckan_id, ns.OWL.Thing)

      print dataset

      output.save()

# Used when Twistd invokes this service b/c it is sitting in a deployed directory.
resource = AddCKANMetadata()

# Used when this service is manually invoked from the command line (for testing).
#
# Usage: <input-rdf-file> [input-rdf-file-syntax] [output-rdf-file]
#
if __name__ == '__main__':

   if len(sys.argv) == 0:
      print resource.name + ' running on port ' + str(resource.dev_port) + '. Invoke it with:'
      print 'curl -H "Content-Type: text/turtle" -d @my.ttl http://localhost:' + str(resource.dev_port) + '/' + resource.name
      sadi.publishTwistedService(resource, port=resource.dev_port)

   else:
      reader= open(sys.argv[1],"r")
      mimeType = "application/rdf+xml"
      if len(sys.argv) > 2:
         mimeType = sys.argv[2]
      if len(sys.argv) > 3:
         writer = open(sys.argv[3],"w")

      graph = resource.processGraph(reader,mimeType)

      if len(sys.argv) > 3:
         writer.write(resource.serialize(graph,mimeType))
      else:
         print resource.serialize(graph,mimeType)
