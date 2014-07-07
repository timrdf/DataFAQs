package edu.rpi.tw.data.rdf.jena.vocabulary;

import com.hp.hpl.jena.rdf.model.Model;
import com.hp.hpl.jena.rdf.model.ModelFactory;
import com.hp.hpl.jena.rdf.model.Property;
import com.hp.hpl.jena.rdf.model.Resource;

public class WGS {
   
   private static Model m_model = ModelFactory.createDefaultModel();
   
   public static String prefix = "wgs";
   public static String ns     = "http://www.w3.org/2003/01/geo/wgs84_pos#";

   public static final Resource SpatialThing      = m_model.createResource(ns+"SpatialThing");

   
   public static final Property lat  = m_model.createProperty(ns+"lat");
   public static final Property lng = m_model.createProperty(ns+"long");
}