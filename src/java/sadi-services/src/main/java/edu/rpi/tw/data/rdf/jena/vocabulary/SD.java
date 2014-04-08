package edu.rpi.tw.data.rdf.jena.vocabulary;

import com.hp.hpl.jena.rdf.model.Model;
import com.hp.hpl.jena.rdf.model.ModelFactory;
import com.hp.hpl.jena.rdf.model.Property;
import com.hp.hpl.jena.rdf.model.Resource;

public class SD {
	private static Model m_model = ModelFactory.createDefaultModel();
	public static String prefix = "sd";
	public static String ns = "http://www.w3.org/ns/sparql-service-description#";

	public static final Resource Service         = m_model.createResource(ns+"Service");
	public static final Property endpoint        = m_model.createProperty(ns+"endpoint");		
	public static final Property availableGraphs = m_model.createProperty(ns+"availableGraphs");	
	
	public static final Resource GraphCollection = m_model.createResource(ns+"GraphCollection");
	public static final Property namedGraph      = m_model.createProperty(ns+"namedGraph");
	
	public static final Resource NamedGraph      = m_model.createResource(ns+"NamedGraph");
	public static final Property name            = m_model.createProperty(ns+"name");	
	
}
