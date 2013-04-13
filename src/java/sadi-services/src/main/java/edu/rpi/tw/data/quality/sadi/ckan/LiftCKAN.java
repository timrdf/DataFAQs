package edu.rpi.tw.data.quality.sadi.ckan;

import org.apache.log4j.Logger;
import org.ckan.CKANException;
import org.ckan.Client;
import org.ckan.Connection;
import org.ckan.Dataset;
import org.ckan.Extra;
import org.ckan.Group;

import ca.wilkinsonlab.sadi.service.annotations.ContactEmail;
import ca.wilkinsonlab.sadi.service.annotations.InputClass;
import ca.wilkinsonlab.sadi.service.annotations.Name;
import ca.wilkinsonlab.sadi.service.annotations.OutputClass;
import ca.wilkinsonlab.sadi.service.simple.SimpleSynchronousServiceServlet;

import com.hp.hpl.jena.rdf.model.Model;
import com.hp.hpl.jena.rdf.model.Resource;
import com.hp.hpl.jena.sparql.vocabulary.FOAF;
import com.hp.hpl.jena.vocabulary.DC;
import com.hp.hpl.jena.vocabulary.DCTerms;
import com.hp.hpl.jena.vocabulary.RDF;
import com.hp.hpl.jena.vocabulary.RDFS;

import edu.rpi.tw.data.ckan.CKANReader;
import edu.rpi.tw.data.naming.NameFactory;
import edu.rpi.tw.data.rdf.jena.vocabulary.CON;
import edu.rpi.tw.data.rdf.jena.vocabulary.DCAT;
import edu.rpi.tw.data.rdf.jena.vocabulary.DataFAQs;
import edu.rpi.tw.data.rdf.jena.vocabulary.OV;
import edu.rpi.tw.data.rdf.jena.vocabulary.PROV;
import edu.rpi.tw.data.rdf.jena.vocabulary.Prefixes;
import edu.rpi.tw.data.rdf.jena.vocabulary.SD;
import edu.rpi.tw.data.rdf.jena.vocabulary.Tag;
import edu.rpi.tw.data.rdf.jena.vocabulary.VoID;

/**
 * Re-implementation of https://github.com/timrdf/DataFAQs/blob/master/services/sadi/ckan/lift-ckan.py
 * 
 * See also https://github.com/timrdf/DataFAQs/wiki/FAqT-Service
 */
@Name("lift-ckan")
@ContactEmail("lebot@rpi.edu")
@InputClass("http://purl.org/twc/vocab/datafaqs#CKANDataset") 
@OutputClass("http://purl.org/twc/vocab/datafaqs#CKANDataset")
public class LiftCKAN extends SimpleSynchronousServiceServlet {
	
	private static final Logger log = Logger.getLogger(LiftCKAN.class);
	private static final long serialVersionUID = 1L;

	/**
	 * 
	 */
	@Override
	public void processInput(Resource input, Resource output) {
		
        Client client = new Client( new Connection( CKANReader.getCKANAPI(input) ), "");
        //                                          ^ e.g. "http://datahub.io"     <key>
        
        try {
        	String inputS = input.asResource().getURI().toString();
        	String base = inputS.replaceFirst("\\/dataset\\/.*$", "");
        	
        	Dataset ds = client.getDataset(CKANReader.getCKANIdentiifer(input));
        	//                             ^ e.g. "farmers-markets-geographic-data-united-states"
        	
        	Model m = output.getModel();
        	Prefixes.setNsPrefixes(m);

        	
        	// Title
        	if( valid(ds.getTitle()) ) {
        		output.addProperty(DC.title, ds.getTitle());
        	}
        	
        	// Notes
        	if( valid(ds.getNotes()) ) {
        		//output.addProperty(DC.description, ds.getNotes());
        	}
        	
        	//
        	// Resources
        	//
        	Resource sparqlEndpoint = null; // Save for Extras processing named graph.
        	for (org.ckan.Resource resource : ds.getResources() ) {
        		if( valid(resource.getUrl()) ) {
					if( "api/sparql".equals(resource.getFormat()) ) {
						sparqlEndpoint = m.createResource(resource.getUrl());
	    				output.addProperty(VoID.sparqlEndpoint, sparqlEndpoint);
	    				System.out.println( " name. "  + resource.getName() );
	        			System.out.println( "    Format: "      + resource.getFormat() );
	        			System.out.println( "    Mimetype: "    + resource.getMimetype() );
	        			System.out.println( "    Description: " + resource.getDescription() );
	        			System.out.println( "    URL: "         + resource.getUrl() + "\n");   
	        			if( valid(resource.getUrl()) ) {
	        				output.addProperty(VoID.sparqlEndpoint, output.getModel().createResource(resource.getUrl()));
	        			}
	        		}else if( "example/turtle".equals(resource.getFormat())) {
	    				output.addProperty(DataFAQs.todo, "resource of type " + resource.getFormat());
	        		}else {
	    				output.addProperty(DataFAQs.todo, "resource of type " + resource.getFormat());
	        		}
        		}
        	}

        	
        	//
        	// Groups
        	//
        	for( Group group : ds.getGroups() ) {
    			Resource groupR = m.createResource(base+"/group/"+group.getName().replaceAll(" ", "-"), DataFAQs.CKANGroup);
    			groupR.addLiteral(DC.identifier, group.getName().replaceAll(" ", ""));
    			groupR.addLiteral(FOAF.name, group.getName());
    			groupR.addLiteral(RDFS.label, group.getName());
    			output.addProperty(DCTerms.isPartOf, groupR);
        	}
        	
        	
        	//
        	// Tags
        	//
        	for( org.ckan.Tag tag : ds.getTags() ) {
        		//output.addProperty(edu.rpi.tw.data.rdf.jena.vocabulary.Tag.taggedWithTag,
        		//		tag.getDisplayName() + " - " + tag.getId() + " - " + tag.getName() + " - " + tag.getVocabularyId());
        		
    			Resource tagR = m.createResource(base+"/tag/"+tag.getName().replaceAll(" ", "-"), Tag.Tag);
    			output.addProperty(Tag.taggedWithTag, tagR);
    			tagR.addLiteral(RDFS.label, tag.getDisplayName()); // Tag.name
    			
    			if( tag.getName().startsWith("format-") ) {
    				// TODO assert VoID.vocabulary based on prefix.cc
    			}
        	}
        	
        	
        	//
        	// Extras
        	//
        	for( Extra extra : ds.getExtras() ){
        		System.out.println(extra.getKey() + extra.getValue());
        		if( "triples".equals(extra.getKey()) ) {
        			long size = Long.parseLong(extra.getValue().replaceAll("[^0-9]", ""));
        			output.addLiteral(VoID.triples, size);
        		}else if( "shortname".equals(extra.getKey()) && valid(extra.getValue()) ) {
        			output.addLiteral(OV.shortName, trim(extra.getValue()));
        		}else if( extra.getKey().startsWith("links:") ) {
        			String otherID  = extra.getKey().substring("links:".length()).replaceAll(" ", "-");
        			String other    = inputS.replaceFirst("\\/dataset\\/.*$", "/dataset/"+otherID);    
        			Resource otherR = m.createResource(other, DataFAQs.CKANDataset);
        			
        			Resource linkset = m.createResource("#linkset-"+otherID+"-"+
        												NameFactory.getMD5(inputS+otherID+ds.getRevision_id()),
        												VoID.Linkset);
        			long size = Long.parseLong(extra.getValue().replaceAll("[^0-9]", ""));
        			linkset.addLiteral(VoID.triples, size);
        			linkset.addProperty(VoID.target, otherR);
        			linkset.addProperty(VoID.target, output);
        			
        			output.addProperty(VoID.subset, linkset);
        		}else if( "preferred_uri".equals(extra.getKey()) && valid(extra.getValue()) ) {
        			output.addProperty(CON.preferredURI, m.createResource(trim(extra.getValue())));
        			//output.addProperty(DataFAQs.todo, "extra: " + extra.getKey() + " = " + extra.getValue());
        		}else if( "namespace".equals(extra.getKey()) && valid(extra.getValue()) ) {
        			output.addLiteral(VoID.uriSpace, trim(extra.getValue()));
        			//output.addProperty(DataFAQs.todo, "extra: " + extra.getKey() + " = " + extra.getValue());
        		}else if( "sparql_graph_name".equals(extra.getKey()) && valid(extra.getValue()) ) {
        			String name = trim(extra.getValue());
                    /*
                    *   <dataset> dcat:distribution [
                    *      a sd:NamedGraph;
                    *      sd:name  <http://purl.org/twc/arrayexpress/E-MTAB-104>;
                    *      sd:graph <http://datahub.io/en/dataset/arrayexpress-e-afmx-1>;
                    *      prov:atLocation <sparqlEndpoint>
                    *   ];
                    */
        			Resource namedGraph = sparqlEndpoint != null ? 
        						m.createResource( "#named-graph-"+NameFactory.getMD5(sparqlEndpoint.getURI().toString()+name), SD.NamedGraph):
            					m.createResource( "#named-graph-"+NameFactory.getMD5(                                   name), SD.NamedGraph);        						
        			output.addProperty(DCAT.distribution, namedGraph);
        			namedGraph.addProperty(SD.name, m.createResource(name));
        			if( sparqlEndpoint != null ) {
        				namedGraph.addProperty(PROV.atLocation, sparqlEndpoint);
        			}
        		}else {
        			output.addProperty(DataFAQs.todo, "extra: " + extra.getKey() + " = " + extra.getValue());
        		}
        	}
        	//output.addProperty(RDF.type, DCAT.Dataset);
        } catch ( CKANException e ) {
            System.out.println(e);
        }
	}
	
	private boolean valid(String string) {
		return string != null && string.length() > 0;
	}
	
	private String trim(String string) {
		return valid(string) ? string.replaceAll("^\"", "").replaceAll("\"$", "") : string;
	}
}