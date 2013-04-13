package edu.rpi.tw.data.rdf.jena.vocabulary;

import com.hp.hpl.jena.rdf.model.Model;
import com.hp.hpl.jena.rdf.model.ModelFactory;
import com.hp.hpl.jena.rdf.model.Property;

public class OV {
	
	private static Model m_model = ModelFactory.createDefaultModel();
	
	public static String prefix = "ov";
	public static String ns     = "http://open.vocab.org/terms/";

	//public static final Resource Evaluated      = m_model.createResource(ns+"Evaluated");

	public static final Property shortName = m_model.createProperty(ns+"shortName");
}