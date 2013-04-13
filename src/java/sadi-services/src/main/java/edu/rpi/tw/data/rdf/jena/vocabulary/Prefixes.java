package edu.rpi.tw.data.rdf.jena.vocabulary;

import com.hp.hpl.jena.rdf.model.Model;
import com.hp.hpl.jena.vocabulary.DC;

/**
 * 
 */
public class Prefixes {
	
	/**
	 * 
	 * @param model
	 */
	public static void setNsPrefixes(Model model) {
		
		model.setNsPrefix(CON.prefix,      CON.ns);
		model.setNsPrefix(DataFAQs.prefix, DataFAQs.ns);
		model.setNsPrefix(DCAT.prefix,     DCAT.ns);
		model.setNsPrefix("dcterms",       DC.getURI());
		model.setNsPrefix(FOAF.prefix,     FOAF.ns);
		model.setNsPrefix(OV.prefix,       OV.ns);
		model.setNsPrefix(PROV.prefix,     PROV.ns);
		model.setNsPrefix(SD.prefix,       SD.ns);
		model.setNsPrefix(SIO.prefix,      SIO.ns);
		model.setNsPrefix(Tag.prefix,      Tag.ns);
		model.setNsPrefix(VoID.prefix,     VoID.ns);
	}
}