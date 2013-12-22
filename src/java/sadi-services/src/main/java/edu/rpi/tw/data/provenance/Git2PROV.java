package edu.rpi.tw.data.provenance;

import java.io.UnsupportedEncodingException;
import java.net.URLEncoder;

import org.apache.log4j.Logger;

import ca.wilkinsonlab.sadi.service.annotations.ContactEmail;
import ca.wilkinsonlab.sadi.service.annotations.Description;
import ca.wilkinsonlab.sadi.service.annotations.InputClass;
import ca.wilkinsonlab.sadi.service.annotations.Name;
import ca.wilkinsonlab.sadi.service.annotations.OutputClass;
import ca.wilkinsonlab.sadi.service.simple.SimpleSynchronousServiceServlet;

import com.hp.hpl.jena.rdf.model.Resource;
import com.hp.hpl.jena.vocabulary.RDFS;

import edu.rpi.tw.data.http.HTTPUtils;

@Name("git2prov")
@Description("Produces a PROV-O description of a given Git repository.")
@ContactEmail("lebot@rpi.edu")
@InputClass("http://usefulinc.com/ns/doap#GitRepository")
@OutputClass("http://www.w3.org/ns/prov#Entity")
public class Git2PROV extends SimpleSynchronousServiceServlet {
   
   private static final Logger log = Logger.getLogger(Git2PROV.class);
   private static final long serialVersionUID = 1L;

   @Override
   public void processInput(Resource input, Resource output) {

      String inputS = input.asResource().getURI().toString();
      log.warn("processing "+inputS);

      if( inputS.startsWith("http") ) {
         //     git@github.com:tetherless-world/opendap.git needs to be rewritten as:
         // https://github.com/tetherless-world/opendap.git
         
         //                                     https://github.com/tetherless-world/opendap.git
         // http://git2prov.org/git2prov?giturl=https%3A%2F%2Fgithub.com%2Ftetherless-world%2Fopendap.git&serialization=PROV-O
         try {
            String url = "http://git2prov.org/git2prov?giturl="+URLEncoder.encode(inputS, "UTF-8")+"&serialization=PROV-O";
            log.warn("will request from: " + url);
            
            //String response = HTTPUtils.get(url, "text/turtle");
            //log.warn("response: " + response);
            
            output.getModel().read(url,"TURTLE");
            log.warn("loaded size: " + output.getModel().size());

         } catch (UnsupportedEncodingException e) {
            e.printStackTrace();
         }
      }else {
         output.addLiteral(RDFS.comment, "Git Repository needs to be HTTPS");
      }
   }
}