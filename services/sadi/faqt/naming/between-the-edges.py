#3> <> prov:specializationOf <https://github.com/timrdf/DataFAQs/blob/master/services/sadi/faqt/naming/between-the-edges.py>;
#3>    rdfs:seeAlso <https://github.com/timrdf/DataFAQs/wiki/FAqT-Service> .

import faqt

import sadi
from rdflib import *
import surf

from surf import *
from surf.query import a, select

import rdflib
rdflib.plugin.register('sparql', rdflib.query.Processor,
                       'rdfextras.sparql.processor', 'Processor')
rdflib.plugin.register('sparql', rdflib.query.Result,
                       'rdfextras.sparql.query', 'SPARQLQueryResult')

import httplib
from urlparse import urlparse, urlunparse
import urllib
import urllib2

# These are the namespaces we are using beyond those already available
# (see http://packages.python.org/SuRF/modules/namespace.html#registered-general-purpose-namespaces)
ns.register(moat='http://moat-project.org/ns#')
ns.register(ov='http://open.vocab.org/terms/')
ns.register(void='http://rdfs.org/ns/void#')
ns.register(dcat='http://www.w3.org/ns/dcat#')
ns.register(sd='http://www.w3.org/ns/sparql-service-description#')
ns.register(conversion='http://purl.org/twc/vocab/conversion/')
ns.register(datafaqs='http://purl.org/twc/vocab/datafaqs#')
ns.register(bte='http://purl.org/twc/vocab/between-the-edges/')

# The Service itself
class BetweenTheEdges(faqt.Service):

   # Service metadata.
   label                  = 'between-the-edges'
   serviceDescriptionText = 'Annotate any rdfs:Resource URI with an RDF description of the URI itself.'
   comment                = 'see https://github.com/timrdf/vsr/wiki/Characterizing-a-list-of-RDF-node-URIs'
   serviceNameText        = 'between-the-edges' # Convention: Match 'name' below.
   name                   = 'between-the-edges' # This value determines the service URI relative to http://localhost:9090/
                                                # Convention: Use the name of this file for this value.
   dev_port = 9235

   def __init__(self):
      # DATAFAQS_PROVENANCE_CODE_RAW_BASE                   +  servicePath  +  '/'  + self.serviceNameText
      # DATAFAQS_PROVENANCE_CODE_PAGE_BASE                  +  servicePath  +  '/'  + self.serviceNameText
      #
      # ^^ The source code location
      #    aligns with the deployment location \/
      #
      #                 DATAFAQS_BASE_URI  +  '/datafaqs/'  +  servicePath  +  '/'  + self.serviceNameText
      faqt.Service.__init__(self, servicePath = 'services/sadi/faqt/naming')
                                                                 # Use: pwd | sed 's/^.*services/services/'
   def getOrganization(self):
      result                      = self.Organization()
      result.mygrid_authoritative = True
      result.protegedc_creator    = 'lebot@rpi.edu'
      result.save()
      return result

   def getInputClass(self):
      return ns.RDFS['Resource']

   def getOutputClass(self):
      return ns.BTE['RDFNode']

   @staticmethod
   def length(input,output):
      output.bte_length = len(input.subject)
      return len(input.subject)

   @staticmethod
   def scheme(url6,output):
      if len(url6.scheme):
         output.bte_scheme = url6.scheme
         return url6.scheme
      
   @staticmethod
   def netloc(url6,output):
      if len(url6.netloc):
         output.bte_netloc = url6.netloc
         return url6.netloc
 
   @staticmethod
   def path(url6,output):
      if len(url6.path):
         output.bte_path = url6.path
         return url6.path
      
   @staticmethod
   def fragment(url6,output):
      if len(url6.fragment):
         output.bte_fragment = url6.fragment
         return url6.fragment

   @staticmethod
   def extension(path,output):
      # /healthworkforce/default.htm -> .htm
      # /Blast.cgi                   -> .cgi
      match = re.search('.*(\.....)$',path)
      if match:
         output.bte_extension = match.group(1)
         output.save()
         return match.group(1)
      else:
         match = re.search('.*(\....)$',path)
         if match:
            output.bte_extension = match.group(1)
            output.save()
            return match.group(1)
         else:
            match = re.search('.*(\...)$',path)
            if match:
               output.bte_extension = match.group(1)
               output.save()
               return match.group(1)
      
   @staticmethod
   def walkPath(base,urlpath,output):

      print >> sys.stderr, '   walking: "' + urlpath + '"'

      Node = output.session.get_class(ns.BTE['Node'])

      # "/twc/"               -> "/twc"
      # "/ftp/hsp/TANF-data/" -> "/ftp/hsp/TANF-data"
      if re.match('.*/$',urlpath):
         # ^ This should only occur when first called by #process(),
         # since walkPath does not include a trailing slash its 
         # recursive calls.
         trimmed_path = re.sub('/$','',urlpath)
         broader = output.session.get_resource(base+trimmed_path,Node)
         broader.rdf_type.append(ns.BTE['Node'])
         broader.save()
         output.bte_broader = broader
         return 1 + BetweenTheEdges.walkPath(base, trimmed_path, output)

      me = output.session.get_resource(base+urlpath,Node) # TODO: does a get_resource replace the previous one?
      me.rdf_type.append(ns.BTE['Node'])

      # e.g.
      #     "http://dailymed.nlm.nih.gov/dailymed/help.cfm"
      #     "http://healthit.hhs.gov/portal/server.pt"
      #
      extension = BetweenTheEdges.extension(urlpath,me) # TODO: This is not asserting the triple.
      if extension is not None:
         print >> sys.stderr, '              '+re.sub('.',' ',urlpath) + extension
         me.bte_extension = extension
         me.save()

      # e.g.
      #      "/"
      #      "/id/agency/cdc"
      #
      match = re.search("^(.*)/([^/]+)$",urlpath)
      if match:
         trimmed_path = match.group(1)
         step         = match.group(2)
         print >> sys.stderr, '             ' + urlpath + ' -> "' + trimmed_path + '" + / + ' + step
         me.bte_step = step

         broader = output.session.get_resource(base+trimmed_path,Node)
         broader.rdf_type.append(ns.BTE['Node'])
         broader.save()

         me.bte_broader = broader
         depth = 1 + BetweenTheEdges.walkPath(base, trimmed_path, output)
         me.bte_depth = depth
         me.save()
         return depth
      else:
         print >> sys.stderr, '           ' + base + ' + "' + urlpath + '" is root. ' + me.subject
         me.bte_depth = 0
         me.save()
         return 0

   def process(self, input, output):

      print >> sys.stderr, 'processing ' + input.subject

      length = BetweenTheEdges.length(input,output)

      if re.match('.*/$',input.subject):
         output.rdf_type.append(ns.BTE['SlashEndURI'])
      elif re.match('.*#$',input.subject):
         output.rdf_type.append(ns.BTE['HashEndURI'])

      #
      # Using urlparse - http://docs.python.org/2/library/urlparse.html
      # e.g. ParseResult(scheme='http', netloc='www.cwi.nl:80', path='/%7Eguido/Python.html', params='', query='', fragment='')
      #
      url6 = urlparse(str(input.subject))
      scheme   = BetweenTheEdges.scheme(url6,output)
      netloc   = BetweenTheEdges.netloc(url6,output)
      path     = BetweenTheEdges.path(url6,output)
      fragment = BetweenTheEdges.fragment(url6,output)

      # <http://dailymed.nlm.nih.gov/dailymed/help.cfm#webservices> 
      #    a bte:RDFNode;
      #    bte:scheme "http";
      #    bte:netloc      "dailymed.nlm.nih.gov";
      #    bte:path                             "/dailymed/help.cfm";
      #    bte:fragment                                            "webservices";
      #    bte:length                                                         57;

      if scheme in ['http'] and path is not None:
         pathDepth = BetweenTheEdges.walkPath(scheme+'://'+netloc , path, output)
         fragDepth = 1 if fragment is not None and len(fragment) else 0
         # <http://bioportal.bioontology.org/>                         depth 1 ('' after the slash)
         # <http://aidsinfo.nih.gov/api>                               depth 1
         # <http://bhpr.hrsa.gov/healthworkforce/default.htm>          depth 2
         # <http://bioportal.bioontology.org/ontologies/umls/>         depth 3 ('' after the slash)
         # <http://bioportal.bioontology.org/ontologies/umls/cui>      depth 3
         # <http://dailymed.nlm.nih.gov/dailymed/help.cfm#webservices> depth 3 (fragID adds one)
         # <http://aspe.hhs.gov/ftp/hsp/TANF-data/>                    depth 4 ('' after the slash)
         output.bte_depth = pathDepth + fragDepth

      output.rdf_type.append(ns.BTE['RDFNode'])
      output.save()

# Used when Twistd invokes this service b/c it is sitting in a deployed directory.
resource = BetweenTheEdges()

# Used when this service is manually invoked from the command line (for testing).
#
# Usage: <input-rdf-file> [input-rdf-file-syntax] [output-rdf-file]
#
if __name__ == '__main__':

   if len(sys.argv) == 0:
      print resource.name + ' running on port ' + str(resource.dev_port) + '. Invoke it with:'
      print 'curl -H "Content-Type: text/turtle" -d @my.ttl http://localhost:' + str(resource.dev_port) + '/' + resource.name
      sadi.publishTwistedService(resource, port=resource.dev_port)
   else:
      reader= open(sys.argv[1],"r")
      mimeType = "application/rdf+xml"
      if len(sys.argv) > 2:
         mimeType = sys.argv[2]
      if len(sys.argv) > 3:
         writer = open(sys.argv[3],"w")

      graph = resource.processGraph(reader,mimeType)

      if len(sys.argv) > 3:
         writer.write(resource.serialize(graph,mimeType))
      else:
         print resource.serialize(graph,mimeType)
