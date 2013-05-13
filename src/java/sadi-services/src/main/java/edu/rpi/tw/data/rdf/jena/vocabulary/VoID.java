package edu.rpi.tw.data.rdf.jena.vocabulary;

import com.hp.hpl.jena.rdf.model.Model;
import com.hp.hpl.jena.rdf.model.ModelFactory;
import com.hp.hpl.jena.rdf.model.Property;
import com.hp.hpl.jena.rdf.model.Resource;

public class VoID {
	
	private static Model m_model = ModelFactory.createDefaultModel();
	
	public static String prefix = "void";
	public static String ns     = "http://rdfs.org/ns/void#";

	public static final Resource Dataset         = m_model.createResource(ns+"Dataset");
	public static final Property subset          = m_model.createProperty(ns+"subset");	
	public static final Property sparqlEndpoint  = m_model.createProperty(ns+"sparqlEndpoint");	
	public static final Property triples         = m_model.createProperty(ns+"triples");	
	public static final Property uriSpace        = m_model.createProperty(ns+"uriSpace");
	public static final Property vocabulary      = m_model.createProperty(ns+"vocabulary");	
	public static final Property exampleResource = m_model.createProperty(ns+"exampleResource");	
	public static final Property dataDump        = m_model.createProperty(ns+"dataDump");
	
	public static final Resource Linkset         = m_model.createResource(ns+"Linkset");
	public static final Property target          = m_model.createProperty(ns+"target");	
}