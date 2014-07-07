package edu.rpi.tw.data.ckan;

import org.apache.log4j.Logger;

import com.hp.hpl.jena.rdf.model.Model;
import com.hp.hpl.jena.rdf.model.ModelFactory;
import com.hp.hpl.jena.rdf.model.Resource;
import com.hp.hpl.jena.vocabulary.DC;

import edu.rpi.tw.data.rdf.jena.vocabulary.DataFAQs;
import edu.rpi.tw.data.rdf.jena.vocabulary.PROV;

/**
 * Java implementation of https://github.com/timrdf/DataFAQs/blob/master/src/python/faqt.python/faqt/faqt.py#L168
 */
public class CKANReader {
	
   private static final Logger log = Logger.getLogger(CKANReader.class);
   
	/**
	 * e.g. http://datahub.io/dataset/farmers-markets-geographic-data-united-states -> http://datahub.io
	 * 
	 * @param dataset
	 * @return
	 */
	public static String getBaseURI(Resource dataset) {
		return dataset.asResource().getURI().toString().replaceFirst("\\/dataset\\/.*$", "")
		      .replaceFirst("\\/group\\/.*$", "")
		      .replaceFirst("\\/tag\\/.*$", "");
	}
	
	/** 
	 * 'http://healthdata.tw.rpi.edu/hub/dataset/2010-basic-stand-alone-home'        -> 'http://healthdata.tw.rpi.edu/hub' + '/api'
	 * 'http://thedatahub.org/dataset/farmers-markets-geographic-data-united-states' -> 'http://thedatahub.org' + '/api'	
	 */
	public static String getCKANAPI(Resource dataset) {

		String base = null;
		
		// ?dataset prov:wasAttributedTo [ a datafaqs:CKAN ]
		if( dataset.hasProperty(PROV.wasAttributedTo) ) { 
			
			// TODO
		}
		
		// ?dataset
		String datasetS = dataset.getURI().toString();
		if( base == null && datasetS.matches("^.*/dataset/.*") ) {

			base = datasetS.replaceFirst("/dataset/.*$", "");
		}else if( base == null && datasetS.matches("^.*/group/.*") ) {

         base = datasetS.replaceFirst("/group/.*$", "");
      }
		else if( base == null && datasetS.matches("^.*/tag/.*") ) {

         base = datasetS.replaceFirst("/tag/.*$", "");
      }
		log.warn("ckan API of "+dataset.toString()+" : "+base);
		return base != null ? base : null;
	}
	
	/**
	 * 'http://datahub.io/dataset/farmers-markets-geographic-data-united-states' -> 'farmers-markets-geographic-data-united-states'
	 */
	public static String getCKANIdentifier(Resource dataset) {
		
		if( dataset.hasProperty(DataFAQs.ckan_identifier) ) { 
			return dataset.getProperty(DataFAQs.ckan_identifier).getObject().asLiteral().getString();
			
		}else if( dataset.hasProperty(DC.identifier) ) {
			return dataset.getProperty(DC.identifier).getObject().asLiteral().getString();
			
		}else if( dataset.asResource().getURI().matches("^.*/dataset/.*") ) {
			return dataset.asResource().getURI().replaceAll("^.*/dataset/","");
			
		}else if( dataset.asResource().getURI().matches("^.*/group/.*") ) {
         return dataset.asResource().getURI().replaceAll("^.*/group/","");
         
      }else if( dataset.asResource().getURI().matches("^.*/tag/.*") ) {
         return dataset.asResource().getURI().replaceAll("^.*/tag/","");
         
      }
		return dataset.asResource().getURI().replaceAll("^.*/dataset/", "");
	}
	
	/**
	 * 
	 * @param args
	 */
	public static void main(String args[]) {
		Model m = ModelFactory.createDefaultModel();
		System.out.println(CKANReader.getCKANAPI(m.createResource("http://healthdata.tw.rpi.edu/hub/dataset/2010-basic-stand-alone-home")));
		System.out.println(CKANReader.getCKANAPI(m.createResource("http://datahub.io/dataset/farmers-markets-geographic-data-united-states")));
		
		System.out.println(CKANReader.getCKANIdentifier(m.createResource("http://thedatahub.org/dataset/uk-postcodes")));
		System.out.println(CKANReader.getCKANIdentifier(m.createResource("http://datahub.io/dataset/klappstuhlclub")));
	}
}