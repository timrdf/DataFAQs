package tw.rpi.edu.datafaqs.treedumps;

import org.restlet.Component;
import org.restlet.data.Protocol;
import org.restlet.routing.VirtualHost;

/**
 * @author Joshua Shinavier (http://fortytwo.net)
 */
public class TreeDumpsRippleService {

    public TreeDumpsRippleService() throws Exception {
        // https://github.com/timrdf/DataFAQs/wiki/FAqT-Service
        int serverPort = 9119;

        Component component = new Component();
        component.getServers().add(Protocol.HTTP, serverPort);

        VirtualHost host = component.getDefaultHost();

        host.attach("/check", new DumpResource());

        component.start();
    }

    public static void main(final String[] args) throws Exception {
        new TreeDumpsRippleService();
    }
}
