package com.ftnet;

import net.floodlightcontroller.core.FloodlightContext;
import net.floodlightcontroller.core.IOFMessageListener;
import net.floodlightcontroller.core.IOFSwitch;
import net.floodlightcontroller.core.IOFSwitchListener;
import net.floodlightcontroller.packet.Ethernet;
import net.floodlightcontroller.packet.IPv4;
import org.openflow.protocol.*;
import org.openflow.protocol.action.OFAction;
import org.openflow.protocol.action.OFActionOutput;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.ArrayList;
import java.util.List;

public class OFListener implements IOFMessageListener, IOFSwitchListener {

    FTManager ftManager;
    protected static Logger log = LoggerFactory.getLogger(OFListener.class.getSimpleName());


    OFListener(FTManager ftManager) {
        this.ftManager = ftManager;
    }

    /**
     * Fired when a switch is connected to the controller, and has sent
     * a features reply.
     *
     * @param sw
     */
    @Override
    public void addedSwitch(IOFSwitch sw) {
        ftManager.setSwitch(sw);
    }

    /**
     * Fired when a switch is disconnected from the controller.
     *
     * @param sw
     */
    @Override
    public void removedSwitch(IOFSwitch sw) {

    }

    /**
     * Fired when ports on a switch change (any change to the collection
     * of OFPhysicalPorts and/or to a particular port)
     *
     * @param switchId
     */
    @Override
    public void switchPortChanged(Long switchId) {

    }

    /**
     * The name assigned to this listener
     *
     * @return
     */
    @Override
    public String getName() {
        return OFListener.class.getSimpleName();
    }

    /**
     * Check if the module called name is a callback ordering prerequisite
     * for this module.  In other words, if this function returns true for
     * the given name, then this message listener will be called after that
     * message listener.
     *
     * @param type the message type to which this applies
     * @param name the name of the module
     * @return whether name is a prerequisite.
     */
    @Override
    public boolean isCallbackOrderingPrereq(OFType type, String name) {
        return false;
    }

    /**
     * Check if the module called name is a callback ordering post-requisite
     * for this module.  In other words, if this function returns true for
     * the given name, then this message listener will be called before that
     * message listener.
     *
     * @param type the message type to which this applies
     * @param name the name of the module
     * @return whether name is a post-requisite.
     */
    @Override
    public boolean isCallbackOrderingPostreq(OFType type, String name) {
        return false;
    }



    /**
     * This is the method Floodlight uses to call listeners with OpenFlow messages
     *
     * @param sw   the OpenFlow switch that sent this message
     * @param msg  the message
     * @param cntx a Floodlight message context object you can use to pass
     *             information between listeners
     * @return the command to continue or stop the execution
     */
    @Override
    public Command receive(IOFSwitch sw, OFMessage msg, FloodlightContext cntx) {
        if(ftManager.getSwitch() == null) ftManager.setSwitch(sw);
//        log.debug("Got message from " + sw);
//        log.debug("Message  = " + msg );
//
//        OFPacketIn ofMsg = (OFPacketIn) msg;
//
//        log.debug("Got message from " + ofMsg.getInPort());
//
//        if(ofMsg.getInPort() == 4) installFlow(sw);




        return Command.CONTINUE;
    }
}
