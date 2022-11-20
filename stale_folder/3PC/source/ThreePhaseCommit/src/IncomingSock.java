/**
 * This code may be modified and used for non-commercial 
 * purposes as long as attribution is maintained.
 * 
 * @author: Isaac Levy
 */

//package ut.distcomp.framework;

import java.io.BufferedInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.Socket;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ConcurrentLinkedQueue;

public class IncomingSock extends Thread {
	final static String MSG_SEP = "&";
	Socket sock;
	InputStream in;
	private volatile boolean shutdownSet;
	private final ConcurrentLinkedQueue<String> queue;
	int bytesLastChecked = 0;
	
	protected IncomingSock(Socket sock) throws IOException {
		this.sock = sock;
		in = new BufferedInputStream(sock.getInputStream());
		//in = sock.getInputStream();
		sock.shutdownOutput();
		queue = new ConcurrentLinkedQueue<String>();
	}
	
	protected List<String> getMsgs() {
		List<String> msgs = new ArrayList<String>();
		String tmp;
		while((tmp = queue.poll()) != null)
			msgs.add(tmp);
		return msgs;
	}
	
	public void run() {
		while (!shutdownSet) {
			try {
				int avail = in.available();
				if (avail == bytesLastChecked) {
					sleep(10);
				} else {
					in.mark(avail);
					byte[] data = new byte[avail];
					in.read(data);
					String dataStr = new String(data);
					int curPtr = 0;
					int curIdx;
					while ((curIdx = dataStr.indexOf(MSG_SEP, curPtr)) != -1) {
						queue.offer(dataStr.substring(curPtr, curIdx));
						curPtr = curIdx + 1;
					}
					in.reset();
					in.skip(curPtr);
					bytesLastChecked = avail - curPtr;
				}
			} catch (IOException e) {
				e.printStackTrace();
			} catch (InterruptedException e) {
				e.printStackTrace();
			}
		}
		
		shutdown();
	}
	
	public void cleanShutdown() {
		shutdownSet = true;
	}
	
	protected void shutdown() {
		try { in.close(); } catch (IOException e) {}
		
		try { 
			sock.shutdownInput();
			sock.close(); }			
		catch (IOException e) {}
	}
}
