package edu.rpi.tw.data.quality.sadi.ckan;

import java.util.HashMap;

import org.apache.log4j.Logger;
import org.ckan.CKANException;
import org.ckan.Client;
import org.ckan.Connection;
import org.ckan.Dataset;
import org.ckan.DatasetRevision;
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
import com.hp.hpl.jena.vocabulary.RDFS;

import edu.rpi.tw.data.ckan.CKANReader;
import edu.rpi.tw.data.naming.NameFactory;
import edu.rpi.tw.data.rdf.jena.vocabulary.CON;
import edu.rpi.tw.data.rdf.jena.vocabulary.DCAT;
import edu.rpi.tw.data.rdf.jena.vocabulary.DataFAQs;
import edu.rpi.tw.data.rdf.jena.vocabulary.Formats;
import edu.rpi.tw.data.rdf.jena.vocabulary.OV;
import edu.rpi.tw.data.rdf.jena.vocabulary.PROV;
import edu.rpi.tw.data.rdf.jena.vocabulary.Prefixes;
import edu.rpi.tw.data.rdf.jena.vocabulary.SD;
import edu.rpi.tw.data.rdf.jena.vocabulary.SIOC;
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
	
	private HashMap<String,Resource> ephemeralFormats = new HashMap<String,Resource>();

	/**
	 * 
	 */
	@Override
	public void processInput(Resource input, Resource output) {
        
        try {
            Client client = new Client( new Connection( CKANReader.getCKANAPI(input) ), "");
            //                                          ^ e.g. "http://datahub.io"     <key>
            
        	String inputS = input.asResource().getURI().toString();
        	log.warn("processing "+inputS);
        	
        	String base = CKANReader.getBaseURI(input); // inputS.replaceFirst("\\/dataset\\/.*$", "");
        	
        	log.warn("processing id "+CKANReader.getCKANIdentiifer(input));
        	Dataset ds = client.getDataset(CKANReader.getCKANIdentiifer(input));
        	//                             ^ e.g. "farmers-markets-geographic-data-united-states"
        	
        	Model m = output.getModel();
        	Prefixes.setNsPrefixes(m);

        	// Title
        	tryTitle(ds, output);
        	
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
        			
        			Resource distribution = m.createResource(resource.getUrl(), DCAT.Distribution);
        			if( valid(resource.getDescription()) ) {
        				distribution.addProperty(DCTerms.description, resource.getDescription());
        			}
        			output.addProperty(DCAT.distribution, distribution);
        			Resource resourceR = m.createResource(inputS+"/resource/"+resource.getId(), DataFAQs.CKANResource);
        			resourceR.addProperty(DCTerms.isPartOf, output);
        			
					if( "api/sparql".equals(resource.getFormat()) ) {
						
	    				//System.out.println( " name. "  + resource.getName() );
	        			//System.out.println( "    Format: "      + resource.getFormat() );
	        			//System.out.println( "    Mimetype: "    + resource.getMimetype() );
	        			//System.out.println( "    Description: " + resource.getDescription() );
	        			//System.out.println( "    URL: "         + resource.getUrl() + "\n");   
						
						sparqlEndpoint = m.createResource(resource.getUrl(), SD.Service);
	    				output.addProperty(VoID.sparqlEndpoint, sparqlEndpoint);
	    				output.addProperty(DCAT.distribution,   sparqlEndpoint);

	        		}else if( resource.getFormat().startsWith("example/") ) {
	        			/*
	        			 * William Waite's GoLD translation (https://bitbucket.org/okfn/gockan):
	        			 * 
	        			 * <http://thedatahub.org/dataset/farmers-markets-geographic-data-united-states>
	        			 *    dcat:distribution [
	        			 *       a dcat:Distribution ;
						 *       dc:description "Turtle example link" ;
						 *       dc:format [
						 *          moat:taggedWithTag [
						 *              moat:name "example/turtle" ;
						 *              a moat:Tag
						 *          ] ;
						 *          a dc:IMT
						 *      ] ;
						 *      dcat:accessURL <http://logd.tw.rpi.edu/...data-gov-4383-2011-Nov-29.e1.sample.ttl>
						 *    ];
						 * .
	        			 */
	        			distribution.addProperty(DCAT.downloadURL, distribution);

	        			// Format
	        			String format = resource.getFormat().substring("example/".length()).trim();
	        			Resource formatR = Formats.getFormat(format);
	        			if( formatR == null ) {
	        				formatR = m.createResource(DCTerms.FileFormat);
	        			}
        				formatR.addProperty(RDFS.label, format);
        				distribution.addProperty(DCTerms.format, formatR);

	        			output.addProperty(VoID.exampleResource, distribution);
	        		}else if( "csv".equalsIgnoreCase(resource.getFormat()) ) {
	        			distribution.addProperty(DCAT.downloadURL, distribution);
	        			
	        			distribution.addProperty(FOAF.isPrimaryTopicOf, resourceR);
	        			
	        			Resource formatPW  = m.createResource("http://provenanceweb.org/format/mime/text/csv");
	        			formatPW.addLiteral(RDFS.label, "CSV");
	        			formatPW.addLiteral(DCTerms.description, "Comma Separated Values");
	        			
	        			Resource formatPRN = m.createResource("http://provenanceweb.org/formats/pronom/x-fmt/18");
	        			formatPRN.addLiteral(RDFS.label, "CSV");
	        			formatPRN.addLiteral(DCTerms.description, "Comma Separated Values");
	        			
	        			distribution.addProperty(DCTerms.format, formatPW);
	        			distribution.addProperty(DCTerms.format, formatPRN);
	        		}else if( "pdf".equalsIgnoreCase(resource.getFormat()) ) {
	        			distribution.addProperty(DCAT.downloadURL, distribution);
	        			
	        			distribution.addProperty(FOAF.isPrimaryTopicOf, resourceR);
	        			
	        			Resource formatPW  = m.createResource("http://provenanceweb.org/format/mime/application/pdf");
	        			formatPW.addLiteral(RDFS.label, "PDF");
	        			formatPW.addLiteral(DCTerms.description, "Portable Document Format");
	        			
	        			Resource formatPRN = m.createResource("http://provenanceweb.org/formats/pronom/fmt/276");
	        			formatPRN.addLiteral(RDFS.label, "PDF");
	        			formatPRN.addLiteral(DCTerms.description, "Portable Document Format");
	        			
	        			distribution.addProperty(DCTerms.format, formatPW);
	        			distribution.addProperty(DCTerms.format, formatPRN);
	        		}else if( "pptx".equalsIgnoreCase(resource.getFormat()) ) {
	        			distribution.addProperty(DCAT.downloadURL, distribution);
	        			
	        			distribution.addProperty(FOAF.isPrimaryTopicOf, resourceR);
	        			
	        			Resource formatPW  = m.createResource("http://provenanceweb.org/format/mime/application/vnd.ms-powerpoint");
	        			formatPW.addLiteral(RDFS.label, "PDF");
	        			formatPW.addLiteral(DCTerms.description, "Microsoft Powerpoint");
	        			
	        			Resource formatPRN = m.createResource("http://provenanceweb.org/formats/pronom/fmt/215");
	        			formatPRN.addLiteral(RDFS.label, "PDF");
	        			formatPRN.addLiteral(DCTerms.description, "Microsoft Powerpoint for Windows");
	        			
	        			distribution.addProperty(DCTerms.format, formatPW);
	        			distribution.addProperty(DCTerms.format, formatPRN);
	        		}else {
	        			distribution.addProperty(FOAF.isPrimaryTopicOf, resourceR);
	        			distribution.addProperty(DCAT.downloadURL, distribution);
	        			
	        			Resource format = getFormat(resource.getFormat(), m);
	        			
	        			distribution.addProperty(DCTerms.format, format);
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
        		if( "triples".equals(extra.getKey()) ) {
        			long size = Long.parseLong(extra.getValue().replaceAll("[^0-9]", ""));
        			output.addLiteral(VoID.triples, size);
        		}else if( "shortname".equals(extra.getKey()) && valid(extra.getValue()) ) {
        			output.addLiteral(OV.shortName, trim(extra.getValue()));
        		}else if( extra.getKey().startsWith("links:") ) {
        			String otherID  = extra.getKey().substring("links:".length()).replaceAll(" ", "-");
        			String other    = inputS.replaceFirst("\\/dataset\\/.*$", "/dataset/"+otherID);    
        			Resource otherR = m.createResource(other, DataFAQs.CKANDataset);
        			
        			// Jena can't handle relative fragIDs...
        			/*Resource linkset = m.createResource("#linkset-"+otherID+"-"+
        												NameFactory.getMD5(inputS+otherID+ds.getRevision_id()),
        												VoID.Linkset);*/
        			Resource linkset = m.createResource(NameFactory.INSTANCE_HUB+"linkset/"+otherID+"/"+
														NameFactory.getMD5(inputS+otherID+ds.getRevision_id()),
														VoID.Linkset);
        			long size = Long.parseLong(extra.getValue().replaceAll("[^0-9]", ""));
        			linkset.addLiteral(VoID.triples, size);
        			linkset.addProperty(VoID.target, otherR);
        			linkset.addProperty(VoID.target, output);
        			
        			log.warn("void:subset "+linkset.getURI().toString());
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
        			// Jena can't handle relative fragIDs...
        			/*Resource namedGraph = sparqlEndpoint != null ? 
        						m.createResource( "#named-graph-"+NameFactory.getMD5(sparqlEndpoint.getURI().toString()+name), SD.NamedGraph):
            					m.createResource( "#named-graph-"+NameFactory.getMD5(                                   name), SD.NamedGraph);*/
        			Resource namedGraph = sparqlEndpoint != null ? 
    						m.createResource(NameFactory.INSTANCE_HUB+"named-graph/"+NameFactory.getMD5(sparqlEndpoint.getURI().toString()+name), SD.NamedGraph):
        					m.createResource(NameFactory.INSTANCE_HUB+"named-graph/"+NameFactory.getMD5(                                   name), SD.NamedGraph);   
        			output.addProperty(DCAT.distribution, namedGraph);
        			namedGraph.addProperty(SD.name, m.createResource(name));
        			if( sparqlEndpoint != null ) {
        				namedGraph.addProperty(PROV.atLocation, sparqlEndpoint);
        			}
        		}else {
        			output.addProperty(DataFAQs.todo, "extra: " + extra.getKey() + " = " + extra.getValue());
        		}
        	}
        
        	//
        	// Dataset entry revisions
        	//
        	for( DatasetRevision revision : client.getDatasetRevisions(CKANReader.getCKANIdentiifer(input)) ) {
        		Resource revisionR = m.createResource(base+"/revision/"+revision.getID());
        		
        		Resource user = null;
        		if( revision.getAuthor() != null && revision.getAuthor().startsWith("http") ) {
        			user = m.createResource(revision.getAuthor());
        		}else if(revision.getAuthor() != null && 
        				revision.getAuthor().matches(
        				"^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$") ) {
        			user = m.createResource(base+"/user/"+revision.getAuthor());
        			revisionR.addLiteral(SIOC.ip_address, revision.getAuthor());
        		}else if( revision.getAuthor() != null ){
        			user = m.createResource(base+"/user/"+revision.getAuthor());
        		}
        		
        		output.addProperty(PROV.wasDerivedFrom, revisionR);
        		revisionR.addProperty(DCTerms.created, revision.getTimestamp());
        		if( revision.getMessage() != null && revision.getMessage().length() > 0 ) {
        			revisionR.addProperty(DCTerms.description, revision.getMessage());
        		}
        		if( user != null ) {
        			revisionR.addProperty(PROV.wasAttributedTo, user);
            		user.addProperty(FOAF.name, revision.getAuthor());
        		}
        	}
        	//output.addProperty(RDF.type, DCAT.Dataset);
        }catch ( CKANException e ) {
            log.error("CKANException " + e.getMessage());
        }
	}
	
	private Resource getFormat(String label, Model m) {
		Resource formatR = Formats.getFormat(label);
		if( formatR == null ) {
			if( !ephemeralFormats.containsKey(label) ) {
				formatR = m.createResource(DCTerms.FileFormat);
				ephemeralFormats.put(label, formatR);
			}
			formatR = ephemeralFormats.get(label);
		}
		formatR.addProperty(RDFS.label, label);
		formatR.addProperty(DataFAQs.todo, "URI for FileFormat " + label);
		return formatR;
	}
	
	private void tryTitle(Dataset ds, Resource output) {
		try {
	    	// Title
	    	if( valid(ds.getTitle()) ) {
	    		output.addProperty(DC.title, ds.getTitle());
	    	}
		} catch(Exception e) {
			log.error("exception on title");
		}
	}
	
	private boolean valid(String string) {
		return string != null && string.length() > 0;
	}
	
	private String trim(String string) {
		return valid(string) ? string.replaceAll("^\"", "").replaceAll("\"$", "") : string;
	}
}