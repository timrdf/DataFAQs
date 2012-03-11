#3> <> prov:specializationOf <https://raw.github.com/timrdf/DataFAQs/master/services/sadi/core/select-faqts/identity.rpy>;
#3>    rdfs:seeAlso <https://github.com/timrdf/DataFAQs/wiki/DataFAQs-Core-Services> .
#3>
#3> <http://sparql.tw.rpi.edu/services/datafaqs/core/select-faqts/identity>
#3>    a datafaqs:FAqTService .
#3> []
#3>    a prov:Activity;
#3>    prov:hadQualifiedAttribution [
#3>       a prov:Attribution;
#3>       prov:hadQualifiedEntity <http://sparql.tw.rpi.edu/services/datafaqs/core/select-faqts/identity>;
#3>       prov:adoptedPlan        <https://raw.github.com/timrdf/DataFAQs/master/services/sadi/core/select-faqts/identity.rpy>;
#3>    ];
#3> .
#3> <https://raw.github.com/timrdf/DataFAQs/master/services/sadi/core/select-faqts/identity.rpy>
#3>    foaf:homepage <https://github.com/timrdf/DataFAQs/blob/master/services/sadi/core/select-faqts/identity.rpy> .

import re
import sadi
from rdflib import *
import surf

from surf import *
from surf.query import select

# These are the namespaces we are using beyond those already available
# (see http://packages.python.org/SuRF/modules/namespace.html#registered-general-purpose-namespaces)
ns.register(datafaqs='http://purl.org/twc/vocab/datafaqs#')

# The Service itself
class IdentityFAqTService(sadi.Service):

   # Service metadata.
   label                  = 'identity'
   serviceDescriptionText = 'Return the FAqT services given.'
   comment                = ''
   serviceNameText        = 'identity' # Convention: Match 'name' below.
   name                   = 'identity' # This value determines the service URI relative to http://localhost:9090/
                                       # Convention: Use the name of this file for this value.
   def __init__(self): 
      sadi.Service.__init__(self)

   def getOrganization(self):
      result                      = self.Organization()
      result.mygrid_authoritative = True
      result.protegedc_creator    = 'lebot@rpi.edu'
      result.save()
      return result

   def annotateServiceDescription(self, desc):

      # Works fine.
      desc.rdfs_comment.append('in annotateServiceDescription')

      #desc.rdfs_seeAlso(URIRef('https://raw.github.com/timrdf/DataFAQs/master/services/sadi/core/select-faqts/identity.ttl'))
      #Thing = desc.session.get_class(ns.OWL['Thing'])
      Thing = self.getClass(ns.OWL['Thing'])
      #Thing = self.descriptionSession(ns.OWL['Thing'])
      wiki = Thing('https://raw.github.com/timrdf/DataFAQs/master/services/sadi/core/select-faqts/identity.ttl')
      wiki.save()

      #desc.foaf_isPrimaryTopicOf.append(wiki) # Adding this destroys 'desc' as a resource in the model.
      desc.save()

   def getInputClass(self):
      return ns.DATAFAQS['FAqTService']

   def getOutputClass(self):
      return ns.DATAFAQS['FAqTServiceCollection']

   def process(self, input, output):
  
      print input.subject

      #FAqTService = output.session.get_class(ns.DATAFAQS['FAqTService'])
      #faqt_service = output.session.get_resource(output.subject,ns.DATAFAQS['FAqTService']) #FAqTService(output.subject)
      #faqt_service.rdf_type.append(ns.DATAFAQS['FAqTService'])
      #faqt_service.save()

      output.rdf_type.append(ns.DATAFAQS['FAqTService'])
      output.dcterms_hasPart.append(output)

      output.save()

# Used when Twistd invokes this service b/c it is sitting in a deployed directory.
resource = IdentityFAqTService()

# Used when this service is manually invoked from the command line (for testing).
if __name__ == '__main__':
   port = 9105
   print 'curl -H "Content-Type: text/turtle" -d @my.ttl http://localhost:' + str(port) + '/' + resource.name
   sadi.publishTwistedService(resource, port=port)
