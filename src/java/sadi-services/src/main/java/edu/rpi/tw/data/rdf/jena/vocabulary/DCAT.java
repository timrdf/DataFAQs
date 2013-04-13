package edu.rpi.tw.data.rdf.jena.vocabulary;

import com.hp.hpl.jena.rdf.model.Model;
import com.hp.hpl.jena.rdf.model.ModelFactory;
import com.hp.hpl.jena.rdf.model.Property;
import com.hp.hpl.jena.rdf.model.Resource;

public class DCAT {
	
	private static Model m_model = ModelFactory.createDefaultModel();
	
	public static String prefix = "dcat";
	public static String ns     = "http://www.w3.org/ns/dcat#";

	public static final Resource Dataset      = m_model.createResource(ns+"Dataset");
	public static final Property distribution = m_model.createProperty(ns+"distribution");
	
	public static final Resource Distribution = m_model.createResource(ns+"Distribution");
	public static final Property accessURL   = m_model.createProperty(ns+"accessURL");
}