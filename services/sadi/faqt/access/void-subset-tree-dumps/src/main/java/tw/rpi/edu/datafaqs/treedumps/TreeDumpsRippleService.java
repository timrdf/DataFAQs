package tw.rpi.edu.datafaqs.treedumps;

import org.restlet.Component;
import org.restlet.data.Protocol;
import org.restlet.routing.VirtualHost;

/**
 * @author Joshua Shinavier (http://fortytwo.net)
 */
public class TreeDumpsRippleService {

    public TreeDumpsRippleService() throws Exception {
        // TODO: make the port number configurable
        int serverPort = 8118;

        Component component = new Component();
        component.getServers().add(Protocol.HTTP, serverPort);

        VirtualHost host = component.getDefaultHost();

        //router = new Router(component.getContext());
        //context = component.getContext();

        host.attach("/dump", new DumpResource());

        component.start();
    }

    public static void main(final String[] args) throws Exception {
        new TreeDumpsRippleService();
    }
}
