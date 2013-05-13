package edu.rpi.tw.data.rdf.jena.vocabulary;

import java.util.HashMap;

import com.hp.hpl.jena.rdf.model.Model;
import com.hp.hpl.jena.vocabulary.DC;

/**
 * 
 */
public class Prefixes {
	
	private static HashMap<String,String> prefixes = new HashMap<String,String>();
	static {
		prefixes.put(CON.prefix,      CON.ns);
		prefixes.put(DataFAQs.prefix, DataFAQs.ns);
		prefixes.put(DCAT.prefix,     DCAT.ns);
		prefixes.put("dcterms",       DC.getURI());
		prefixes.put(FOAF.prefix,     FOAF.ns);
		prefixes.put(OV.prefix,       OV.ns);
		prefixes.put(PROV.prefix,     PROV.ns);
		prefixes.put(SD.prefix,       SD.ns);
		prefixes.put(SIO.prefix,      SIO.ns);
		prefixes.put(SIOC.prefix,     SIOC.ns);
		prefixes.put(Tag.prefix,      Tag.ns);
		prefixes.put(VoID.prefix,     VoID.ns);
	}
	
	/**
	 * 
	 * @param model
	 */
	public static void setNsPrefixes(Model model) {
		for( String prefix : prefixes.keySet() ) {
			model.setNsPrefix(prefix, prefixes.get(prefix));			
		}
	}
	
	/**
	 * 
	 * @param prefixes
	 * @return
	 */
	public static String declareTurtlePrefixes(String ... prefixes) {
		return declarePrefixes("@",".",prefixes);
	}
	
	/**
	 * 
	 * @param prefixes
	 * @return
	 */
	public static String declareSPARQLPrefixes(String ... prefixes) {
		return declarePrefixes("","",prefixes);
	}
	
	/**
	 * 
	 * @param strings
	 */
	private static String declarePrefixes(String prepend, String append, String ... prefixes) {
		StringBuffer declaration = new StringBuffer();
		for ( int i = 0; i < prefixes.length; ++i ) {
			String prefix = prefixes[i];
			declaration.append(prepend + "prefix " + prefix + ": <" + Prefixes.prefixes.get(prefix) + "> "+append+"\n");
		}
		return declaration.toString();
	}
}