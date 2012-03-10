package tw.rpi.edu.datafaqs.treedumps;

import net.fortytwo.flow.Collector;
import net.fortytwo.ripple.RippleException;
import net.fortytwo.ripple.model.Model;
import net.fortytwo.ripple.model.RippleList;
import net.fortytwo.ripple.model.impl.sesame.SesameModel;
import net.fortytwo.ripple.query.QueryEngine;
import net.fortytwo.ripple.query.QueryPipe;
import org.openrdf.repository.Repository;
import org.openrdf.repository.RepositoryConnection;
import org.openrdf.repository.RepositoryException;
import org.openrdf.repository.sail.SailRepository;
import org.openrdf.rio.RDFFormat;
import org.openrdf.rio.RDFParseException;
import org.openrdf.sail.Sail;
import org.openrdf.sail.SailException;
import org.openrdf.sail.memory.MemoryStore;
import org.openrdf.model.ValueFactory;
import org.openrdf.model.impl.ValueFactoryImpl;
import org.restlet.Request;
import org.restlet.Response;
import org.restlet.Restlet;
import org.restlet.data.MediaType;
import org.restlet.data.Method;
import org.restlet.data.Status;
import org.restlet.representation.Representation;
import org.restlet.representation.StringRepresentation;
import org.restlet.resource.ResourceException;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.Collection;

/**
 * @author Joshua Shinavier (http://fortytwo.net)
 */
public class DumpResource extends Restlet {
    @Override
    public void handle(final Request  request,
                       final Response response) {
        
       /* This is HTTP POSTed to this service:
         @prefix rdf:      <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
         @prefix datafaqs: <http://purl.org/twc/vocab/datafaqs#> .
         @prefix void:     <http://rdfs.org/ns/void#> .
         @prefix owl:      <http://www.w3.org/2002/07/owl#> .
         @prefix con:      <http://www.w3.org/2000/10/swap/pim/contact#> .

         <http://aquarius.tw.rpi.edu/projects/datafaqs/epoch> 
            rdf:type void:Dataset, datafaqs:FAqTBrick;
            void:subset <http://aquarius.tw.rpi.edu/projects/datafaqs/epoch/2012-03-05> ,
                        <http://aquarius.tw.rpi.edu/projects/datafaqs/epoch/2012-03-07> ,
                        <http://aquarius.tw.rpi.edu/projects/datafaqs/epoch/2012-03-09> ,
                        <http://aquarius.tw.rpi.edu/projects/datafaqs/epoch/2012-02-18> .

         <http://aquarius.tw.rpi.edu/projects/datafaqs/epoch/2012-02-18> rdf:type datafaqs:Epoch .
         <http://aquarius.tw.rpi.edu/projects/datafaqs/epoch/2012-02-10> rdf:type datafaqs:Epoch .
         <http://aquarius.tw.rpi.edu/projects/datafaqs/epoch/2012-03-05> rdf:type datafaqs:Epoch .
         <http://aquarius.tw.rpi.edu/projects/datafaqs/epoch/2012-03-09> rdf:type datafaqs:Epoch .
         <http://aquarius.tw.rpi.edu/projects/datafaqs/epoch/2012-03-07> rdf:type datafaqs:Epoch .
        */

        String baseUri = "http://example.org/baseURI/";

        // TODO: obtain http://aquarius.tw.rpi.edu/projects/datafaqs/epoch from POSTed graph
        // (any instance of void:Dataset)

        // TODO: what should the query do?
        //
        // Ripple query 1 of 2:
        //   Walk the subset hierarhy and collect any void:dataDumps they have.
        //   <http://aquarius.tw.rpi.edu/projects/datafaqs/epoch> void:subset* distinct.
        // 
        // Ripple query 2 of 2:
        //   Tally the % of void:Datasets that have void:dataDumps.
        //   <http://aquarius.tw.rpi.edu/projects/datafaqs/epoch> void:subset* void:dataDump. distinct.

        String rippleQuery = "<http://aquarius.tw.rpi.edu/projects/datafaqs/epoch> void:subset* distinct."; // TODO: remove hard code of subject.

        if (request.getMethod() != Method.POST) {
            throw new ResourceException(Status.CLIENT_ERROR_METHOD_NOT_ALLOWED, "you must *POST* RDF content into this service");
        }

        String type = request.getEntity().getMediaType().toString();
        String ent;
        try {
            ent = request.getEntity().getText();
        } catch (IOException e) {
            e.printStackTrace(System.err);
            throw new ResourceException(Status.SERVER_ERROR_INTERNAL, e.toString());
        }

        RDFFormat format = RDFFormat.forMIMEType(type);
        if (null == format) {
            throw new ResourceException(Status.CLIENT_ERROR_UNSUPPORTED_MEDIA_TYPE, "not a known RDF format: " + type);
        }

        try {
            Sail sail = new MemoryStore();
            sail.initialize();
            try {
                Repository r = new SailRepository(sail);
                RepositoryConnection rc = r.getConnection();
                try {
                    InputStream in = new ByteArrayInputStream(ent.getBytes());
                    try {
                        rc.add(in, baseUri, format);
                    } finally {
                        in.close();
                    }

                    rc.commit();
                } finally {
                    rc.close();
                }

                Collection<RippleList> results = doRippleQuery(sail, rippleQuery);

                // TODO: what should the result actually look like?
                // The result should be _all_ of the sail repository.
                // But before returning it, we want to walk the RippleList collection, do some domain-specific logic, 
                // assert a few more triples into the repos, THEN return. One triple is rdf:type datafaqs:Unsatisfactory.
                ValueFactory vf = ValueFactoryImpl.getInstance();
                try {
                    rc.add(vf.createURI("http://aquarius.tw.rpi.edu/projects/datafaqs/epoch"),
                           vf.createURI("http://www.w3.org/1999/02/22-rdf-syntax-ns#"),
                           vf.createURI("http://purl.org/twc/vocab/datafaqs#"));
                    rc.commit();
                } finally {
                    rc.close();
                }

                Representation rep = new StringRepresentation(createResponseEntity(results));
                rep.setMediaType(MediaType.TEXT_PLAIN);
            } finally {
                sail.shutDown();
            }
        } catch (SailException e) {
            e.printStackTrace(System.err);
            throw new ResourceException(Status.SERVER_ERROR_INTERNAL, e.toString());
        } catch (RepositoryException e) {
            e.printStackTrace(System.err);
            throw new ResourceException(Status.SERVER_ERROR_INTERNAL, e.toString());
        } catch (IOException e) {
            e.printStackTrace(System.err);
            throw new ResourceException(Status.SERVER_ERROR_INTERNAL, e.toString());
        } catch (RippleException e) {
            e.printStackTrace(System.err);
            throw new ResourceException(Status.SERVER_ERROR_INTERNAL, e.toString());
        } catch (RDFParseException e) {
            e.printStackTrace(System.err);
            throw new ResourceException(Status.CLIENT_ERROR_NOT_ACCEPTABLE, "parse error: " + e.toString());
        }
    }

    private Collection<RippleList> doRippleQuery(final Sail cache,
                                                 final String query) throws RippleException {
        Model m = new SesameModel(cache);
        try {
            QueryEngine qe = new QueryEngine(m);

            Collector<RippleList> r = new Collector<RippleList>();
            QueryPipe p = new QueryPipe(qe, r);

            p.put(query);

            return r;
        } finally {
            m.shutDown();
        }
    }

    private String createResponseEntity(final Collection<RippleList> results) {
        StringBuilder sb = new StringBuilder();

        sb.append("results (in a temporary plain-text format):\n");
        for (RippleList l : results) {
            sb.append(l).append("\n");
        }
        
        return sb.toString();
    }
}
