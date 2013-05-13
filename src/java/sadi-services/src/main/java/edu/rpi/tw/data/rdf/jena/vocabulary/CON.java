package edu.rpi.tw.data.rdf.jena.vocabulary;

import com.hp.hpl.jena.rdf.model.Model;
import com.hp.hpl.jena.rdf.model.ModelFactory;
import com.hp.hpl.jena.rdf.model.Property;

public class CON {
	private static Model m_model = ModelFactory.createDefaultModel();
	
	public static String prefix = "con";
	public static String ns     = "http://www.w3.org/2000/10/swap/pim/contact#";

	//public static final Resource Dataset      = m_model.createResource(ns+"Dataset");

	public static final Property preferredURI = m_model.createProperty(ns+"preferredURI");
}
