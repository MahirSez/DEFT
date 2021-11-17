package com.ftnet;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.io.PrintWriter;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

public class HostCommand implements Runnable{

    private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);
    protected static Logger log = LoggerFactory.getLogger(HostCommand.class.getSimpleName());
    private final Socket sock;
    HostCommand() {
        this.sock = new Socket();
    }

    private boolean connectSocket() {
        if (!this.sock.isConnected()) {
            try {
                String hostIP = "192.168.1.1";
                int port = 8080;
                log.debug("Attempting to connect to socket");
                this.sock.connect(new InetSocketAddress(hostIP, port));
                log.debug("Socket connection successful");

            } catch (IOException e) {
                log.error("Failed to connect to host");
                return false;
            }
        }
        return true;
    }

    private void writeCommand() {
        try {
            log.debug("sending start command" );
            PrintWriter out = new PrintWriter(this.sock.getOutputStream());
            out.println("start");
//            out.println(String.format("%s %s %d %d", command, "capture.pcap", this.rate, this.numPkts));
            out.flush();
            sock.close();
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
        log.debug("HostCommand called after every 2 seconds");
        if(connectSocket()) writeCommand();
        log.debug("Scheduling after 2 seconds");
        scheduler.schedule(new HostCommand(),2, TimeUnit.SECONDS);
    }
}
