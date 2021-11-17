package com.ftnet;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.io.InputStream;
import java.net.ServerSocket;
import java.net.Socket;


public class ServerListener implements Runnable{
    ServerSocket serverSocket;
    protected static Logger log = LoggerFactory.getLogger(ServerListener.class.getSimpleName());

    ServerListener() {
        try {
            serverSocket = new ServerSocket(6666);
        } catch (IOException e) {
            e.printStackTrace();
        }

    }
    private void read(Socket socket) {
        try {
            log.debug("reading from socket");
            byte[] buffer = new byte[1024];
            int read;
            InputStream is = socket.getInputStream();
            while((read = is.read(buffer)) != -1) {
                String output = new String(buffer, 0, read);
                log.debug("Socket output:\n" + output);
            };
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
        try {
            log.info("Starting to listen for incoming connections");
            while(true) {
                Socket socket = this.serverSocket.accept();
                read(socket);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
