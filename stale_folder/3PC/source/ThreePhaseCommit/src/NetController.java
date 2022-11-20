/**
 * This code may be modified and used for non-commercial 
 * purposes as long as attribution is maintained.
 * 
 * @author: Isaac Levy
 */

/**
* The sendMsg method has been modified by Navid Yaghmazadeh to fix a bug regarding to send a message to a reconnected socket.
*/

//package ut.distcomp.framework;

import java.io.IOException;
import java.net.Socket;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.ListIterator;
import java.util.logging.Level;

/**
 * Public interface for managing network connections.
 * You should only need to use this and the Config class.
 * @author ilevy
 *
 */
public class NetController {
	private final Config config;
	private final List<IncomingSock> inSockets;
	private final OutgoingSock[] outSockets;
	private final ListenServer listener;
	
	private static final boolean netDebug = false;
	
	public NetController(Config config) {
		this.config = config;
		inSockets = Collections.synchronizedList(new ArrayList<IncomingSock>());
		listener = new ListenServer(config, inSockets);
		outSockets = new OutgoingSock[config.numProcesses];
		listener.start();
	}
	
	// Establish outgoing connection to a process
	private synchronized void initOutgoingConn(int proc) throws IOException {
		if (outSockets[proc] != null)
			throw new IllegalStateException("proc " + proc + " not null");
		
		outSockets[proc] = new OutgoingSock(new Socket(config.addresses[proc], config.ports[proc]));
		if(netDebug) {
			config.logger.info(String.format("Server %d: Socket to %d established", config.procNum, proc));
		}
	}
	
	/**
	 * Send a msg to another process.  This will establish a socket if one is not created yet.
	 * Will fail if recipient has not set up their own NetController (and its associated serverSocket)
	 * @param process int specified in the config file - 0 based
	 * @param msg Do not use the "&" character.  This is hardcoded as a message separator. 
	 *            Sends as ASCII.  Include the sending server ID in the message
	 * @return bool indicating success
	 */
	public synchronized boolean sendMsg(int process, String msg) {
		try {
			if (outSockets[process] == null) {
				initOutgoingConn(process);
			}
			outSockets[process].sendMsg(msg);
		} catch (IOException e) { 
			if (outSockets[process] != null) {
				outSockets[process].cleanShutdown();
				outSockets[process] = null;
				try{
					initOutgoingConn(process);
                        		outSockets[process].sendMsg(msg);	
				} catch(IOException e1){
					if (outSockets[process] != null) {
						outSockets[process].cleanShutdown();
	                	outSockets[process] = null;
					}
					if(netDebug) {
						config.logger.info(String.format("Server %d: Msg to %d failed.",
								config.procNum, process));
						config.logger.log(Level.FINE, String.format("Server %d: Socket to %d error",
								config.procNum, process), e);
					}
                    return false;
				}
				return true;
			}
			if(netDebug) {
				config.logger.info(String.format("Server %d: Msg to %d failed.", 
						config.procNum, process));
				config.logger.log(Level.FINE, String.format("Server %d: Socket to %d error", 
						config.procNum, process), e);
			}
			return false;
		}
		return true;
	}
	
	/**
	 * Return a list of msgs received on established incoming sockets
	 * @return list of messages sorted by socket, in FIFO order. *not sorted by time received*
	 */
	public synchronized List<String> getReceivedMsgs() {
		List<String> objs = new ArrayList<String>();
		synchronized(inSockets) {
			ListIterator<IncomingSock> iter  = inSockets.listIterator();
			while (iter.hasNext()) {
				IncomingSock curSock = iter.next();
				try {
					objs.addAll(curSock.getMsgs());
				} catch (Exception e) {
					if(netDebug) {
						config.logger.log(Level.INFO, 
								"Server " + config.procNum + " received bad data on a socket", e);
					}
					curSock.cleanShutdown();
					iter.remove();
				}
			}
		}
		
		return objs;
	}
	/**
	 * Shuts down threads and sockets.
	 */
	public synchronized void shutdown() {
		listener.cleanShutdown();
        if(inSockets != null) {
		    for (IncomingSock sock : inSockets)
			    if(sock != null)
                    sock.cleanShutdown();
        }
		if(outSockets != null) {
            for (OutgoingSock sock : outSockets)
			    if(sock != null)
                    sock.cleanShutdown();
        }
		
	}

}
