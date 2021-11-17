package net.floodlightcontroller.pktinhistory;

import net.floodlightcontroller.restserver.RestletRoutable;
import org.restlet.Context;
import org.restlet.Restlet;
import org.restlet.routing.Router;

public class PktInHistoryWebRoutable implements RestletRoutable {
    /**
     * Get the restlet that will map to the resources
     *
     * @param context the context for constructing the restlet
     * @return the restlet
     */
    @Override
    public Restlet getRestlet(Context context) {
        Router router = new Router(context);
        router.attach("/history/json", PktInHistoryResource.class);
        return router;
    }

    /**
     * Get the base path URL where the router should be registered
     *
     * @return the base path URL where the router should be registered
     */
    @Override
    public String basePath() {
        return "/wm/pktinhistory";
    }
}
