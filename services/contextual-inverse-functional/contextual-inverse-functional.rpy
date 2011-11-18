import sadi
from rdflib import *
from surf import *

import rdflib
rdflib.plugin.register('sparql', rdflib.query.Processor,
                       'rdfextras.sparql.processor', 'Processor')
rdflib.plugin.register('sparql', rdflib.query.Result,
                       'rdfextras.sparql.query', 'SPARQLQueryResult')

# These are the namespaces we are using.  They need to be added in
# order for the Object RDF Mapping tool to work.
ns.register(cif="http://purl.org/twc/ontology/cif.owl#")

# The Service itself
class ContextualInverseFunctional(sadi.Service):

    # Service metadata.
    label                  = "my label"
    serviceDescriptionText = 'my description text'
    comment                = 'my commment'
    serviceNameText        = "my name text"
    name                   = "Contextual Inverse Functional"

    def __init__(self): 
        super(ContextualInverseFunctional,self).__init__()
        self.lodlinks = Store(  reader='rdflib',
                                writer='rdflib',
                                rdflib_store = 'IOMemory')
        store.load_triples(source='http://homepages.rpi.edu/~lebot/lod-links/state-fips-dbpedia.ttl')
        store.load_triples(source='http://homepages.rpi.edu/~lebot/lod-links/state-fips-geonames.ttl')
        store.load_triples(source='http://homepages.rpi.edu/~lebot/lod-links/state-fips-govtrack.ttl')

    def getOrganization(self):
        result                      = self.Organization("http://tw.rpi.edu")
        result.mygrid_authoritative = True
        result.protegedc_creator    = 'lebot@rpi.edu'
        result.save()
        return result

    # The service input class. ReferencedEntity is a class that has at
    # least one BioPAX xref. Note that here lbpx from the namespace
    # becomes LBPX when getting URIs back out.
    def getInputClass(self):
        return ns.CIF["IdentifiedResource"]

    # The service output class. These have 0 or more sameAs
    # assertions, but probably can have other things if it makes
    # sense.
    def getOutputClass(self):
        return ns.CIF["SameResource"]

    instanceQueryNamespace = dict(dcterms=str(ns.DCTERMS))

    instanceQuery = '''
select distinct ?instance where {
    ?instance dcterms:identifier ?id .
}
'''

    def getInstances(self, session, store, graph):
        InputClass = session.get_class(self.getInputClass())
        instances = graph.query(self.instanceQuery, 
                                initNs=self.instanceQueryNamespace)
        print len(instances)
        return [InputClass(i) for i in instances]

    sameAsQuery = '''
select distinct ?s where {
   ?s dcterms:identifier ?id .
}
'''

    def process(self, input, output):
        for ident in input.dcterms_identifier:
            output.owl_sameAs.extend( binding[0] for binding in self.lodlinks.graph.query(sameAsQuery, initNs=instanceQueryNamespace, 
                                                                                          initBindings={'?id' : input.dcterms_identifier} )

# For when Twistd invokes me.
resource = LinkedBioPAXService()

# For when I invoke myself from command line.
# Set up the service to listen on port 9090
if __name__ == "__main__":
    sadi.publishTwistedService(resource, port=9090)
