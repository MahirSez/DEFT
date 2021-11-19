package com.ftnet;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.io.InputStream;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;


public class ServerListener implements Runnable{
    ServerSocket serverSocket;
    private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);
    protected static Logger log = LoggerFactory.getLogger(ServerListener.class.getSimpleName());
    private FTManager ftManager;

    ServerListener(FTManager ftManager) {
        try {
            serverSocket = new ServerSocket(6666);
            this.ftManager = ftManager;
        } catch (IOException e) {
            e.printStackTrace();
        }

    }
    private void read(Socket socket) {

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
        try {
            log.info("Starting to listen for incoming connections");
            while(true) {
                Socket socket = this.serverSocket.accept();
                scheduler.schedule(new CommandHandler(socket, ftManager), 0, TimeUnit.SECONDS);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
