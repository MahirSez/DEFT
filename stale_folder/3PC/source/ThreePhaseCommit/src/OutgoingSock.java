/**
 * This code may be modified and used for non-commercial 
 * purposes as long as attribution is maintained.
 * 
 * @author: Isaac Levy
 */

//package ut.distcomp.framework;

import java.io.IOException;
import java.io.OutputStream;
import java.net.Socket;

public class OutgoingSock {
	final static byte[] MSG_SEP = "&".getBytes();
	Socket sock;
	OutputStream out;
	
	protected OutgoingSock(Socket sock) throws IOException {
		this.sock = sock;
		
		out = sock.getOutputStream();
		sock.shutdownInput();
	}
	
	/** 
	 * Do not use '&' character.  This is a hardcoded separator
	 * @param msg
	 * @throws IOException 
	 */
	protected synchronized void sendMsg(String msg) throws IOException {
		out.write(msg.getBytes());
		out.write(MSG_SEP);
		out.flush();
	}
	
	public synchronized void cleanShutdown() {
		try { out.close(); } 
		catch (IOException e) {}

		try { 
			sock.shutdownOutput();
			sock.close(); 
		} catch (IOException e) {}
	}
}
