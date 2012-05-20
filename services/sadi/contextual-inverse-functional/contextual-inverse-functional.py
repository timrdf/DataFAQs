#3> <> prov:specializationOf <https://github.com/timrdf/DataFAQs/raw/master/services/sadi/contextual-inverse-functional/contextual-inverse-functional.py>;
#3>    rdfs:seeAlso <https://github.com/timrdf/DataFAQs/wiki/FAqT-Service> .

import faqt

import sadi
from rdflib import *
from surf import *
from surf.query import select

import rdflib
rdflib.plugin.register('sparql', rdflib.query.Processor,
                       'rdfextras.sparql.processor', 'Processor')
rdflib.plugin.register('sparql', rdflib.query.Result,
                       'rdfextras.sparql.query', 'SPARQLQueryResult')

# These are the namespaces we are using.  They need to be added in
# order for the Object RDF Mapping tool to work.
ns.register(cif="http://purl.org/twc/ontology/cif.owl#")

# The Service itself
class ContextualInverseFunctional(faqt.Service):

    # Service metadata.
    label                  = "my label"
    serviceDescriptionText = 'my description text'
    comment                = 'my commment'
    serviceNameText        = "my name text"
    name                   = "ContextualInverseFunctional"

   def __init__(self):
        faqt.Service.__init__(self, servicePath = 'services/sadi/contextual-inverse-functional')
        
        #self.lodlinks = Graph()
        #self.lodlinks.parse('http://homepages.rpi.edu/~lebot/lod-links/state-fips-dbpedia.ttl', format="n3")
        #self.lodlinks.parse('http://homepages.rpi.edu/~lebot/lod-links/state-fips-geonames.ttl', format="n3")
        #self.lodlinks.parse('http://homepages.rpi.edu/~lebot/lod-links/state-fips-govtrack.ttl', format="n3")
        self.logd = Store(  reader          =   "sparql_protocol",
                            writer          =   "sparql_protocol",
                            endpoint        =   "http://logd.tw.rpi.edu:8890/sparql")

    def getOrganization(self):
        result                      = self.Organization("http://tw.rpi.edu")
        result.mygrid_authoritative = True
        result.protegedc_creator    = 'lebot@rpi.edu'
        result.save()
        return result

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
        print input.subject
        for ident in input.dcterms_identifier:
            query = select("?s").where(("?s", ns.DCTERMS["identifier"], ident))
            results = self.logd.execute(query)
            same = [URIRef(x['s']['value']) for x in results['results']['bindings']]
            output.owl_sameAs.extend(same)
        #   output.owl_sameAs.extend( self.logd.execute(query) )
        #   output.owl_sameAs.extend( self.lodlinks.query(self.sameAsQuery, initNs=self.instanceQueryNamespace, 
        #                                                 initBindings={'id' : ident}) )
        output.save()

# For when Twistd invokes me.
resource = ContextualInverseFunctional()

# For when I invoke myself from command line.
# Set up the service to listen on port 9090
if __name__ == "__main__":
    sadi.publishTwistedService(resource, port=9090)
