package edu.rpi.tw.data.rdf.jena.vocabulary;

import com.hp.hpl.jena.rdf.model.Model;
import com.hp.hpl.jena.rdf.model.ModelFactory;
import com.hp.hpl.jena.rdf.model.Property;
import com.hp.hpl.jena.rdf.model.Resource;

/**
 * 
 */
public class GeoNames {
   
   private static Model m_model = ModelFactory.createDefaultModel();
   
   public static String prefix = "geonames";
   public static String ns     = "http://www.geonames.org/ontology#";

   public static final Resource WikipediaArticle = m_model.createResource(ns+"WikipediaArticle");
   
   public static final Property parentFeature = m_model.createProperty(ns+"parentFeature");
   public static final Property nearby        = m_model.createProperty(ns+"nearby");
}