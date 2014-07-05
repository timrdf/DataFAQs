package edu.rpi.tw.data.quality.sadi.faqt.core.select.datasets;

import org.apache.log4j.Logger;

import ca.wilkinsonlab.sadi.service.annotations.Name;
import ca.wilkinsonlab.sadi.service.annotations.Description;
import ca.wilkinsonlab.sadi.service.annotations.ContactEmail;
import ca.wilkinsonlab.sadi.service.annotations.InputClass;
import ca.wilkinsonlab.sadi.service.annotations.OutputClass;
import ca.wilkinsonlab.sadi.service.simple.SimpleSynchronousServiceServlet;

import com.hp.hpl.jena.rdf.model.Model;
import com.hp.hpl.jena.rdf.model.ModelFactory;
import com.hp.hpl.jena.rdf.model.Property;
import com.hp.hpl.jena.rdf.model.Resource;
//import com.hp.hpl.jena.rdf.model.Statement;
//import com.hp.hpl.jena.rdf.model.StmtIterator;

@Name("select-datasets-by-ckan-group")
@Description("Links a CKAN group to the datasets that are in the group.")
@ContactEmail("lebot@rpi.edu")
@InputClass("http://www.w3.org/ns/prov#Entity")
@OutputClass("http://www.w3.org/ns/prov#Entity")
public class ByCKANGroup extends SimpleSynchronousServiceServlet
{
	private static final Logger log = Logger.getLogger(ByCKANGroup.class);
	private static final long serialVersionUID = 1L;

	@Override
	public void processInput(Resource input, Resource output)
	{
		/* your code goes here
		 * (add properties to output node based on properties of input node...)
		 */
	}

	@SuppressWarnings("unused")
	private static final class Vocab
	{
		private static Model m_model = ModelFactory.createDefaultModel();
		
		public static final Resource Entity = m_model.createResource("http://www.w3.org/ns/prov#Entity");
	}
}
