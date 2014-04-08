package edu.rpi.tw.data.rdf.jena.vocabulary;

import com.hp.hpl.jena.rdf.model.Model;
import com.hp.hpl.jena.rdf.model.ModelFactory;
import com.hp.hpl.jena.rdf.model.Property;
import com.hp.hpl.jena.rdf.model.Resource;

public class PROV {

   private static Model m_model = ModelFactory.createDefaultModel();

   public static String prefix = "prov";
   public static String ns = "http://www.w3.org/ns/prov#";

   public static final Resource Entity                  = m_model.createResource(ns+"Entity");

   public static final Property wasInfluencedBy         = m_model.createProperty(ns+"wasInfluencedBy");
   public static final Property wasDerivedFrom          = m_model.createProperty(ns+"wasDerivedFrom");

   public static final Property wasAttributedTo         = m_model.createProperty(ns+"wasAttributedTo");

   public static final Property atLocation              = m_model.createProperty(ns+"atLocation");
   public static final Property value                   = m_model.createProperty(ns+"value");
}