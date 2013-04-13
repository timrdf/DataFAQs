package edu.rpi.tw.data.rdf.jena.vocabulary;

import com.hp.hpl.jena.rdf.model.Model;
import com.hp.hpl.jena.rdf.model.ModelFactory;
import com.hp.hpl.jena.rdf.model.Property;

public class SIO {
	private static Model m_model = ModelFactory.createDefaultModel();
	public static String prefix = "sio";
	public static String ns = "http://semanticscience.org/resource/";

	public static final Property count        = m_model.createProperty(ns+"count");		
}
