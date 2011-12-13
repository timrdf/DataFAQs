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

# These are the namespaces we are using beyond those already available
# (see http://packages.python.org/SuRF/modules/namespace.html#registered-general-purpose-namespaces)
ns.register(cif="http://purl.org/twc/ontology/cif.owl#")
ns.register(moat="http://moat-project.org/ns#")
ns.register(ov="http://open.vocab.org/terms/")
ns.register(datafaqs="http://purl.org/twc/vocab/datafaqs#")

THEDATAHUB = "http://thedatahub.org/dataset/"

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
        self.ckan = ckanclient.CkanClient(api_key='See https://github.com/timrdf/DataFAQs/wiki/Missing-CKAN-API-Key')

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

        output.save()

# Used when Twistd invokes this service b/c it is sitting in a deployed directory.
resource = TagCKANDataset()

# Used when this service is manually invoked from the command line (for testing).
# The service listens on port 9090
if __name__ == "__main__":
    sadi.publishTwistedService(resource, port=9090)
