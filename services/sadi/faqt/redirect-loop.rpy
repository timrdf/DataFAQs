import urllib
from urlparse import urlparse, urlunparse
import httplib
from surf import *
import sadi

# These are the namespaces we are using beyond those already available
# (see http://packages.python.org/SuRF/modules/namespace.html#registered-general-purpose-namespaces)
ns.register(moat='http://moat-project.org/ns#')
ns.register(ov='http://open.vocab.org/terms/')
ns.register(void='http://rdfs.org/ns/void#')
ns.register(conversion='http://purl.org/twc/vocab/conversion/')
ns.register(datafaqs='http://purl.org/twc/vocab/datafaqs#')

def getHEAD(url):
    # Ripped from https://github.com/timrdf/csv2rdf4lod-automation/blob/master/bin/util/pcurl.py
    o = urlparse(str(url))
    #print o
    connections = {'http' :httplib.HTTPConnection,
                   'https':httplib.HTTPSConnection}
    connection = connections[o.scheme](o.netloc)
    fullPath = urlunparse([None,None,o.path,o.params,o.query,o.fragment])
    connection.request('GET',fullPath)
    return connection.getresponse()

# The Service itself
# http://logd.tw.rpi.edu/test/redirect_loop_1_of_4 ---303---> http://logd.tw.rpi.edu/test/redirect_loop_2_of_4
# http://logd.tw.rpi.edu/test/redirect_loop_2_of_4 ---303---> http://logd.tw.rpi.edu/test/redirect_loop_3_of_4 
# http://logd.tw.rpi.edu/test/redirect_loop_3_of_4 ---303---> http://logd.tw.rpi.edu/test/redirect_loop_1_of_4
class RedirectLoop(sadi.Service):

   # Service metadata.
   label                  = 'redirect-loop'
   serviceDescriptionText = 'Returns unsatisfactory if the dataset URI resolves to a 303 redirect loop.'
   comment                = 'http://logd.tw.rpi.edu/test/redirect_loop_1_of_4 will fail this test.'
   serviceNameText        = 'redirect-loop' # Convention: Match 'name' below.
   name                   = 'redirect-loop' # This value determines the service URI relative to http://localhost:9090/
                                            # Convention: Use the name of this file for this value.
   def __init__(self): 
      sadi.Service.__init__(self)

   def getOrganization(self):
      result                      = self.Organization('http://tw.rpi.edu')
      result.mygrid_authoritative = True
      result.protegedc_creator    = 'lebot@rpi.edu'
      result.save()
      return result

   def getInputClass(self):
      return ns.VOID['Dataset']

   def getOutputClass(self):
      return ns.DATAFAQS['EvaluatedDataset']

   def process(self, input, output):

      next = input.subject
      history = set([next])
      head = getHEAD(next)
      while head.status >= 300 and head.status < 400:
         #print next + ' ' + str(head.status) + ' ' + head.msg.dict['location']
         next = head.msg.dict['location']
         if next in history:
            output.rdf_type.append(ns.DATAFAQS['Unsatisfactory'])
            del history
            break
         history.add(next)
         head = getHEAD(next)

      if ns.DATAFAQS['Unsatisfactory'] not in output.rdf_type:
         output.rdf_type.append(ns.DATAFAQS['Satisfactory'])
         
      output.rdf_type.append(ns.DATAFAQS['EvaluatedDataset'])
      output.save()

# Used when Twistd invokes this service b/c it is sitting in a deployed directory.
resource = RedirectLoop()

# Used when this service is manually invoked from the command line (for testing).
if __name__ == '__main__':
   sadi.publishTwistedService(resource, port=9093)
