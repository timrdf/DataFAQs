import sadi
from rdflib import *
import surf

from surf import *
from surf.query import select

import rdflib
rdflib.plugin.register('sparql', rdflib.query.Processor,
                       'rdfextras.sparql.processor', 'Processor')
rdflib.plugin.register('sparql', rdflib.query.Result,
                       'rdfextras.sparql.query', 'SPARQLQueryResult')

ns.register(moat='http://moat-project.org/ns#')
ns.register(ov='http://open.vocab.org/terms/')
ns.register(void='http://rdfs.org/ns/void#')
ns.register(dcat='http://www.w3.org/ns/dcat#')
ns.register(sd='http://www.w3.org/ns/sparql-service-description#')
ns.register(prov='http://www.w3.org/ns/prov#')
ns.register(conversion='http://purl.org/twc/vocab/conversion/')
ns.register(datafaqs='http://purl.org/twc/vocab/datafaqs#')

class Service(sadi.Service):

   CODE_PAGE_BASE = 'https://github.com/timrdf/DataFAQs/blob/master/services/sadi/faqt/datascape/'
   CODE_RAW_BASE  = 'https://raw.github.com/timrdf/DataFAQs/master/services/sadi/faqt/datascape/'

   startedLifeAt = 'TODO' #None

   def __init__(self): 
      sadi.Service.__init__(self)

   def annotateServiceDescription(self, desc):
      Thing       = desc.session.get_class(ns.OWL['Thing'])
      Attribution = desc.session.get_class(ns.PROV['Attribution'])
      Entity      = desc.session.get_class(ns.PROV['Entity'])
      Plan        = desc.session.get_class(ns.PROV['Plan'])
      Agent       = desc.session.get_class(ns.PROV['Agent'])
      Page        = desc.session.get_class(ns.FOAF['Page'])
      plan = Plan(self.CODE_PAGE_BASE + self.serviceNameText + '.py')
      plan.foaf_homepage.append(Thing(self.CODE_PAGE_BASE + self.serviceNameText + '.py'))
      plan.save()
      agent = Agent('#')
      #agent.rdf_type.append(ns.DATAFAQS['FAqTService'])
      agent.save()
      attr = Attribution()
      attr.prov_agent   = agent
      attr.prov_hadPlan = plan
      attr.dcterms_date.append(str(self.startedLifeAt))
      attr.save()
      desc.dcterms_subject.append(Agent(''))
      desc.save()
