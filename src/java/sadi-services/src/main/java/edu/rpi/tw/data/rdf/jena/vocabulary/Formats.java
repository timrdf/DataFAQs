package edu.rpi.tw.data.rdf.jena.vocabulary;

import java.util.HashMap;

import com.hp.hpl.jena.rdf.model.Model;
import com.hp.hpl.jena.rdf.model.ModelFactory;
import com.hp.hpl.jena.rdf.model.Property;
import com.hp.hpl.jena.rdf.model.Resource;

/**
 * See http://www.w3.org/ns/formats/
 *
 */
public class Formats {

	private static Model m_model = ModelFactory.createDefaultModel();

	public static String prefix = "formats";
	public static String ns     = "http://www.w3.org/ns/formats/";

	public static final Resource Format           = m_model.createResource(ns+"Format");
	
	public static final Property media_type       = m_model.createProperty(ns+"media_type");
	public static final Property preferred_suffix = m_model.createProperty(ns+"preferred_suffix");

	public static final HashMap<String,Resource> formats = new HashMap<String,Resource>();

	public static final Resource N3                  = m_model.createResource(ns + "N3");
	public static final Resource NTriples            = m_model.createResource(ns + "N-Triples");
	public static final Resource OWL_XML             = m_model.createResource(ns + "OWL_XML");
	public static final Resource OWL_Functional      = m_model.createResource(ns + "OWL_Functional");
	public static final Resource OWL_Manchester      = m_model.createResource(ns + "OWL_Manchester");
	public static final Resource POWDER              = m_model.createResource(ns + "POWDER");
	public static final Resource POWDER_S            = m_model.createResource(ns + "POWDER-S");
	public static final Resource RDFa                = m_model.createResource(ns + "RDFa");
	public static final Resource RDF_XML             = m_model.createResource(ns + "RDF_XML");
	public static final Resource RIF_XML             = m_model.createResource(ns + "RIF_XML");
	public static final Resource SPARQL_Results_XML  = m_model.createResource(ns + "SPARQL_Results_XML");
	public static final Resource SPARQL_Results_JSON = m_model.createResource(ns + "SPARQL_Results_JSON");
	public static final Resource SPARQL_Results_CSV  = m_model.createResource(ns + "SPARQL_Results_CSV");
	public static final Resource SPARQL_Results_TSV  = m_model.createResource(ns + "SPARQL_Results_TSV");
	public static final Resource Turtle              = m_model.createResource(ns + "Turtle");
	public static final Resource PROV_N              = m_model.createResource(ns + "PROV-N");
	public static final Resource PROV_XML            = m_model.createResource(ns + "PROV-XML");
	public static final Resource JSON_LD             = m_model.createResource(ns + "JSON-LD");

	static {
		formats.put("rdf+xml",    RDF_XML);
		formats.put("turtle",     Turtle);
		formats.put("ntriples",   NTriples);
		formats.put("x-ntriples", NTriples);
		formats.put("x-quads",    null);
		formats.put("rdfa",       RDFa);
		formats.put("x-trig",     null);
	}

	public static Resource getFormat(String label) {
		return formats.containsKey(label) ? formats.get(label) : null;
	}
}