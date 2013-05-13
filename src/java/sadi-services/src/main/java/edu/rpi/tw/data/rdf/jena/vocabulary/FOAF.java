package edu.rpi.tw.data.rdf.jena.vocabulary;

import com.hp.hpl.jena.rdf.model.Model;
import com.hp.hpl.jena.rdf.model.ModelFactory;
import com.hp.hpl.jena.rdf.model.Property;

public class FOAF {
	private static Model m_model = ModelFactory.createDefaultModel();
	
	public static String prefix = "foaf";
	public static String ns     = "http://xmlns.com/foaf/0.1/";
	
	public static final Property knows = m_model.createProperty(ns+"knows");
}
