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
    public void handle(final Request request,
                       final Response response) {
        String baseUri = "http://example.org/baseURI/";
        // TODO: what should the query do?
        String rippleQuery = "insert Ripple query here";

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
