#3> <> prov:specializationOf <https://github.com/timrdf/DataFAQs/raw/master/services/sadi/ckan/add-metadata.py>;
#3>    rdfs:seeAlso <https://github.com/timrdf/DataFAQs/wiki/FAqT-Service> .

import faqt

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

THEDATAHUB = 'http://thedatahub.org/dataset/'

def getResponse(url):
   # Ripped from https://github.com/timrdf/csv2rdf4lod-automation/blob/master/bin/util/pcurl.py
   o = urlparse(str(url))
   #print o
   connection = connections[o.scheme](o.netloc)
   fullPath = urlunparse([None,None,o.path,o.params,o.query,o.fragment])
   connection.request('GET',fullPath)
   return connection.getresponse()

# The Service itself
class AddCKANMetadata(faqt.Service):

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
      # http://docs.python.org/library/configparser.html (could use this technique)
      key = os.environ['X_CKAN_API_Key']
      if len(key) <= 1:
          print 'ERROR: https://github.com/timrdf/DataFAQs/wiki/Missing-CKAN-API-Key'
          sys.exit(1)
      self.ckan = ckanclient.CkanClient(api_key=key)

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

      ckan_id = None
      if len(input.datafaqs_ckan_identifier) > 0:
         ckan_id = input.datafaqs_ckan_identifier.first
      elif len(input.dcterms_identifier) > 0:
         ckan_id = input.dcterms_identifier.first
      elif re.match('^.*/dataset/',input.subject):
         ckan_id = re.replace('^.*/dataset/','',str(input.subject))
      else:
         print 'Error: cannot determine what dataset to create/modify'
         return
      print 'ckan_id ' + ckan_id
     
      #
      # GET the current dataset metadata listing from CKAN.
      dataset = {}
      try:
         self.ckan.package_entity_get(ckan_id)
         dataset = self.ckan.last_message
      except ckanclient.CkanApiNotFoundError:
         # If we want to play it safe - only modify existing datasets.
         #output.rdf_type.append(ns.DATAFAQS['NotCKANDataset'])
         #output.save()
         #return

         print 'CKAN dataset id does not exist; registering it on CKAN.' 
         # Register the dataset
         package_entity = { 'name': ckan_id }
         self.ckan.package_register_post(package_entity)

         # GET the new dataset metadata listing from CKAN.
         self.ckan.package_entity_get(ckan_id)
         dataset = self.ckan.last_message
      #print dataset

      #
      # dcterms:title ?title
      if len(input.dcterms_title) > 0:
         dataset['title'] = input.dcterms_title.first

      #
      # dcterms:description ?description
      if len(input.dcterms_description) > 0:
         dataset['notes'] = input.dcterms_description.first

      #
      # Core: author
      query = select("?name ?mbox").where((input.subject, ns.DCTERMS['creator'], "?creator"),
                                          ("?creator",    ns.FOAF['mbox'],       "?mbox"),
                                          ("?creator",    ns.FOAF['name'],       "?name"))
      for bindings in input.session.default_store.execute(query):
         #print 'creator: ' + bindings[0] + ' ' + bindings[1]
         dataset['author']       = re.sub('^mailto:','',bindings[0])
         dataset['author_email'] = re.sub('^mailto:','',bindings[1])

      #
      # Core: maintainer
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
      for binding in results:
         ckan_group = binding[0] # e.g. http://thedatahub.org/group/arrayexpress
         ckan_group_id = re.sub('http.*/group/','',str(ckan_group))
         if ckan_group_id != 'lodcloud': # Prevent spamming of the manually curated set.
            dataset['groups'].append(ckan_group_id) 

      # Extra: shortName
      if input.ov_shortName:
         dataset['extras']['shortname'] = input.ov_shortName.first

      # Extra: namespace
      if input.datafaqs_namespace:
         dataset['extras']['namespace'] = input.datafaqs_namespace.first

      # Extra: triples
      if input.void_triples:
         dataset['extras']['triples'] = input.void_triples.first

      # Extra: preferred_uri
      if input.con_preferredURI:
          dataset['extras']['preferred_uri'] = input.con_preferredURI.first

      linksQuery = '''
prefix void: <http://rdfs.org/ns/void#>
select distinct ?otherbubble ?triples 
where { 
   <''' + input.subject + '''>
     void:subset [
       a void:Linkset;
       void:target  <''' + input.subject + '''>,
                    ?otherbubble;
       void:triples ?triples;
     ] .
   filter(regex(str(?otherbubble),'^http://thedatahub.org/dataset/'))
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
    
      # Tags
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
      dataset_resources = {}
      for resource in dataset['resources']:
         print 'indexing ' + resource['url']
         dataset_resources[URIRef(resource['url'])] = resource

      #
      # SPARQL Endpoint (two ways)
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

      if sparqlEndpoint not in dataset_resources:
         # Resource with this URL did not exist.
         print 'brand new ' + sparqlEndpoint
         dataset['resources'].append( { 'name':   'SPARQL Endpoint',
                                        'url':    sparqlEndpoint, 
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
                                           'url':    vocab, 
                                           'format': 'meta/rdf-schema' } )

      # POST the new details of the dataset.
      self.ckan.package_entity_put(dataset)

      # GET the timestamp of the change we just submitted.
      self.ckan.package_entity_get(ckan_id)
      dataset = self.ckan.last_message
      output.dcterms_modified = dataset['metadata_modified']
      output.rdfs_seeAlso = output.session.get_resource(THEDATAHUB + ckan_id, ns.OWL.Thing)

      output.save()

# Used when Twistd invokes this service b/c it is sitting in a deployed directory.
resource = AddCKANMetadata()

# Used when this service is manually invoked from the command line (for testing).
# The service listens on port 9090
#if __name__ == '__main__':
#    sadi.publishTwistedService(resource, port=9090)

# Used when this service is manually invoked from the command line (for testing).
if __name__ == '__main__':
   print resource.name + ' running on port ' + str(resource.dev_port) + '. Invoke it with:'
   print 'curl -H "Content-Type: text/turtle" -d @my.ttl http://localhost:' + str(resource.dev_port) + '/' + resource.name
   sadi.publishTwistedService(resource, port=resource.dev_port)
