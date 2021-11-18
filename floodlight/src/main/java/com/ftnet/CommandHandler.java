package com.ftnet;

import net.floodlightcontroller.core.IOFSwitch;
import net.floodlightcontroller.packet.Ethernet;
import net.floodlightcontroller.packet.IPv4;
import org.openflow.protocol.OFFlowMod;
import org.openflow.protocol.OFMatch;
import org.openflow.protocol.OFPacketOut;
import org.openflow.protocol.OFPort;
import org.openflow.protocol.action.OFAction;
import org.openflow.protocol.action.OFActionOutput;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.io.InputStream;
import java.io.PrintWriter;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.util.ArrayList;

public class CommandHandler implements Runnable {

    private final String READY = "ready";
    private final String START = "start";
    private final String OVERLOAD = "overload";
    private final String TERMINATE = "terminate";
    private static final short DEFAULT_PRIORITY = 1000;
    private static final short TIMEOUT_PERMANENT = 0;


    private final Socket socket;
    protected static Logger log = LoggerFactory.getLogger(CommandHandler.class.getSimpleName());
    private final FTManager ftManager;
    private final String ipAddr;

    CommandHandler(Socket socket, FTManager ftManager) {
        this.ftManager = ftManager;
        this.socket = socket;
        this.ipAddr = ((InetSocketAddress) this.socket.getRemoteSocketAddress()).getAddress().getHostAddress();
        log.debug("Connected with ip "+ ipAddr );
    }

    private void addFlow(int srcPort, int dstPort) {
        OFFlowMod rule = changeFlow(srcPort, dstPort, OFFlowMod.OFPFC_ADD);
        if(rule != null) log.debug("Installed rule: " + rule);
    }
    private void delFlow(int srcPort, int dstPort) {
        OFFlowMod rule = changeFlow(srcPort, dstPort, OFFlowMod.OFPFC_DELETE);
        if(rule != null) log.debug("Deleted rule: " + rule);
    }

    private OFFlowMod changeFlow(int srcPort, int dstPort, short flowCmd ) {
        if(ftManager.getSwitch() == null) {
            log.error("Switch not set in yet");
            return null;
        }

        OFFlowMod rule = new OFFlowMod();
        rule.setCommand(flowCmd);
        rule.setPriority(DEFAULT_PRIORITY);
        rule.setBufferId(OFPacketOut.BUFFER_ID_NONE);
        rule.setHardTimeout(TIMEOUT_PERMANENT);
        rule.setIdleTimeout(TIMEOUT_PERMANENT);

        ArrayList<OFAction> actions = new ArrayList<OFAction>();
        actions.add(new OFActionOutput((short)dstPort));
        rule.setActions(actions);
        rule.setLength((short) (OFFlowMod.MINIMUM_LENGTH + (OFActionOutput.MINIMUM_LENGTH * actions.size())));
        rule.setOutPort((flowCmd == OFFlowMod.OFPFC_DELETE) ? (short)dstPort: OFPort.OFPP_NONE.getValue());

        OFMatch match = new OFMatch();
        match.setDataLayerType(Ethernet.TYPE_IPv4);
        match.setNetworkProtocol(IPv4.PROTOCOL_TCP);
        match.setInputPort((short) srcPort);
        match.setWildcards(OFMatch.OFPFW_ALL ^ OFMatch.OFPFW_DL_TYPE ^ OFMatch.OFPFW_NW_PROTO ^ OFMatch.OFPFW_IN_PORT);
//        log.debug(String.valueOf(rule));
//        log.debug(String.valueOf(match));

        rule.setMatch(match);
        IOFSwitch sw = ftManager.getSwitch();
        // Install the rule
        try
        {
            sw.write(rule, null);
            sw.flush();
        }
        catch (Exception e)
        { e.printStackTrace(); }
        return rule;

    }
    private void send(String cmd) {
        try {
            log.debug("Sending output");
            PrintWriter out = new PrintWriter(this.socket.getOutputStream());
            out.println(cmd);
            out.flush();
            socket.close();
        }
        catch (IOException e) {
            log.error("Error occurred while sending command");
        }
    }

    private void handle(String output) {
        log.debug(ipAddr + " said: " + output);
        switch (output) {
            case READY:
                addFlow(5, 1);
                send(START);
                break;
            case OVERLOAD:
                addFlow(5, 2);
                delFlow(5, 1);
                break;
            case TERMINATE:
                delFlow(5, 2);
                break;
        }

    }

    private void serve() {
        try {
            log.debug("reading from socket");
            byte[] buffer = new byte[1024];
            int read;
            InputStream is = socket.getInputStream();
            while((read = is.read(buffer)) != -1) {
                String output = new String(buffer, 0, read);
                handle(output.replaceAll("\\s+",""));
            }
            socket.close();
        }
        catch (IOException e) {
            log.error("Error occurred while sending command");
        }
    }

    /**
     * When an object implementing interface <code>Runnable</code> is used
     * to create a thread, starting the thread causes the object's
     * <code>run</code> method to be called in that separately executing
     * thread.
     * <p>
     * The general contract of the method <code>run</code> is that it may
     * take any action whatsoever.
     *
     * @see Thread#run()
     */
    @Override
    public void run() {
        serve();
    }

}
