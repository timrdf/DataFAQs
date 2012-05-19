#3> <> prov:specializationOf <https://raw.github.com/timrdf/DataFAQs/master/packages/faqt.python/faqt/faqt.py> .
#3>
#3> <https://raw.github.com/timrdf/DataFAQs/master/packages/faqt.python/faqt/faqt.py>
#3>    foaf:homepage <https://github.com/timrdf/DataFAQs/blob/master/packages/faqt.python/faqt/faqt.py> .

import sadi
from rdflib import *
import surf

from surf import *
from surf.query import select

import rdflib
from rdflib.namespace import XSD
rdflib.plugin.register('sparql', rdflib.query.Processor,
                       'rdfextras.sparql.processor', 'Processor')
rdflib.plugin.register('sparql', rdflib.query.Result,
                       'rdfextras.sparql.query', 'SPARQLQueryResult')

import datetime
import os
import uuid

ns.register(moat='http://moat-project.org/ns#')
ns.register(ov='http://open.vocab.org/terms/')
ns.register(void='http://rdfs.org/ns/void#')
ns.register(dcat='http://www.w3.org/ns/dcat#')
ns.register(sd='http://www.w3.org/ns/sparql-service-description#')
ns.register(prov='http://www.w3.org/ns/prov#')
ns.register(conversion='http://purl.org/twc/vocab/conversion/')
ns.register(datafaqs='http://purl.org/twc/vocab/datafaqs#')

class Service(sadi.Service):

   # Shell environment variables override these.
   baseURI        = None # e.g. http://aquarius.tw.rpi.edu/projects/datafaqs
   CODE_PAGE_BASE = None # e.g. https://github.com/timrdf/DataFAQs/blob/master
   CODE_RAW_BASE  = None # e.g. https://raw.github.com/timrdf/DataFAQs/master

   # Passed in by any class extending this class.
                      #      http://aquarius.tw.rpi.edu/projects/datafaqs
                      #                                                  /
   servicePath = None # e.g.                                              services/sadi/faqt/connected
                      #                                                                               /void-linkset

   uuid          = None
   startedLifeAt = None

   def __init__(self, servicePath): 
      sadi.Service.__init__(self)

      self.servicePath    = servicePath # No ending slash

      self.uuid           = uuid.uuid()
      self.startedLifeAt  = datetime.datetime.utcnow()

      self.baseURI        = os.environ['DATAFAQS_BASE_URI']                  if 'DATAFAQS_BASE_URI'                  in os.environ \
                                                                             else None
      self.CODE_RAW_BASE  = os.environ['DATAFAQS_PROVENANCE_CODE_RAW_BASE']  if 'DATAFAQS_PROVENANCE_CODE_RAW_BASE'  in os.environ \
                                                                             else 'https://github.com/timrdf/DataFAQs/blob/master'
      self.CODE_PAGE_BASE = os.environ['DATAFAQS_PROVENANCE_CODE_PAGE_BASE'] if 'DATAFAQS_PROVENANCE_CODE_PAGE_BASE' in os.environ \
                                                                             else 'https://raw.github.com/timrdf/DataFAQs/master'
   def annotateServiceDescription(self, desc):

      #3> <#TEMPLATE/path/to/where/source-code.rpy/is/deployed/for/invocation>
      #3>    a datafaqs:FAqTService .
      #3> []
      #3>    a prov:Activity;
      #3>    prov:qualifiedAttribution [
      #3>       a prov:Attribution;
      #3>       prov:agent   <#TEMPLATE/path/to/where/source-code.rpy/is/deployed/for/invocation>;
      #3>       prov:hadPlan <#TEMPLATE/path/to/public/source-code.rpy>;
      #3>    ];
      #3> .
      #3> <#TEMPLATE/path/to/public/source-code.rpy>
      #3>    a prov:Plan;
      #3>    foaf:homepage <#TEMPLATE/path/to/public/HOMEPAGE-FOR/source-code.rpy>;
      #3>    rdfs:seeAlso <https://github.com/timrdf/DataFAQs/wiki/FAqT-Service> .

      Thing       = desc.session.get_class(ns.OWL['Thing'])
      Activity    = desc.session.get_class(ns.PROV['Activity'])
      Attribution = desc.session.get_class(ns.PROV['Attribution'])
      Agent       = desc.session.get_class(ns.PROV['Agent'])
      FAqTService = desc.session.get_class(ns.DATAFAQS['FAqTService'])
      Plan        = desc.session.get_class(ns.PROV['Plan'])
      Entity      = desc.session.get_class(ns.PROV['Entity'])
      Page        = desc.session.get_class(ns.FOAF['Page'])

      desc.dcterms_subject.append(Agent(''))
      desc.datafaqs_x_baseURI.append(str(self.baseURI))
      desc.datafaqs_x_raw.append(str(self.CODE_RAW_BASE))
      desc.datafaqs_x_page.append(str(self.CODE_PAGE_BASE))

      agent = None
      if self.baseURI     is not None and self.baseURI     != '' and \
         self.servicePath is not None and self.servicePath != '' and \
         self.serviceNameText != '':
         # If we can figure out the URI for this service, talk about it.
         agent = Agent(self.baseURI +'/datafaqs/'+ self.servicePath +'/'+ self.serviceNameText)
         agent.prov_generatedAtTime.append(self.startedLifeAt);
         agent.rdf_type.append(ns.DATAFAQS['FAqTService'])
         agent.rdf_type.append(ns.PROV['Agent'])
         agent.rdf_type.append(ns.FOAF['Agent'])
         agent.rdfs_seeAlso.append(Thing('https://github.com/timrdf/DataFAQs/wiki/FAqT-Service'))
      else:
         # Otherwise, we can only point to it (and not describe it) because of a SuRF/rdflib error.
         agent = FAqTService('')
      agent.save()

      plan = None
      if self.servicePath is not None:
         # servicePath is passed in by any class extending faqt.python
         plan = Plan(                    self.CODE_RAW_BASE  +'/'+ self.servicePath +'/'+ self.serviceNameText + '.py')
         plan.foaf_homepage.append(Thing(self.CODE_PAGE_BASE +'/'+ self.servicePath +'/'+ self.serviceNameText + '.py'))
         plan.save()

      attribution = Attribution('#'+self.uuid+'-activity')
      attribution.prov_agent   = agent
      if plan is not None:
         attribution.prov_hadPlan = plan
      attribution.save()

      activity = Activity('#'+self.uuid+'-activity')
      if self.startedLifeAt is not None:
         activity.prov_startedAtTime.append(self.startedLifeAt)
      activity.prov_qualifiedAttribution.append(attribution)
      activity.save()

      desc.save()
