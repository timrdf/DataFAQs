package edu.rpi.tw.data.quality.sadi.faqt;

import com.hp.hpl.jena.rdf.model.Resource;
import com.hp.hpl.jena.vocabulary.RDF;

import edu.rpi.tw.data.rdf.jena.vocabulary.DataFAQs;

/**
 * 
 */
public class FAqT {
	
	/**
	 * 
	 * @param dataset
	 */
	public static void unsatisfactoryIfNotSatisfactory(Resource dataset) {
		if( !dataset.getModel().contains(dataset, RDF.type, DataFAQs.Satisfactory) ) {
			dataset.addProperty(RDF.type, DataFAQs.Unsatisfactory);
		}
	}
	
	/**
	 * 
	 * @param dataset
	 */
	public static void satisfactoryIfNotUnsatisfactory(Resource dataset) {
		if( !dataset.getModel().contains(dataset, RDF.type, DataFAQs.Satisfactory) ) {
			dataset.addProperty(RDF.type, DataFAQs.Satisfactory);
		}
	}
}