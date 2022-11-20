import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Set;
import java.util.StringTokenizer;


public class Node {

	public long TimeoutTime = 1000; //in ms
	public long cycleSleepTime = 5;
	
	public boolean isPrimary;
	public String state;
	public long timeout = -1;
	public int reqNum;
	public String action;
	public String song;
	public String url;
	public String decision;
	public Set<Integer> upSet;
	public Set<Integer> responsesToVoteREQ;
	public Set<Integer> currentlyAlive;
	public ArrayList<String> actions;
	public boolean vetoNext = false;
	public int currentPrimary;
	public boolean isRecovering = true;
	public int partialPreCommit = -1;
	public int partialCommit = -1;
	public int lastKnownDecision = -1;
	
	public int deathAfter = -1;
	public ArrayList<Integer> deathAfterN = new ArrayList<Integer>();
	public ArrayList<Integer> recoverRequest = new ArrayList<Integer>();
	
	
	Node() {
		state = "BEGIN";
		upSet = new HashSet<Integer>();
		currentlyAlive = new HashSet<Integer>();
		this.responsesToVoteREQ = new HashSet<Integer>();
		actions = new ArrayList<String>();
		
		for(int i = 0; i < ThreePhaseCommit.totalNumber -1; i++) {
			this.deathAfterN.add(-1);
		}
		for(int i = 0; i < ThreePhaseCommit.totalNumber -1; i++) {
			this.recoverRequest.add(-1);
		}
		ThreePhaseCommit.myLog.parse(this);
		this.decision = "";

		
		if(this.isRecovering) {
			this.currentlyAlive.add(ThreePhaseCommit.PID);
			
			if(state.equals("BEGIN"))
			{ 
				
			}
			else if(state.equals("ABORTED"))
			{
				this.abortSelf();
			}
			else if(state.equals("UNCERTAIN")||state.equals("COMMITTABLE"))
			{
				//wait to hear from primary
			}
			else if(state.equals("COMMITTED"))
			{
				this.commit();
				ThreePhaseCommit.myLog.write("DECISION|COMMIT");
				this.state = "BEGIN";
				if(ThreePhaseCommit.verbose) {
					System.out.println("state: BEGIN\n\n");
				}
				clear();
			}
			
			this.send_RECOVER();
		}
			
	}
	
	public void run() {
	
		if(this.isPrimary) {
			this.TimeoutTime = this.TimeoutTime / 2;
		}
		
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		
		while(true) {

			if(this.deathAfter == 0) {
				this.halt();
			}
			for(int i: this.deathAfterN) {
				if(i == 0) {
					this.halt();
				}
			}
			java.util.List<String> incomingMessages = ThreePhaseCommit.net.getReceivedMsgs();
			if(incomingMessages.size() == 0) {
				try {
					Thread.sleep(this.cycleSleepTime);
				} catch (InterruptedException e) {
					e.printStackTrace();
				}
			}
			for(String message: incomingMessages) {
				parseMessage(message);
			}
			
			//System.out.println(this.timeout - System.currentTimeMillis());
			if(this.timeout != -1 && System.currentTimeMillis() > this.timeout) {
				timeout();
			}
			//get user input
			try {
				if ( br.ready() ) {
					String userInput = br.readLine();
					handleInput(userInput);
				}
			} catch (IOException e) {
				e.printStackTrace();
			}
			
			
		}
		
		
		
		
	}
	
	private void parseMessage(String message) {
		ArrayList<String> messageList = new ArrayList<String>();
		StringTokenizer st = new StringTokenizer(message, "|");
		String type = null;
		
		while(st.hasMoreTokens())
		{
			if(type==null) {
				type = st.nextToken();
				messageList.add(type);
			}
			else messageList.add(st.nextToken());
			
		}
		
		if(this.deathAfter != -1 && this.deathAfter-- == 0) {
			this.halt();
		}
		if(!type.equals("halt") && !type.equals("REQUEST")) {
			int sender = Integer.parseInt(messageList.get(1));
			int count = this.deathAfterN.get(sender); 
			if(count != -1 && count == 0 ) {
				this.halt();
			}
			else if(count != -1) {
				this.deathAfterN.set(sender, count-1);
			}
		}
		
		switch(type)
		{
		case "REQUEST": {handle_REQUEST(messageList); break;}
		case "VOTE_REQ": {handle_VOTE_REQ(messageList); break;}
		case "REPLY_VOTE_REQ": {handle_REPLY_VOTE_REQ(messageList); break;}
		case "PRE_COMMIT": {handle_PRE_COMMIT(messageList); break;}
		case "DECISION": {handle_DECISION(messageList); break;}

		case "STATE_REQUEST": {handle_STATE_REQUEST(messageList); break;}
		case "REPLY_STATE_REQUEST": {handle_REPLY_STATE_REQUEST(messageList); break;}
		case "DECISION_REQ": {handle_DECISION_REQ(messageList); break;}
		case "REPLY_DECISION_REQ": {handle_REPLY_DECISION_REQ(messageList); break;}
		case "UR_ELECTED": {handle_UR_ELECTED(messageList); break;}
		case "RECOVER":{handle_RECOVER(messageList); break;}
		case "RECOVER_INFO":{handle_RECOVER_INFO(messageList); break;}
		case "halt": {halt(); break;}
		default: System.out.println("Could not recognize the message: " + message);
		
		}
		//System.out.println(message);
	}
	
	private void handle_RECOVER_INFO(java.util.List<String> message) {
		if(ThreePhaseCommit.verbose) {
			String printString = "received: ";
			for(String s: message)
				printString += s + " ";
			System.out.println(printString);
		}
		
		this.isRecovering = false;
		
		int oldReqNum = this.reqNum;
		
		//parse input
		int l = message.size();
		
		if(l-3 == 0 && !this.state.equals("BEGIN")) { //no actions, abort current
			this.abortSelf();
			this.clear();
			return;
		}
		else if(l-3 == 0) {
			this.clear();
			return;
		}
		
		
		for(int i = 3; i < l; i++) {
			
			String s = message.get(i);
			StringTokenizer st = new StringTokenizer(s, ",");
			
			
			int first  = -1;
			
			this.reqNum = Integer.parseInt(st.nextToken());
			if(first != -1) first = this.reqNum;
			
			this.action = st.nextToken();
			this.song = st.nextToken();
			if(!this.action.equals("delete"))
				this.url = st.nextToken();
			
			if(!this.state.equals("BEGIN")) {
				if(this.reqNum != oldReqNum) {
					this.abortSelf();
					this.log_request();
					this.commitSelf();
					this.clear();
				}
				else {
					this.commitSelf();
					this.clear();
				}
			}
			else {
				this.log_request();
				this.commitSelf();
				this.clear();
			}
			
		}
		
		this.updateUpset(message.get(2));
		this.writeUpset();
		
		//reset upset
		
		
		this.writeUpset();
		
		this.isRecovering = false;
		
		if(ThreePhaseCommit.verbose) {
			String printString = "Node has recovered.";
			System.out.println(printString);
		}
		
	}
	
	private void log_request() {
		String logString = "REQUEST|";
		logString += this.reqNum+"|";
		logString += this.action+"|";
		logString += this.song;
		if(!this.action.equals("delete")) {
			logString += "|"+this.url;
		}
		ThreePhaseCommit.myLog.write(logString);
	}
	
	private void handle_REQUEST(java.util.List<String> message) {
		
		if(ThreePhaseCommit.verbose) {
			String printString = "received: ";
			for(String s: message)
				printString += s + " ";
			System.out.println(printString);
		}
				
		if(!this.state.equals("BEGIN")) {
			return;
		}

		
		this.reqNum = Integer.parseInt(message.get(1)); //if problems, check reqNum here...
		this.action = message.get(2);
		this.song = message.get(3);
		
		String logString = "REQUEST|";
		logString += message.get(1)+"|";
		logString += message.get(2)+"|";
		logString += message.get(3);
		if(message.size() == 5) {
			logString += "|"+message.get(4);
			this.url = message.get(4);
		}
		ThreePhaseCommit.myLog.write(logString);
		
		if(this.isPrimary) {
			ThreePhaseCommit.myLog.write("START_3PC");

			if(this.upSet.size() == 1) {
				this.commitOthers();
				this.commitSelf();
				this.clear();
				return;
			}
			
			this.send_vote_req();
			
			this.state = "VOTEREQ";
			if(ThreePhaseCommit.verbose) {
				System.out.println("state: VOTEREQ");
			}
			this.resetTimeout();
		}
		else {
			this.state = "VOTEREQ";
			if(ThreePhaseCommit.verbose) {
				System.out.println("state: VOTEREQ");
			}
			this.resetTimeout();
		}
		
		
	}
	
	private void send_RECOVER() {
		
		String recoverMessage = "RECOVER|";
		recoverMessage += ThreePhaseCommit.PID + "|";
		recoverMessage += this.lastKnownDecision +"|";
		boolean first = true;
		for(int i: this.upSet) {
			if(!first) recoverMessage += ",";
			recoverMessage += i;
			first = false;
		}
		
		if(ThreePhaseCommit.verbose) {
			String printString = "send: " + recoverMessage;
			System.out.println(printString);
		}
		
		for(int iii = 0; iii < ThreePhaseCommit.totalNumber -1; iii++) {
			if(iii == ThreePhaseCommit.PID) continue;
			ThreePhaseCommit.net.sendMsg(iii,recoverMessage);
		}
		this.resetTimeout();
	}
	
	private void handle_RECOVER(java.util.List<String> message) {
		if(ThreePhaseCommit.verbose) {
			String printString = "received: ";
			for(String s: message)
				printString += s + " ";
			System.out.println(printString);
		}
		
		//Remove the node from the upSet (if it is still there)
		this.upSet.remove(Integer.parseInt(message.get(1)));
		
		if(this.isPrimary) {
			if(!this.state.equals("BEGIN")) {
				return; //ignore it, try again in future
			}
			else {
				String actions = ThreePhaseCommit.myLog.getAllOperations(Integer.parseInt(message.get(2)));
				this.send_recover_info(actions,Integer.parseInt(message.get(1)));
				this.upSet.add(Integer.parseInt(message.get(1)));
				this.writeUpset();
			}
		}
		else if(this.isRecovering){
			
			
			int sender = Integer.parseInt(message.get(1));
			
			//add sender to currently alive
			this.currentlyAlive.add(sender);
			//record request number
			int rq = Integer.parseInt(message.get(2));
			this.recoverRequest.set(sender, rq);
			
			Set<Integer> receivedUp = new HashSet<Integer>();
			String s = message.get(3);
			StringTokenizer st = new StringTokenizer(s, ",");
			while(st.hasMoreTokens())
			{
				receivedUp.add(Integer.parseInt(st.nextToken()));
			}
			//upSet = intersection upSet and recieved upset
			this.upSet.retainAll(receivedUp);
			this.writeUpset(); //CHECK
			
			boolean subset = true;
			for(Integer x: this.upSet)
			{
				if(!this.currentlyAlive.contains(x))
				{
					subset = false;
					break;
				}
				
			}
			//if upset is subset of currently alive
			if(subset)
			{
				//elect lowest node in upset
				int lowest =  10000;
				for(Integer x : this.upSet)
				{
					if(x < lowest) lowest = x;
				}
				//if elected
				if(lowest == ThreePhaseCommit.PID)
				{
						
					this.recoverAll();
				}
				else{
					this.currentPrimary = lowest;
					//if not elected
						//if it is another node, send that node UR_ELECTED (check if we are in recovery in handle_UR_ELECTED)
					String informNewPrimary = "UR_ELECTED|";
					informNewPrimary += ThreePhaseCommit.PID + "|";
					informNewPrimary += this.reqNum;
					ThreePhaseCommit.net.sendMsg(this.currentPrimary, informNewPrimary);
					this.resetTimeout();
					
					//wait for RECOVER_INFO
						//if timeout
							//remove primary from currently alive nodes
							//continue to broadcast RECOVER messages
						//set timeout, this.resetTimer()
				}
			}
			else{	
				//keep sending recover msg	
			}
		}
		//if the primary is dead call election protocol
		else if(Integer.parseInt(message.get(1)) == this.currentPrimary){ 
			this.electionProtocol();
		}
		
	}
	
	private void send_recover_info(String actions, int target) {
		
		String recoverInfoMessage = "RECOVER_INFO|";
		recoverInfoMessage += ThreePhaseCommit.PID + "|";
		boolean first = true;
		for(int i: this.upSet) {
			if(!first) recoverInfoMessage += ",";
			recoverInfoMessage += i;
			first = false;
		}
		if(actions != null) {
			recoverInfoMessage += "|" + actions;
		}
		if(ThreePhaseCommit.verbose) {
			String printString = "send: " + recoverInfoMessage;
			System.out.println(printString);
		}
		ThreePhaseCommit.net.sendMsg(target, recoverInfoMessage);
		
	}
	
	private void handle_VOTE_REQ(java.util.List<String> message) {
		
		if(ThreePhaseCommit.verbose) {
			String printString = "received: ";
			for(String s: message)
				printString += s + " ";
			System.out.println(printString);
		}
		
		this.currentPrimary = Integer.parseInt(message.get(1));
		
		boolean decision = true;
		if(this.vetoNext) { 
			decision = false;
			this.vetoNext = false;
		}
		//add simulated voting of no
		//potentially randomized (i.e. 99%)
		
		this.updateUpset(message.get(3));
		this.writeUpset();
		
		this.send_reply_vote_req(decision, message);
	}
	
	private void handle_REPLY_VOTE_REQ(java.util.List<String> message) {
		
		if(ThreePhaseCommit.verbose) {
			String printString = "received: ";
			for(String s: message)
				printString += s + " ";
			System.out.println(printString);
		}
		
		int sender = Integer.parseInt(message.get(1));
		String vote = message.get(3);
		
		if(vote.equals("YES")) {
			this.responsesToVoteREQ.add(sender);
		}
		else {
			this.decision = "abort";
			this.responsesToVoteREQ.add(sender);
		}
		
		if(this.responsesToVoteREQ.size() == this.upSet.size() - 1) {
			
			this.stopTimeout();
			
			if(this.decision.equals("abort")) {
				this.abortSelf();
				this.abortOthers();
				clear();
			}
			else {
				this.send_pre_commit();
				this.commitOthers();
				clear();
			}
		}
	}
	
	private void handle_PRE_COMMIT(java.util.List<String> message) {
		
		if(ThreePhaseCommit.verbose) {
			String printString = "received: ";
			for(String s: message)
				printString += s + " ";
			System.out.println(printString);
		}
		
		ThreePhaseCommit.myLog.write("PRECOMMIT");
		this.state = "COMMITABLE";
		if(ThreePhaseCommit.verbose) {
			System.out.println("state: COMMITABLE");
		}
		
		this.resetTimeout();
	}
	
	private void handle_DECISION(java.util.List<String> message) {
		
		this.stopTimeout();
		
		if(ThreePhaseCommit.verbose) {
			String printString = "received: ";
			for(String s: message)
				printString += s + " ";
			System.out.println(printString);
		}
		
		String theDecision = message.get(3);
		if(theDecision.equals("COMMIT")) {
			this.commitSelf();
			this.clear();
		}
		else {
			this.abortSelf();
			this.clear();
		}
		
	}
	
	//everything below this line is for recovery protocol
	
	private void handle_STATE_REQUEST(java.util.List<String> message) {
		
		if(ThreePhaseCommit.verbose) {
			String printString = "received: ";
			for(String s: message)
				printString += s + " ";
			System.out.println(printString);
		}
		
		this.send_reply_state_request(message);	
		
	}
	
	private void handle_REPLY_STATE_REQUEST(java.util.List<String> message) {
	
		if(ThreePhaseCommit.verbose) {
			String printString = "received: ";
			for(String s: message)
				printString += s + " ";
			System.out.println(printString);
		}
		
		int sender = Integer.parseInt(message.get(1));
		String senderStatus = message.get(3);
				
		if(senderStatus.equals("COMMIT")) {
			this.responsesToVoteREQ.add(sender);
			this.decision = "commit";
		}
		else if(senderStatus.equals("COMMITABLE")) {
			this.responsesToVoteREQ.add(sender);
			if(!this.decision.equals("commit")) {
				this.decision = "committable";
			}
		}
		else if(senderStatus.equals("UNCERTAIN")) {
			this.responsesToVoteREQ.add(sender);
			if(!(this.decision.equals("commit") || this.decision.equals("commitable") || this.decision.equals("abort"))) {
				this.decision = "uncertain";
			}
		}
		else {
			this.decision = "abort";
			this.responsesToVoteREQ.add(sender);
		}
		
		if(this.responsesToVoteREQ.size() == this.upSet.size() - 1) {
			this.stopTimeout();
			
			if(this.decision == null || this.decision.equals("") || this.decision.equals("abort") || this.decision.equals("uncertain")) {
				this.abortSelf();
				this.abortOthers();
				clear();
			}
			else if(this.decision.equals("commit")){
				this.commitOthers();
				
				clear();
			}
			else {
				this.send_pre_commit();
				this.commitOthers();
				clear();
			}
		}
			
	}
	
	private void handle_DECISION_REQ(java.util.List<String> message) {
		
	}
	
	private void handle_REPLY_DECISION_REQ(java.util.List<String> message) {
		
	}
	
	private void handle_UR_ELECTED(java.util.List<String> message){
		
		if(ThreePhaseCommit.verbose) {
			String printString = "received: ";
			for(String s: message)
				printString += s + " ";
			System.out.println(printString);
		}
		
		if(this.isPrimary) return;
		if(this.isRecovering)
		{
			this.recoverAll();
			return;
		}
		
		this.isPrimary = true;
		
		if(ThreePhaseCommit.verbose) {
			System.out.println("I am new primary. Long live the king.");
		}
		
		this.responsesToVoteREQ.clear();
		
		this.timeout = this.timeout / 2;
		
		this.upSet.remove(this.currentPrimary);
		
		
		this.currentPrimary = ThreePhaseCommit.PID;
				
		if(this.state.equals("VOTEREQ")) {
			this.abortSelf();
			this.abortOthers();
			clear();
		}
		else if(this.state.equals("UNCERTAIN")) {
			
			this.decision = "uncertain";
			
			String stateReqMessage = "STATE_REQUEST|";
			stateReqMessage += ThreePhaseCommit.PID + "|";
			stateReqMessage += this.reqNum + "|";
			boolean first = true;
			for(int i: this.upSet) {
				if(!first) stateReqMessage += ",";
				stateReqMessage += i;
				first = false;
			}
			
			for(int i: this.upSet) {
				if(i == ThreePhaseCommit.PID) continue;
				ThreePhaseCommit.net.sendMsg(i, stateReqMessage);
			}
			
			this.resetTimeout();
			
			this.state = "WAIT_FOR_STATES";
			if(ThreePhaseCommit.verbose) {
				System.out.println("state: WAIT_FOR_STATES");
			}
			
		}
		else if(this.state.equals("COMMITABLE")) {
						
			this.send_pre_commit();
			this.commitOthers();
			clear();
		}
		else if(this.state.equals("BEGIN")) {
		
			String decision = ThreePhaseCommit.myLog.getDecision(Integer.parseInt(message.get(2)),this);
			
			this.reqNum = Integer.parseInt(message.get(2));
			
			if(decision.equals("COMMIT"))
			{
				this.send_pre_commit();
				this.commitOthers();
				clear();
			}
			else
			{
				this.abortSelf();
				this.abortOthers();
				clear();
			}
		}
	}
	
	private void timeout() {
				
		if(this.isPrimary) {
			if(this.state.equals("VOTEREQ")) {			
				this.timeout_primary_votereq();
			}
			else if(this.state.equals("WAIT_FOR_STATES")) {
				this.timeout_primary_wait_for_states();
			}
		}
		else {
			//System.out.println(this.isRecovering);
			if(this.isRecovering) {
				this.currentlyAlive.remove(this.currentPrimary);
				this.writeUpset();
				this.send_RECOVER();
			}
			else if(this.state.equals("VOTEREQ")) {
				this.timeout_participant_votereq();
			}
			else if(this.state.equals("UNCERTAIN")) {
				this.timeout_participant_uncertain();
			}
			else if(this.state.equals("COMMITABLE")){
				this.timeout_participant_commitable();
			}
			//also add stuff for recovery
			
		}
		
	}
	
	private void timeout_primary_wait_for_states() {
		
		if(this.decision.equals("commit")) {
			this.commitOthers();
			
			clear();
		}
		else if(this.decision.equals("commitable")) {
			this.send_pre_commit();
			this.commitOthers();
			clear();
		}
		else {
			this.abortSelf();
			this.abortOthers();
			clear();
		}
		
		
	}
	
	private void timeout_participant_commitable() {
		this.electionProtocol();
	}
	
	private void timeout_participant_uncertain() {
		this.electionProtocol();
	}
	
	private void timeout_participant_votereq() {
		this.electionProtocol();
	}
	
	private void timeout_primary_votereq() {
		this.upSet.clear(); 
		this.upSet.add(ThreePhaseCommit.PID);
		for(int i: this.responsesToVoteREQ) {
			this.upSet.add(i);	
		}
		this.writeUpset();
		
		this.abortSelf();
		this.abortOthers();
		clear();
	}
	
	public void updateUpset(String message)
	{
		this.upSet.clear();
		StringTokenizer st = new StringTokenizer(message,",");
		while(st.hasMoreTokens())
		{
			this.upSet.add(Integer.parseInt(st.nextToken()));
		}
		
		
	}
	
	public void writeUpset() {
		
		String myUpset = "";
		boolean first = true;
		for(Integer x: this.upSet) {
			if(!first)
				myUpset += ",";
			myUpset += x;
			first = false;
		}
		try {
		    PrintWriter out = new PrintWriter(new BufferedWriter(new FileWriter(ThreePhaseCommit.upsetFileName, false)));
		    out.println(myUpset);
		    out.close();
		} catch (Exception e) {
		    
		}
	}
	
	private void showActions()
	{
		for(String s: this.actions)
			System.out.println(s);
		
	}
	
	private void commit() {
		if(this.action.equals("add")) {
			ThreePhaseCommit.myPlaylist.add(this.song,this.url);
		}
		else if(this.action.equals("edit")) {
			ThreePhaseCommit.myPlaylist.edit(this.song,this.url);
		}
		else if(this.action.equals("delete")) {
			ThreePhaseCommit.myPlaylist.delete(this.song);
		}
		
		String actionPerformed = this.action + " <" + this.song;
		if(this.url != null) {
			actionPerformed += ", " + this.url;
		}
		actionPerformed += ">";
//		System.out.println(actionPerformed);
		this.actions.add(actionPerformed);
	}
	
	private void halt() {
		ThreePhaseCommit.net.shutdown();
		System.exit(0);
	}
	
	private void resetTimeout() {
		this.timeout = System.currentTimeMillis() + TimeoutTime;
	}
	
	private void stopTimeout() {
		this.timeout = -1;
	}
	
	private void clear() {
		
		reqNum = -1;
		action =null;
		song =null;
		url = null;
		decision = "";
		responsesToVoteREQ.clear();
		this.stopTimeout();
		
	}
	
	private void handleInput(String userInput) {
		
		String firstThing = null;
		ArrayList<String> args = new ArrayList<String>();
		StringTokenizer st = new StringTokenizer(userInput);
		if(userInput!=null){
			firstThing = st.nextToken();
		}
		while(st.hasMoreTokens())
			args.add(st.nextToken());
		switch(firstThing) {
		case "halt": {this.halt(); break;}
		case "state": {System.out.println(this.state); break;}
		case "actions": {this.showActions(); break;}
		case "playlist": {this.showPlaylist(); break;}
		case "deathafter": { 
			if(args.size()!=1)
				System.out.println("Exactly one argument is needed");
			else
				this.deathAfter(Integer.parseInt(args.get(0)));
			break;
		}
		case "deathaftern": { 
			if(args.size()!=2)
				System.out.println("Exactly two arguments are needed");
			else
				this.deathAfterN(Integer.parseInt(args.get(0)),Integer.parseInt(args.get(1)));
			break;
		}
		case "vetonext": {this.vetoNext(); break;}
		case "timeout": {
			if(args.size()!=1)
				System.out.println("Exactly one argument is needed");
			else
				this.setTimeoutTime(Float.parseFloat(args.get(0)));
			break;
		}
		case "speed": {
			if(args.size()!=1)
				System.out.println("Exactly one argument is needed");
			else
				this.setSpeed(Float.parseFloat(args.get(0)));
			break;
		}
		case "partialpre": {
			if(args.size()!=1)
				System.out.println("Exactly one argument is needed");
			else
				this.partialPreCommit = Integer.parseInt(args.get(0));
			break;
		}
		case "partialcomm": {
			if(args.size()!=1)
				System.out.println("Exactly one argument is needed");
			else
				this.partialCommit = Integer.parseInt(args.get(0));
			break;
		}
		default: System.out.println("Error: user input cannot be recognized");
		
		}
		
		
	}
	
	private void showPlaylist() {
		
		File f = new File(ThreePhaseCommit.playlistFileName);
		if(!f.exists()) return;
		
		BufferedReader br; String line  = null;
		try {
			br = new BufferedReader(new FileReader(f));
			
			while ((line = br.readLine()) != null) {
			   System.out.println(line);
			}
			br.close();
		
		} catch (Exception e) {
			System.out.println(e);
			e.printStackTrace();
		}
		
	}
	
	private void deathAfter(int messages) {
		this.deathAfter = messages;
	}
	
	private void deathAfterN(int messages, int sender) {
		this.deathAfterN.set(sender, messages);
	}
	
	private void vetoNext() {
		this.vetoNext = true;
	}
	
	private void setTimeoutTime(float newTimeoutTime) {
		this.TimeoutTime = (long)(newTimeoutTime * 1000);
	}
	
	private void setSpeed(float newCycleTime) {
		this.cycleSleepTime = (long)(newCycleTime * 1000);
	}
	
	private void electionProtocol() {
		
		
		this.upSet.remove(this.currentPrimary);
		this.writeUpset();	
				
		int lowest = 10000;
		for(int i: this.upSet)
		{
			if(i<lowest)
				lowest = i;
		}
		this.currentPrimary = lowest;
		if(lowest == 10000) return; //just in case
		if(this.currentPrimary==ThreePhaseCommit.PID)
			this.isPrimary = true;
		
		if(this.isPrimary) {
			//if it's me continue the protocol
			
			if(ThreePhaseCommit.verbose) {
				System.out.println("I am new primary. Long live the king.");
			}
			
			this.responsesToVoteREQ.clear();
			
			this.timeout = this.timeout / 2;
			if(this.state.equals("VOTEREQ")) {
				this.abortSelf();
				this.abortOthers();
				clear();
				
				this.stopTimeout();
				
			}
			else if(this.state.equals("UNCERTAIN")) {
				
				String stateReqMessage = "STATE_REQUEST|";
				stateReqMessage += ThreePhaseCommit.PID + "|";
				stateReqMessage += this.reqNum + "|";
				boolean first = true;
				for(int i: this.upSet) {
					if(!first) stateReqMessage += ",";
					stateReqMessage += i;
					first = false;
				}
				
				for(int i: this.upSet) {
					if(i == ThreePhaseCommit.PID) continue;
					ThreePhaseCommit.net.sendMsg(i, stateReqMessage);
				}
				
				this.resetTimeout();
				
				this.state = "WAIT_FOR_STATES";
				if(ThreePhaseCommit.verbose) {
					System.out.println("state: WAIT_FOR_STATES");
				}
				
			}
			else if(this.state.equals("COMMITABLE")) {
				this.send_pre_commit();
				this.commitOthers();
				clear();
			}
			
		}
		else {
			
			String informNewPrimary = "UR_ELECTED|";
			informNewPrimary += ThreePhaseCommit.PID + "|";
			informNewPrimary += this.reqNum;
			ThreePhaseCommit.net.sendMsg(this.currentPrimary, informNewPrimary);
			this.resetTimeout();
			
		}

	}
	private void recoverAll()
	{
		this.stopTimeout(); //CHECK
		this.isRecovering = false;
		this.isPrimary = true;
		this.currentPrimary = ThreePhaseCommit.PID;
		//uplist = nodes that are currently alive
		this.upSet.clear();
		for(Integer x: this.currentlyAlive)
			this.upSet.add(x);
		this.writeUpset(); //CHECK
		
		this.currentlyAlive.clear();
		
		if(this.state.equals("BEGIN"))
		{
			//if state == BEGIN
			//send RECOVER_INFO (needs lowest req# from each node)
			for(Integer x: this.upSet)
			{
				if(x == ThreePhaseCommit.PID)
					continue;
				int r = this.recoverRequest.get(x);
				String actions = ThreePhaseCommit.myLog.getAllOperations(r);
				send_recover_info(actions, x);
			}
			
		}
		else if(this.state.equals("ABORTED") || this.state.equals("UNCERTAIN"))
		{ 
			//if state == abort
			//abort
			//send RECOVER_INFO (needs lowest req# from each node)
			this.abortSelf();
			for(Integer x: this.upSet)
			{
				if(x == ThreePhaseCommit.PID)
					continue;
				int r = this.recoverRequest.get(x);
				String actions = ThreePhaseCommit.myLog.getAllOperations(r);
				send_recover_info(actions, x);
			}
			
		}
		else if(this.state.equals("COMMITTED") || this.state.equals("COMMITTABLE"))
		{
		//if state == commit or commitable
			//commit
			//send RECOVER_INFO (needs lowest req# from each node)
			this.commitSelf();
			for(Integer x: this.upSet)
			{
				if(x == ThreePhaseCommit.PID)
					continue;
				int r = this.recoverRequest.get(x);
				String actions = ThreePhaseCommit.myLog.getAllOperations(r);
				send_recover_info(actions, x);
			}
		}
		
		for(int i = 0; i< ThreePhaseCommit.totalNumber - 1; i++)
			this.recoverRequest.add(-1);
		//if state == uncertain
			//abort
			//send RECOVER_INFO (needs lowest req# from each node)
		//we should be in state BEGIN, this.stopTimer();
		
	}
	
	private void abortSelf() {
		if(ThreePhaseCommit.verbose) {
			System.out.println("decision: ABORT");
		}
		ThreePhaseCommit.myLog.write("ABORT");
		ThreePhaseCommit.myLog.write("DECISION|ABORT");
		this.state = "BEGIN";
		if(ThreePhaseCommit.verbose) {
			System.out.println("state: BEGIN\n\n");
		}
	}
	
	private void abortOthers() {
		String decideAbort = "DECISION|";
		decideAbort += ThreePhaseCommit.PID + "|";
		decideAbort += this.reqNum + "|";
		decideAbort += "ABORT";
		
		for(Integer x: this.upSet) {
			if(!(x == ThreePhaseCommit.PID)) {
				ThreePhaseCommit.net.sendMsg(x, decideAbort);
			}
		}
	}
	
	private void commitSelf() {
		ThreePhaseCommit.myLog.write("COMMIT");
		this.commit();
		ThreePhaseCommit.myLog.write("DECISION|COMMIT");
		this.state = "BEGIN";
		if(ThreePhaseCommit.verbose) {
			System.out.println("state: BEGIN\n\n");
		}
	}
	
	private void commitOthers() {
		ThreePhaseCommit.myLog.write("COMMIT");

		if(this.partialPreCommit == 0) {
			this.halt();
		}
		
		this.commit();
		
		String messageToClient = this.action + "|" + this.song;
		if(this.url != null) {
			messageToClient += "|" + this.url;
		}
		ThreePhaseCommit.net.sendMsg(ThreePhaseCommit.totalNumber - 1, messageToClient);
		
		if(ThreePhaseCommit.verbose) {
			System.out.println("send: COMMIT messages");
		}
		
		ThreePhaseCommit.myLog.write("DECISION|COMMIT");
		this.state = "BEGIN";
		if(ThreePhaseCommit.verbose) {
			System.out.println("state: BEGIN\n\n");
		}
		
		String commitMessage = "DECISION|";
		commitMessage += ThreePhaseCommit.PID + "|";
		commitMessage += this.reqNum + "|";
		commitMessage += "COMMIT";
		
		for(Integer x: this.upSet) {
			if(!(x == ThreePhaseCommit.PID)) {
				if(this.partialCommit == -1 || this.partialCommit-- > 0) {
					ThreePhaseCommit.net.sendMsg(x, commitMessage);
				}
				else {
					this.halt();
				}
				
			}
		}
		
		if(this.partialPreCommit == 0) {
			this.halt();
		}
		
	}
	
	private void send_pre_commit() {
		ThreePhaseCommit.myLog.write("PRECOMMIT");
		
		if(ThreePhaseCommit.verbose) {
			System.out.println("send: PRECOMMIT messages");
		}
		
		if(this.partialPreCommit == 0) {
			this.halt();
		}
		
		String preCommitMessage = "PRE_COMMIT|";
		preCommitMessage += ThreePhaseCommit.PID + "|";
		preCommitMessage += this.reqNum;
		
		for(Integer x: this.upSet) {
			if(!(x == ThreePhaseCommit.PID)) {
				if(this.partialPreCommit == -1 || (this.partialPreCommit-- > 0)) {
					ThreePhaseCommit.net.sendMsg(x, preCommitMessage);
				}
				else {
					this.halt();
				}
			}
		}
		
		if(this.partialPreCommit == 0) {
			this.halt();
		}
		
	}
	
	private void send_reply_state_request(java.util.List<String> message) {
		String replyMessage = "REPLY_STATE_REQUEST|";
		replyMessage += ThreePhaseCommit.PID + "|";
		replyMessage += message.get(2) + "|";
		
		if(this.state.equals("BEGIN")) {
			//read log to find status, should be committed or aborted
			
			String decision = ThreePhaseCommit.myLog.getDecision(Integer.parseInt(message.get(2)),this);
			if(decision==null) return;
			replyMessage += decision;
			
		}
		else {
			replyMessage += this.state;
		}
		if(ThreePhaseCommit.verbose) {
			System.out.println("send: " + replyMessage);
		}
		ThreePhaseCommit.net.sendMsg(Integer.parseInt(message.get(1)), replyMessage);
	}
	
	private void send_vote_req() {
		String voteReqMessage = "VOTE_REQ|";
		voteReqMessage += ThreePhaseCommit.PID + "|";
		voteReqMessage += this.reqNum + "|";
		
		boolean first = true;
		for(Integer x:this.upSet) {
			if(!first) {
				voteReqMessage += ",";
			}
			voteReqMessage += x;
			first = false;
		}
		
		if(ThreePhaseCommit.verbose) {
			System.out.println("send: VOTEREQ messages-> " + voteReqMessage);
		}
		
		for(Integer x:this.upSet) {
			if(x != ThreePhaseCommit.PID) {
				ThreePhaseCommit.net.sendMsg(x,voteReqMessage);
			}
		}
	}
	
	private void send_reply_vote_req(boolean decision, java.util.List<String> message) {
		if(decision) {
			ThreePhaseCommit.myLog.write("YES");
			String replyVoteReq = "REPLY_VOTE_REQ|";
			replyVoteReq += ThreePhaseCommit.PID+"|";
			replyVoteReq += this.reqNum + "|";
			replyVoteReq += "YES";
			ThreePhaseCommit.net.sendMsg(Integer.parseInt(message.get(1)), replyVoteReq);
			this.state = "UNCERTAIN";
			if(ThreePhaseCommit.verbose) {
				System.out.println("state: UNCERTAIN");
			}
		}
		else {
			
			String replyVoteReq = "REPLY_VOTE_REQ|";
			replyVoteReq += ThreePhaseCommit.PID+"|";
			replyVoteReq += this.reqNum + "|";
			replyVoteReq += "NO";
			ThreePhaseCommit.net.sendMsg(Integer.parseInt(message.get(1)), replyVoteReq);
			
			this.abortSelf();
			clear();
		}
	}
}
