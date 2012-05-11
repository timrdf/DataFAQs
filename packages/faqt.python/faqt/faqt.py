import sadi

class Service(sadi.Service):

   def __init__(self, param):
      super(sadi.Service, self).__init__(param)
      print "faqt.Serivce::", param

   startedLifeAt = 'TODO' #None

   def annotateServiceDescription(self, desc):
      print 'annotate ' + desc.subject
      Thing       = desc.session.get_class(ns.OWL['Thing'])
      Attribution = desc.session.get_class(ns.PROV['Attribution'])
      Entity      = desc.session.get_class(ns.PROV['Entity'])
      Plan        = desc.session.get_class(ns.PROV['Plan'])
      Agent       = desc.session.get_class(ns.PROV['Agent'])
      Page        = desc.session.get_class(ns.FOAF['Page'])
      plan = Plan(self.rawBase + self.serviceNameText)
      plan.foaf_homepage.append(Thing(self.pageBase + self.serviceNameText))
      plan.save()
      attr = Attribution()
      attr.prov_entity  = Agent('') 
      attr.prov_hadPlan = plan
      attr.dcterms_date.append(str(self.startedLifeAt))
      attr.save()
      desc.dcterms_subject.append(Agent(''))
      desc.save()
