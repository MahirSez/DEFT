import java.awt.List;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.Scanner;
import java.util.StringTokenizer;


public class Client {

	public static long TimeoutTime = 60000; //in ms
	
	private long timeout;
	private int reqNum = 0;
	
	Client() {
		
	}
	
	public void run() {
		this.timeout = -1;
		
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		
		while(true) {
			java.util.List<String> incomingMessages = ThreePhaseCommit.net.getReceivedMsgs();
			if(incomingMessages.size() == 0) {
				try {
					Thread.sleep(5);
				} catch (InterruptedException e) {
					e.printStackTrace();
				}
			}
			for(String message: incomingMessages) {
				parseMessage(message);
			}
			if(this.timeout != -1 && System.currentTimeMillis() > this.timeout) {
				timeout();
			}
			//get user input
			try {
				if ( br.ready() ) {
					String userInput = br.readLine();
					createRequest(userInput);
				}
			} catch (IOException e) {
				e.printStackTrace();
			}
		}	
	}
	
	private void resetTimeout() {
		this.timeout = System.currentTimeMillis() + TimeoutTime;
	}
	private void stopTimeout() {
		this.timeout = -1;
	}
	
	void timeout() {
		
	}
	private void createRequest(String userInput)
	{
		if(userInput.indexOf('|') != -1 || userInput.indexOf('&') != -1) {
			System.out.println("You may not use '|' or '&'");
			return;
		}
		
		Scanner sc = new Scanner(System.in);
		String song =null;
		String url = null;
		String request = "REQUEST|" + this.reqNum + "|";
		this.reqNum += 1;
		if(userInput.equals("add")) {
			System.out.print("Song name: ");
			song = sc.nextLine();
			if(song.indexOf('|') != -1 || song.indexOf('&') != -1) {
				System.out.println("\nYou may not use '|' or '&'");
				return;
			}
			System.out.print("\nURL: ");
			url = sc.nextLine();
			if(url.indexOf('|') != -1 || url.indexOf('&') != -1) {
				System.out.println("\nYou may not use '|' or '&'");
				return;
			}
			System.out.println("");
			request += "add|" + song +"|" + url;
			broadcast(request);
		}
		else if (userInput.equals("edit")) {
			System.out.print("Song name: ");
			song = sc.nextLine();
			if(song.indexOf('|') != -1 || song.indexOf('&') != -1) {
				System.out.println("\nYou may not use '|' or '&'");
				return;
			}
			System.out.print("\nURL: ");
			url = sc.nextLine();
			if(url.indexOf('|') != -1 || url.indexOf('&') != -1) {
				System.out.println("\nYou may not use '|' or '&'");
				return;
			}
			System.out.println("");
			request += "edit|" + song +"|" + url;
			broadcast(request);
		}
		else if(userInput.equals("delete")) {
			System.out.print("Song name: ");
			song = sc.nextLine();
			if(song.indexOf('|') != -1 || song.indexOf('&') != -1) {
				System.out.println("\nYou may not use '|' or '&'");
				return;
			}
			System.out.println("");
			request += "delete|" + song;
			broadcast(request);
		}
		else if(userInput.equals("halt")) {
			broadcast("halt");
			ThreePhaseCommit.net.shutdown();
			System.exit(0);
		}
		else if(userInput.equals("kill")) {
			System.out.print("Which node should we kill? ");
			int p = sc.nextInt();
			ThreePhaseCommit.net.sendMsg(p, "halt");
		}
		else {
			System.out.println("Error, valid commands are add, edit, and delete.");
		}
		
	}
	private void parseMessage(String message) {
		//java.util.List<String> messageList = (java.util.List<String>) new List();
		StringTokenizer st = new StringTokenizer(message, "|");
		
		System.out.print("\"");
		while(st.hasMoreTokens())
		{
			System.out.print(st.nextToken()+ " ");
			
		}
		
		System.out.println("\" is successful.");
	}
	
	private void broadcast(String message) {
		for(int iii = 0; iii < ThreePhaseCommit.totalNumber - 1; iii++) {
			ThreePhaseCommit.net.sendMsg(iii, message);
		}
	}

	
}
