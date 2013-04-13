package edu.rpi.tw.data.rdf.jena.vocabulary;

import com.hp.hpl.jena.rdf.model.Model;
import com.hp.hpl.jena.rdf.model.ModelFactory;
import com.hp.hpl.jena.rdf.model.Property;
import com.hp.hpl.jena.rdf.model.Resource;

public class DataFAQs {
	
	private static Model m_model = ModelFactory.createDefaultModel();
	
	public static String prefix = "datafaqs";
	public static String ns     = "http://purl.org/twc/vocab/datafaqs#";

	public static final Resource Evaluated      = m_model.createResource(ns+"Evaluated");
	public static final Resource Satisfactory   = m_model.createResource(ns+"Satisfactory");
	public static final Resource Unsatisfactory = m_model.createResource(ns+"Unsatisfactory");
	
	public static final Property ckan_identifier = m_model.createProperty(ns+"ckan_identifier");
	public static final Property todo = m_model.createProperty(ns+"todo");
	

	public static final Resource CKANDataset = m_model.createResource(ns+"CKANDataset");
	public static final Resource CKANGroup   = m_model.createResource(ns+"CKANGroup");
}
