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

import os.path

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

      my_print_debug = False

      if my_print_debug:
         print >> sys.stderr, '   walking: "' + urlpath + '"' #+ ' (base = ' + base + ')'

      Node = output.session.get_class(ns.BTE['Node'])

      # "/twc/"               -> "/twc"
      # "/ftp/hsp/TANF-data/" -> "/ftp/hsp/TANF-data"
      if re.match('.*/$',urlpath):
         # ^ This should only occur when first called by #process(),
         # since walkPath does not include a trailing slash its 
         # recursive calls.
         # FWIW, this is done in process() for URIs with fragIDs
         trimmed_path = re.sub('/$','',urlpath)
         broader = output.session.get_resource(base+trimmed_path,Node)
         broader.rdf_type.append(ns.BTE['Node'])
         broader.save()
         output.bte_broader = broader
         return 1 + BetweenTheEdges.walkPath(base, trimmed_path, output)

      me = output.session.get_resource(base+urlpath,Node) if base+urlpath != str(output.subject) else output
      me.rdf_type.append(ns.BTE['Node'])

      # e.g.
      #     "http://dailymed.nlm.nih.gov/dailymed/help.cfm"
      #     "http://healthit.hhs.gov/portal/server.pt"
      #
      extension = BetweenTheEdges.extension(urlpath,me)
      if my_print_debug:
         if extension is not None:
            print >> sys.stderr, '              '+re.sub('.',' ',urlpath) + extension

      # e.g.
      #      "/"
      #      "/id/agency/cdc"
      #
      match = re.search("^(.*)/([^/]+)$",urlpath)
      if match:
         trimmed_path = match.group(1)
         step         = match.group(2)
         if my_print_debug:
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
         if my_print_debug:
            print >> sys.stderr, '           ' + base + ' + "' + urlpath + '" is root. ' + me.subject
         me.bte_depth = 0
         me.save()
         return 0

   def process(self, input, output):

      my_print_debug = False

      print >> sys.stderr, 'processing ' + input.subject

      length = BetweenTheEdges.length(input,output)

      #
      # Using urlparse - http://docs.python.org/2/library/urlparse.html
      # e.g. ParseResult(scheme='http', netloc='www.cwi.nl:80', path='/%7Eguido/Python.html', params='', query='', fragment='')
      #
      url6 = urlparse(str(input.subject))
      scheme   = BetweenTheEdges.scheme(url6,output)
      netloc   = BetweenTheEdges.netloc(url6,output)
      path     = BetweenTheEdges.path(url6,output)     # Does NOT include ending '#'.
      fragment = BetweenTheEdges.fragment(url6,output) # returns portion after '#'; if just '#' returns None.

      if re.match('.*/$',input.subject):
         # URI ends in '/'
         output.rdf_type.append(ns.BTE['SlashEndURI'])
         fragDepth = 0
      elif re.match('.*#$',input.subject):
         # URI ends in '#'
         output.rdf_type.append(ns.BTE['HashEndURI'])
         fragDepth = 1 
      elif fragment is not None and len(fragment):
         fragDepth = 1 
      else:
         fragDepth = 0

      # TODO: "netloc" fails if it's an IP.

      # <http://dailymed.nlm.nih.gov/dailymed/help.cfm#webservices> 
      #    a bte:RDFNode;
      #    bte:scheme "http";
      #    bte:netloc      "dailymed.nlm.nih.gov";
      #    bte:path                             "/dailymed/help.cfm";
      #    bte:fragment                                            "webservices";
      #    bte:length                                                         57;

      if scheme in ['http', 'https'] and path is not None:
         if fragDepth > 0:
            # FWIW, this is done in walkPath() for URIs ending in '/'
            Node = output.session.get_class(ns.BTE['Node'])
            trimmed_path = re.sub('#.*$','',input.subject)
            if my_print_debug:
               print >> sys.stderr, '   handling "' + trimmed_path + '#..."' 
            broader = output.session.get_resource(trimmed_path,Node)
            broader.rdf_type.append(ns.BTE['Node'])
            broader.save()
            output.bte_broader = broader

         pathDepth = BetweenTheEdges.walkPath(scheme+'://'+netloc , path, output)
         # <http://bioportal.bioontology.org/>                         depth 1 ('' after the slash)
         # <http://aidsinfo.nih.gov/api>                               depth 1
         # <http://bhpr.hrsa.gov/healthworkforce/default.htm>          depth 2
         # <http://bioportal.bioontology.org/ontologies/umls/>         depth 3 ('' after the slash)
         # <http://bioportal.bioontology.org/ontologies/umls/cui>      depth 3
         # <http://dailymed.nlm.nih.gov/dailymed/help.cfm#>            depth 3 (hash adds one)
         # <http://dailymed.nlm.nih.gov/dailymed/help.cfm#webservices> depth 3 
         # <http://aspe.hhs.gov/ftp/hsp/TANF-data/>                    depth 4 ('' after the slash)
         output.bte_depth = pathDepth + fragDepth

      output.rdf_type.append(ns.BTE['RDFNode'])
      output.save()

# Used when Twistd invokes this service b/c it is sitting in a deployed directory.
resource = BetweenTheEdges()

# Used when this service is manually invoked from the command line (for testing).
#
# Usage: <input-rdf-file> [input-rdf-file-syntax] ( [output-rdf-file] | -od <directory> )
#
# If dependency issues, see https://github.com/timrdf/DataFAQs/issues/125
#
if __name__ == '__main__':

   if len(sys.argv) == 1:
      print resource.name + ' running on port ' + str(resource.dev_port) + '. Invoke it with:'
      print 'curl -H "Content-Type: text/turtle" -d @my.ttl http://localhost:' + str(resource.dev_port) + '/' + resource.name
      sadi.publishTwistedService(resource, port=resource.dev_port)
   else:
      reader= open(sys.argv[1],"r")
      mimeType = "application/rdf+xml"
      if len(sys.argv) > 2:
         mimeType = sys.argv[2]
      if len(sys.argv) == 5 and sys.argv[3] == '-od':
         print sys.argv[4]+"/"+os.path.basename(sys.argv[1])+".bte.ttl"
         if not os.path.exists(sys.argv[4]):
            os.makedirs(sys.argv[4])
         writer = open(sys.argv[4]+"/"+os.path.basename(sys.argv[1])+".bte.ttl","w")
      elif len(sys.argv) > 3:
         writer = open(sys.argv[3],"w")

      graph = resource.processGraph(reader,mimeType)

      if len(sys.argv) > 3:
         writer.write(resource.serialize(graph,mimeType))
      else:
         print resource.serialize(graph,mimeType)
