package edu.rpi.tw.data.rdf.jena.vocabulary;

import com.hp.hpl.jena.rdf.model.Model;
import com.hp.hpl.jena.rdf.model.ModelFactory;
import com.hp.hpl.jena.rdf.model.Property;
import com.hp.hpl.jena.rdf.model.Resource;

public class Tag {
	
	private static Model m_model = ModelFactory.createDefaultModel();
	
	public static String prefix = "tag";
	public static String ns     = "http://www.holygoat.co.uk/owl/redwood/0.1/tags/";

	public static final Resource Tag            = m_model.createResource(ns+"Tag");

	public static final Property taggedWithTag  = m_model.createProperty(ns+"taggedWithTag");
	public static final Property name           = m_model.createProperty(ns+"name");
}