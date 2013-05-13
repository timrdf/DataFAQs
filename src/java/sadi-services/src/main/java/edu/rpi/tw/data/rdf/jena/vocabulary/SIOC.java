package edu.rpi.tw.data.rdf.jena.vocabulary;

import com.hp.hpl.jena.rdf.model.Model;
import com.hp.hpl.jena.rdf.model.ModelFactory;
import com.hp.hpl.jena.rdf.model.Property;
import com.hp.hpl.jena.rdf.model.Resource;

public class SIOC {
	
	private static Model m_model = ModelFactory.createDefaultModel();
	
	public static String prefix = "sioc";
	public static String ns     = "http://rdfs.org/sioc/ns#";

	public static final Resource Item            = m_model.createResource(ns+"Item");

	public static final Property ip_address     = m_model.createProperty(ns+"ip_address");
	
}