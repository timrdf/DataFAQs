package tw.rpi.edu.datafaqs.treedumps;

import net.fortytwo.flow.Collector;
import net.fortytwo.linkeddata.sail.LinkedDataSail;
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
import org.openrdf.rio.RDFHandlerException;
import org.openrdf.rio.RDFParseException;
import org.openrdf.rio.RDFWriter;
import org.openrdf.rio.Rio;
import org.openrdf.sail.Sail;
import org.openrdf.sail.SailException;
import org.openrdf.sail.memory.MemoryStore;
import org.restlet.Request;
import org.restlet.Response;
import org.restlet.Restlet;
import org.restlet.data.MediaType;
import org.restlet.data.Method;
import org.restlet.data.Preference;
import org.restlet.data.Status;
import org.restlet.representation.Representation;
import org.restlet.representation.StringRepresentation;
import org.restlet.resource.ResourceException;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.Collection;

/**
 * @author Joshua Shinavier (http://fortytwo.net)
 */
public class DumpResource extends Restlet {
    @Override
    public void handle(final Request request,
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

        String findDatasetsQuery = "void:Dataset rdf:type~. void:subset* distinct.";
        String findDumpsQuery = findDatasetsQuery + " void:dataDump. distinct.";

        // Tally the % of void:Datasets that have void:dataDumps.
        /*String makeAssertionsQuery = "@prefix datafaqs: <http://purl.org/twc/vocab/datafaqs#>\n" +
                "void:Dataset rdf:type~. = sets\n" +
                "sets. void:subset* distinct. = subsets\n" +
                "subsets apply count. top. = total\n" +
                "subsets. void:dataDump count. top. = dumps\n" +
                "dumps. 100 mul. total. div. = coverage\n" +
                "sets. rdfs:comment coverage. to-string. \"% coverage\" concat. assert.\n" +
                "sets. coverage. 75 lt. (rdf:type datafaqs:Unsatisfactory assert.) scrap branch.";*/

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

        RDFFormat outFormat = getPreferredRDFFormat(request);

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

                LinkedDataSail lds = new LinkedDataSail(sail);
                lds.initialize();

                Collection<RippleList> datasets = doRippleQuery(lds, findDatasetsQuery);
                System.out.println("dataset results:");
                for (RippleList l : datasets) {
                    System.out.println("\t" + l.getFirst());
                }
                
                Collection<RippleList> dumps = doRippleQuery(lds, findDumpsQuery);
                System.out.println("data dump results:");
                for (RippleList l : dumps) {
                    System.out.println("\t" + l.getFirst());
                }

                //Collection<RippleList> results = doRippleQuery(lds, makeAssertionsQuery);

                /*
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
                } */

                Representation rep = createResponseEntity(sail, outFormat);
                response.setEntity(rep);
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
        } catch (RDFHandlerException e) {
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

            p.close();

            return r;
        } finally {
            m.shutDown();
        }
    }

    private Representation createResponseEntity(final Sail sail,
                                                final RDFFormat format) throws IOException, RepositoryException, RDFHandlerException {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        try {
            Repository r = new SailRepository(sail);
            RepositoryConnection rc = r.getConnection();
            try {
                RDFWriter w = Rio.createWriter(format, out);
                rc.export(w);
            } finally {
                rc.close();
            }

            Representation rep = new StringRepresentation(new String(out.toByteArray()));
            rep.setMediaType(new MediaType(format.getDefaultMIMEType()));
            return rep;
        } finally {
            out.close();
        }
    }

    private RDFFormat getPreferredRDFFormat(final Request request) {
        float maxQuality = -1;
        RDFFormat best = null;

        for (Preference<MediaType> p : request.getClientInfo().getAcceptedMediaTypes()) {
            RDFFormat f = RDFFormat.forMIMEType(p.getMetadata().getName());
            if (null != f) {
                float q = p.getQuality();
                if (q > maxQuality) {
                    best = f;
                    maxQuality = q;
                }
            }
        }

        return null == best ? RDFFormat.RDFXML : best;
    }
}
