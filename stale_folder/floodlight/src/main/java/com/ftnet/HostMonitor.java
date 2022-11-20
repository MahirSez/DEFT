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

/**
 * Client monitor
 * Sends command to hosts on a regular interval
*/
public class HostMonitor implements Runnable{

    private final int DELAY = 5;
    private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);
    protected static Logger log = LoggerFactory.getLogger(HostMonitor.class.getSimpleName());
    private final FTManager ftManager;
    private final int HOST_PORT = 8080;

    HostMonitor(FTManager ftManager) {
        this.ftManager = ftManager;
    }

    private Socket connectSocket(String hostIP) {
        Socket socket = new Socket();
        if (!socket.isConnected()) {
            try {
                log.debug("Attempting to connect to " + hostIP + " on port " + HOST_PORT) ;
                socket.connect(new InetSocketAddress(hostIP, HOST_PORT));
                log.debug("Socket connection successful with " + hostIP);
            } catch (IOException e) {
                log.error("Failed to connect to host " + hostIP);
                return null;
            }
        }
        return socket;
    }

    private void writeCommand(String hostIP, Socket socket) {
        assert socket.isConnected();
        try {
            log.debug("sending start command to " + hostIP );
            PrintWriter out = new PrintWriter(socket.getOutputStream());
            out.println("packet_count " + hostIP);
            out.flush();
        }
        catch (IOException e) {
            e.printStackTrace();
            log.error("Error occurred while sending command");
        }
        try {
            socket.close();
        } catch (IOException e) {
            e.printStackTrace();
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
        log.debug("HostCommand called after every " + DELAY + " seconds");

        for(String ip: ftManager.getHosts()) {
            Socket socket =connectSocket(ip);
            if(socket != null) writeCommand(ip, socket);
        }

        log.debug("Scheduling after " + DELAY + " seconds");
        scheduler.schedule(new HostMonitor(ftManager), DELAY, TimeUnit.SECONDS);
    }
}
