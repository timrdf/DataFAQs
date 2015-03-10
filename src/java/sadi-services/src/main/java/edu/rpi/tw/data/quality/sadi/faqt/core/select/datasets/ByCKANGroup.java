package edu.rpi.tw.data.quality.sadi.faqt.core.select.datasets;

import org.apache.log4j.Logger;
import org.ckan.CKANException;
import org.ckan.Client;
import org.ckan.Connection;
import org.ckan.Dataset;
import org.ckan.Group;

import ca.wilkinsonlab.sadi.service.annotations.ContactEmail;
import ca.wilkinsonlab.sadi.service.annotations.Description;
import ca.wilkinsonlab.sadi.service.annotations.InputClass;
import ca.wilkinsonlab.sadi.service.annotations.Name;
import ca.wilkinsonlab.sadi.service.annotations.OutputClass;
import ca.wilkinsonlab.sadi.service.simple.SimpleSynchronousServiceServlet;

import com.hp.hpl.jena.rdf.model.Model;
import com.hp.hpl.jena.rdf.model.Resource;
import com.hp.hpl.jena.vocabulary.DCTerms;
import com.hp.hpl.jena.vocabulary.RDF;

import edu.rpi.tw.data.ckan.CKANReader;
import edu.rpi.tw.data.rdf.jena.vocabulary.DCAT;
import edu.rpi.tw.data.rdf.jena.vocabulary.DataFAQs;
import edu.rpi.tw.data.rdf.jena.vocabulary.Prefixes;
//import com.hp.hpl.jena.rdf.model.Statement;
//import com.hp.hpl.jena.rdf.model.StmtIterator;

/**
 * Java implementation of https://github.com/timrdf/DataFAQs/blob/master/services/sadi/core/select-datasets/by-ckan-group.py
 *
 */
@Name("select-datasets-by-ckan-group")
@Description("Links a CKAN group to the datasets that are in the group.")
@ContactEmail("lebot@rpi.edu")
@InputClass("http://purl.org/twc/vocab/datafaqs#CKANGroup")
@OutputClass("http://purl.org/twc/vocab/datafaqs#DatasetCollection")
public class ByCKANGroup extends SimpleSynchronousServiceServlet {
   
	private static final Logger log = Logger.getLogger(ByCKANGroup.class);
	private static final long serialVersionUID = 1L;

	@Override
	public void processInput(Resource input, Resource output) {
	   
      String inputS = input.asResource().getURI().toString();
      log.warn("processing "+inputS);
      String groupID = CKANReader.getCKANIdentifier(input);
      log.warn("processing id "+groupID);
      Model m = output.getModel();
      Prefixes.setNsPrefixes(m);
      
      String base = CKANReader.getBaseURI(input);
	   // (Taken from LiftCKAN)
      Client client = new Client( new Connection( CKANReader.getCKANAPI(input) ), "");
      //                                          ^ e.g. "http://datahub.io"     <key>
      
      try {
         Resource groupR = m.createResource(inputS, DataFAQs.CKANGroup);
         groupR.addProperty(RDF.type, DataFAQs.DatasetCollection);
         Group group = client.getGroup(groupID);
         for( Dataset dataset : group.getPackages() ) {
            //log.warn(groupID + " has dataset "+dataset.getName());
            Resource datasetR = m.createResource(base+"/dataset/"+dataset.getName(), DataFAQs.CKANDataset);
            datasetR.addProperty(RDF.type, DCAT.Dataset);
            output.addProperty(DCTerms.hasPart, datasetR);
         }
      }catch (CKANException e) {
         e.printStackTrace();
      }
	}	
}