package edu.rpi.tw.data.quality.sadi.faqt.sparql_service_description;

import java.io.UnsupportedEncodingException;
import java.net.URLEncoder;
import java.util.Calendar;
import java.util.GregorianCalendar;

import org.apache.log4j.Logger;

import ca.wilkinsonlab.sadi.service.annotations.ContactEmail;
import ca.wilkinsonlab.sadi.service.annotations.InputClass;
import ca.wilkinsonlab.sadi.service.annotations.Name;
import ca.wilkinsonlab.sadi.service.annotations.OutputClass;
import ca.wilkinsonlab.sadi.service.simple.SimpleSynchronousServiceServlet;

import com.hp.hpl.jena.query.Query;
import com.hp.hpl.jena.query.QueryExecution;
import com.hp.hpl.jena.query.QueryExecutionFactory;
import com.hp.hpl.jena.query.QueryFactory;
import com.hp.hpl.jena.query.QuerySolution;
import com.hp.hpl.jena.query.ResultSet;
import com.hp.hpl.jena.rdf.model.Model;
import com.hp.hpl.jena.rdf.model.RDFNode;
import com.hp.hpl.jena.rdf.model.Resource;
import com.hp.hpl.jena.sparql.resultset.ResultSetMem;
import com.hp.hpl.jena.sparql.resultset.ResultSetRewindable;
import com.hp.hpl.jena.vocabulary.DC;
import com.hp.hpl.jena.vocabulary.RDF;

import edu.rpi.tw.data.rdf.jena.vocabulary.DataFAQs;
import edu.rpi.tw.data.rdf.jena.vocabulary.Prefixes;
import edu.rpi.tw.data.rdf.jena.vocabulary.SD;
import edu.rpi.tw.data.rdf.jena.vocabulary.SIO;
import edu.rpi.tw.data.rdf.jena.vocabulary.VoID;

@Name("named-graphs")
@ContactEmail("lebot@rpi.edu")
@InputClass("http://www.w3.org/ns/dcat#Dataset")
@OutputClass("http://purl.org/twc/vocab/datafaqs#Evaluated")
public class NamedGraphs extends SimpleSynchronousServiceServlet
{
	@SuppressWarnings("unused")
	private static final Logger log = Logger.getLogger(NamedGraphs.class);
	private static final long serialVersionUID = 1L;

	/**
	 * <http://thedatahub.org/dataset/farmers-markets-geographic-data-united-states>
     *     void:sparqlEndpoint <http://logd.tw.rpi.edu/sparql> .
     *     
     *     or
     *     
     * <http://thedatahub.org/dataset/farmers-markets-geographic-data-united-states>
     *    dcat:distribution [
     *        a sd:NamedGraph;
     *        prov:atLocation <http://logd.tw.rpi.edu/sparql>;
     *        sd:name         <http://logd.tw.rpi.edu/source/data-gov/dataset/4383/version/2011-Nov-29> .
     *    ] .
	 */
	@Override
	public void processInput(Resource input, Resource output)
	{
		//output.addProperty(FOAF.knows, output.getModel().getResource("http://xmlns.com/foaf/0.1/#knows6"));
		
		Model m = output.getModel();
		
		String endpoint = null;
		if( input.hasProperty(VoID.sparqlEndpoint) ) {
			endpoint = input.getProperty(VoID.sparqlEndpoint).getObject().toString();
			output.addProperty(VoID.sparqlEndpoint, m.getResource(endpoint));
		}else {
			output.addProperty(RDF.type, DataFAQs.Unsatisfactory);
			return;
		}
		
		String queryS = "select distinct ?g where {graph ?g {[] a []}}";

		Query          query = QueryFactory.create(queryS);
		QueryExecution qexec = QueryExecutionFactory.sparqlService(endpoint, query);

		ResultSet results = qexec.execSelect();
		if( results.hasNext() ) {
			output.addProperty(RDF.type, DataFAQs.Satisfactory);
	        //output.addProperty(Vocab.description, ResultSetFormatter.asText(results)); 
			
			/*for( String var : results.getResultVars() ) {
		        output.addProperty(Vocab.comment, var); # e.g. "g"
			}*/
	
			Resource graphCollection = m.createResource();
			output.addProperty(SD.availableGraphs, graphCollection);
			graphCollection.addProperty(RDF.type, SD.GraphCollection);
			Calendar cal = GregorianCalendar.getInstance();
			graphCollection.addProperty(DC.date, m.createTypedLiteral(cal));

			
			// http://grepcode.com/file/repo1.maven.org/maven2/com.hp.hpl.jena/arq/2.6.0/com/hp/hpl/jena/query/ResultSetFormatter.java
			
			ResultSetRewindable resultSetRewindable = new ResultSetMem(results);
			long numNGs = 0;
			while( resultSetRewindable.hasNext() ) {
				QuerySolution binding = resultSetRewindable.nextSolution();
				numNGs++;
				RDFNode name = binding.get("g");
				
				Resource ng = m.createResource(getSPARQLEndpointGraphName(endpoint, name.toString()));
				if( name.isURIResource() && name.asResource().getURI().toString().startsWith("http") ) {
					ng.addProperty(SD.name, name);
				}else {
					ng.addLiteral(DC.description, name.toString());
				}
				ng.addProperty(RDF.type, SD.NamedGraph);
				graphCollection.addProperty(SD.namedGraph, ng);
			}
			graphCollection.addLiteral(SIO.count, numNGs);
		}else {
			output.addProperty(RDF.type, DataFAQs.Unsatisfactory);
		}
		qexec.close();
		
    	Prefixes.setNsPrefixes(output.getModel());
	}

	/**
	 * COPIED from csv2rdf4lod NameFactory.
	 * 
	 * @param endpoint
	 * @param graph_name
	 * @return
	 */
	public static String getSPARQLEndpointGraphName(String endpoint, String graph_name) {

		//
		//
		// Do NOT change the spacing in this string. It is following the canonical URI construction.
		String query = 
				"PREFIX sd: <http://www.w3.org/ns/sparql-service-description#> "+
						"CONSTRUCT { ?endpoints_named_graph ?p ?o } "+
						"WHERE { GRAPH <"+graph_name+"> { "+
						"[] sd:url <"+endpoint+">; "+
						"sd:defaultDatasetDescription [ sd:namedGraph ?endpoints_named_graph ] . "+
						"?endpoints_named_graph sd:name <"+graph_name+">; ?p ?o . } }";
		// Do NOT change the spacing in this string. It is following the canonical URI construction.
		//
		//

		try {
			return endpoint + "?query=" + URLEncoder.encode(query, "ISO-8859-1");
		} catch (UnsupportedEncodingException e) {
			e.printStackTrace();
			return null;
		}
	}
}