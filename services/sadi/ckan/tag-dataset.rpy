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
import subprocess

import httplib
from urlparse import urlparse, urlunparse
import urllib
connections = {'http':httplib.HTTPConnection,
               'https':httplib.HTTPSConnection}

# These are the namespaces we are using beyond those already available
# (see http://packages.python.org/SuRF/modules/namespace.html#registered-general-purpose-namespaces)
ns.register(cif="http://purl.org/twc/ontology/cif.owl#")
ns.register(moat="http://moat-project.org/ns#")
ns.register(ov="http://open.vocab.org/terms/")
ns.register(datafaqs="http://purl.org/twc/vocab/datafaqs#")
ns.register(void="http://rdfs.org/ns/void#")

THEDATAHUB = "http://thedatahub.org/dataset/"

def getResponse(url):
    # Ripped from https://github.com/timrdf/csv2rdf4lod-automation/blob/master/bin/util/pcurl.py
    o = urlparse(str(url))
    #print o
    connection = connections[o.scheme](o.netloc)
    fullPath = urlunparse([None,None,o.path,o.params,o.query,o.fragment])
    connection.request('GET',fullPath)
    return connection.getresponse()

def call(command):
    # Ripped from https://github.com/timrdf/csv2rdf4lod-automation/blob/master/bin/util/pcurl.py
    p = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result = p.communicate()
    return result

# The Service itself
class TagCKANDataset(sadi.Service):

    # Service metadata.
    label                  = "Tag CKAN Dataset"
    serviceDescriptionText = 'Modifies a CKAN dataset listing based on the MOAT tags given.'
    comment                = 'my commment'
    serviceNameText        = "TagCKANDataset"
    name                   = "TagCKANDataset" # This value determines the service URI relative to http://localhost:9090/

    def __init__(self): 
        sadi.Service.__init__(self)
        
        # Instantiate the CKAN client.
        # http://docs.python.org/library/configparser.html (could use this technique)
        key = call('echo $DATAFAQS_CKAN_API_KEY')[0]
        if len(key) <= 1:
            print "ERROR: https://github.com/timrdf/DataFAQs/wiki/Missing-CKAN-API-Key"
            sys.exit(1)
        self.ckan = ckanclient.CkanClient(api_key=key)

    def getOrganization(self):
        result                      = self.Organization("http://tw.rpi.edu")
        result.mygrid_authoritative = True
        result.protegedc_creator    = 'lebot@rpi.edu'
        result.save()
        return result

    def getInputClass(self):
        return ns.DATAFAQS["TaggedCKANDataset"]

    def getOutputClass(self):
        return ns.DATAFAQS["ModifiedCKANDataset"]

    def process(self, input, output):
        ckan_id = input.dcterms_identifier.first
        print "processing " + input.subject + " ckan_id " + ckan_id
      
        # GET the current dataset metadata listing from CKAN.
        self.ckan.package_entity_get(ckan_id)
        dataset = self.ckan.last_message

        # Add the tags to the dataset.
        for tag_uri in input.moat_taggedWithTag:
            if tag_uri.startswith("http://lod-cloud.net/tag/"):
                tag = tag_uri.replace("http://lod-cloud.net/tag/","")
                dataset['tags'].append(tag)

        # POST the new details of the dataset.
        self.ckan.package_entity_put(dataset)

        # GET the timestamp of the change we just submitted.
        self.ckan.package_entity_get(input.dcterms_identifier.first)
        dataset = self.ckan.last_message
        output.dcterms_modified = dataset['metadata_modified']
        output.rdfs_seeAlso = output.session.get_resource(THEDATAHUB + ckan_id, ns.OWL.Thing)

        # http://prefix.cc/?q=http://www.w3.org/2003/01/geo/wgs84_pos 
        # 302s to http://prefix.cc/geo
        for vocab in input.void_vocabulary:
            print vocab
            response = getResponse("http://prefix.cc/?" + urllib.urlencode({'q':vocab}))
            if response.status == 302:
                prefix_tag = "format-" + response.msg.dict['location'].replace("http://prefix.cc/","")
                print str(response.status) + " " + response.msg.dict['location'] + " " + prefix_tag

            #params = urllib.urlencode({'q': vocab})
            #f = urllib.urlopen("http://prefix.cc/?%s" % params)
            #print f #f.read()

        output.save()

# Used when Twistd invokes this service b/c it is sitting in a deployed directory.
resource = TagCKANDataset()

# Used when this service is manually invoked from the command line (for testing).
# The service listens on port 9090
if __name__ == "__main__":
    sadi.publishTwistedService(resource, port=9090)
