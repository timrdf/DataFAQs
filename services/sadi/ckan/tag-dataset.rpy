import sadi
from rdflib import *
from surf import *
from surf.query import select

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
ns.register(cif='http://purl.org/twc/ontology/cif.owl#')
ns.register(moat='http://moat-project.org/ns#')
ns.register(ov='http://open.vocab.org/terms/')
ns.register(datafaqs='http://purl.org/twc/vocab/datafaqs#')
ns.register(void='http://rdfs.org/ns/void#')

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
class TagCKANDataset(sadi.Service):

    # Service metadata.
    label                  = 'Tag CKAN Dataset'
    serviceDescriptionText = 'Modifies a CKAN dataset listing based on the MOAT tags given.'
    comment                = 'my commment'
    serviceNameText        = 'TagCKANDataset'
    name                   = 'TagCKANDataset' # This value determines the service URI relative to http://localhost:9090/

    def __init__(self): 
        sadi.Service.__init__(self)
        
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
        return ns.DATAFAQS['TaggedCKANDataset']

    def getOutputClass(self):
        return ns.DATAFAQS['ModifiedCKANDataset']

    def process(self, input, output):
        ckan_id = input.dcterms_identifier.first
        print 'processing ' + input.subject + ' ckan_id ' + ckan_id
      
        # GET the current dataset metadata listing from CKAN.
        self.ckan.package_entity_get(ckan_id)
        dataset = self.ckan.last_message

        # Core: author
        #for author in input.dcterms_author:
        #   dataset['author'].append(author)
        #   dataset['author_email'].append(author)

        # Core: groups
        # ?d dc:isPartOf <http://ckan.net/group/datafaqs> . <http://ckan.net/group/datafaqs> a datafaqs:CKANGroup .
        #for ckan_group in input.dcterms_isPartOf:
        #   if ns.DATAFAQS['CKANGroup'] in ckan_group.rdf_type and \
        #      str(ckan_group) != 'http://ckan.net/group/lodcloud':
        #      dataset['groups'].append(ckan_group.replace('http://ckan.net/group/','')

        # Extra: shortName
        if input.ov_shortName:
           dataset['extras']['shortname'] = input.ov_shortName.first

        # Extra: namespace
        if input.datafaqs_namespace:
           dataset['extras']['namespace'] = input.datafaqs_namespace.first

        # Extra: triples
        if input.void_triples:
           dataset['extras']['triples'] = input.void_triples.first

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
        # Extra: link:*
        results = input.session.default_store.execute_sparql(linksQuery)
        for bindings in results['results']['bindings']:
            otherbubble = str(bindings['otherbubble']['value'])
            if otherbubble != str(input.subject): # TODO: why is input.subject appearing?
               attribute = 'links:' + otherbubble.replace('http://thedatahub.org/dataset/','')
               print attribute + ' = ' + bindings['triples']['value']
               dataset['extras'][attribute] = bindings['triples']['value']

        # Tags
        for tag_uri in input.moat_taggedWithTag:
            if tag_uri.startswith('http://ckan.net/tag/') or \
               tag_uri.startswith('http://lod-cloud.net/tag/'):
                tag = tag_uri.replace('http://ckan.net/tag/','') \
                             .replace('http://lod-cloud.net/tag/','')
                dataset['tags'].append(tag)

        # Tags: format-*
#        for vocab in input.void_vocabulary:
#            # http://prefix.cc/?q=http://www.w3.org/2003/01/geo/wgs84_pos 
#            # 302s to http://prefix.cc/geo
#            response = getResponse('http://prefix.cc/?' + urllib.urlencode({'q':vocab}))
#            if response.status == 302:
#                prefix_tag = 'format-' + response.msg.dict['location'].replace('http://prefix.cc/','')
#                print str(response.status) + ' ' + vocab + ' ' + response.msg.dict['location'] + ' ' + prefix_tag
#                dataset['tags'].append(prefix_tag)
#            else:
#                print str(response.status) + ' ' + vocab

        # POST the new details of the dataset.
        self.ckan.package_entity_put(dataset)

        # GET the timestamp of the change we just submitted.
        self.ckan.package_entity_get(input.dcterms_identifier.first)
        dataset = self.ckan.last_message
        output.dcterms_modified = dataset['metadata_modified']
        output.rdfs_seeAlso = output.session.get_resource(THEDATAHUB + ckan_id, ns.OWL.Thing)

        output.save()

# Used when Twistd invokes this service b/c it is sitting in a deployed directory.
resource = TagCKANDataset()

# Used when this service is manually invoked from the command line (for testing).
# The service listens on port 9090
if __name__ == '__main__':
    sadi.publishTwistedService(resource, port=9090)
