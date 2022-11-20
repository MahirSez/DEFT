import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.net.URL;
import java.util.ArrayList;
import java.util.StringTokenizer;


public class Log {

	public int reqNum = -1;
	public String song = null;
	public String action  = null;
	public String url = null;	
	public String state = null;
	
	private String fileName = ThreePhaseCommit.logFileName;
	
	Log() {
		
	}
	
	
	public void write(String message) {
		
		try {
		    PrintWriter out = new PrintWriter(new BufferedWriter(new FileWriter(ThreePhaseCommit.logFileName, true)));
		    out.println(message);
//		    out.flush();
		    out.close();
		} catch (Exception e) {
		    
		}
		
	}
	public ArrayList<String> read(Node currentNode)
	{
		ArrayList<String> progress = new ArrayList<String>();
		
		
		BufferedReader br;
		File f = new File(ThreePhaseCommit.logFileName);
		currentNode.currentPrimary = -1;
		if(!f.exists()){
			currentNode.isRecovering = false;
			System.out.println("log: no pre-existing log file"); 
			try {
				f.createNewFile();
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
			if(ThreePhaseCommit.PID == 0) {
				currentNode.isPrimary = true;
			}
			currentNode.currentPrimary = 0;
			return progress;
		}
		try {
			br = new BufferedReader(new FileReader(f));
			String line; 
			boolean empty = true;
			while ((line = br.readLine()) != null) {
				empty = false;
				
				StringTokenizer st = new StringTokenizer(line, "|");
				String prefix = st.nextToken();
				if(prefix.equals("REQUEST"))
				{ //populate request info
					while(st.hasMoreTokens())
					{
						if(reqNum==-1) reqNum = Integer.parseInt(st.nextToken());
						else if(action==null) action = st.nextToken();
						else if(song==null) song = st.nextToken();
						else url= st.nextToken();
					}
					progress = new ArrayList<String>();
				}
				else if(prefix.equals("DECISION")) // no check for the same req num
				{
					String actionPerformed = action+" <"+song;
					if(url!=null)
						actionPerformed += ", "+url;
					actionPerformed +=">";
					
					currentNode.actions.add(actionPerformed);
					currentNode.lastKnownDecision = reqNum;
					reqNum = -1;
					song = null;
					action  = null;
					url = null;
					progress = new ArrayList<String>();
					state = "BEGIN";	
				}
				else
				{
					progress.add(line);
				}
			}
			br.close();
			
			//if(empty) System.out.println("The file is empty");
			
			
		}catch (Exception e) {
			System.out.println(e);
			e.printStackTrace();
		}
		return progress;
		
	}
	public void DecideState(ArrayList<String> al, Node currentNode)
	{
	
		
		if(reqNum==-1){
			state = "BEGIN";
		}
		else if(al.size()==0) state = "ABORTED";
		else{
			for(String s: al)
			{
				StringTokenizer st = new StringTokenizer(s, "|");
				String prefix = st.nextToken();
				if(prefix.equals("NO")||prefix.equals("START_3PC")||prefix.equals("ABORT"))
					state = "ABORTED";
				else if(prefix.equals("COMMIT"))
					state = "COMMITTED";
				else if(prefix.equals("YES"))
					state = "UNCERTAIN";
				else if(prefix.equals("PRECOMMIT"))
					state = "COMMITTABLE";
			}
		}
		
//		System.out.println("state = "+ state);

	}
	public String getDecision (int r, Node currentNode)
	{
		String decision  = null;
		BufferedReader br;
		File f = new File(ThreePhaseCommit.logFileName);
		try{
			br = new BufferedReader(new FileReader(f));
			String line; boolean readDecision =false;
			while ((line = br.readLine()) != null) {
				
				StringTokenizer st = new StringTokenizer(line, "|");
				String prefix = st.nextToken();
				if(prefix.equals("REQUEST"))
				{ 
					
					int req = Integer.parseInt(st.nextToken());
					if(r == req)
					{
						readDecision = true;
						currentNode.reqNum = req;
						currentNode.action = st.nextToken();
						currentNode.song = st.nextToken();
						if(!currentNode.action.equals("delete"))
							currentNode.url = st.nextToken();
						
					}
					
				}
				else if(prefix.equals("DECISION") && readDecision)
				{
					decision = st.nextToken();
					return decision;
				}
			}
		}catch (Exception e) {
			System.out.println(e);
			e.printStackTrace();
		}
		return decision;
	}
	public void parse(Node currentNode) {

		ArrayList<String> progress = read(currentNode);
		DecideState(progress, currentNode);

		currentNode.reqNum = this.reqNum;
		currentNode.song = this.song;
		currentNode.action = this.action;
		currentNode.url = this.url;
		currentNode.state = this.state;
		System.out.println("state: "+ currentNode.state);

		BufferedReader br; boolean init = true; String line = null;
		File f = new File(ThreePhaseCommit.upsetFileName);
		if(!f.exists()){
			try {
				f.createNewFile();
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}
		else{
			line = null;
			try {
				br = new BufferedReader(new FileReader(f));
				line = br.readLine();
			}catch (Exception e) {
					System.out.println(e);
					e.printStackTrace();
			}
		}
		if(line==null)
		{
			for(int i= 0; i<ThreePhaseCommit.totalNumber-1;i++ )
				currentNode.upSet.add(i);
			currentNode.writeUpset();

		}
		else
		{
			System.out.println("line " + line);
			currentNode.updateUpset(line);
		}
		clear();
		
	}
	public String getAllOperations(int r)
	{
		String allOperations = null;
		
		BufferedReader br;
		File f = new File(ThreePhaseCommit.logFileName);
		try {
			br = new BufferedReader(new FileReader(f));
			String line; 
			
			String interm = null; boolean getDec = false;
			while ((line = br.readLine()) != null) {
				StringTokenizer st = new StringTokenizer(line, "|");
				String prefix = st.nextToken();
				if(prefix.equals("REQUEST"))
				{ 
					int req = Integer.parseInt(st.nextToken());
					if(req > r)
					{
						interm ="";
						interm += req;
						String act = st.nextToken();
						interm += "," + act;
						interm += "," + st.nextToken();
						if(!act.equals("delete"))
							interm += "," + st.nextToken();
						getDec = true;
					}
					
				}
				else if(prefix.equals("DECISION") && getDec) // no check for the same req num
				{
					getDec = false;
					
					String dec = st.nextToken();
					if(dec.equals("COMMIT"))
					{
						if(allOperations == null)
							allOperations = interm;
						else{ 
							allOperations += "|";
							allOperations += interm;
						}
						
					}
					interm = null;
				}
				
			}
			br.close();
			
			
		}catch (Exception e) {
			System.out.println(e);
			e.printStackTrace();
		}
		
		return allOperations;
	}
	public void clear()
	{
		this.reqNum = -1;
		this.song = null;
		this.action = null;
		this.url = null;
		this.state = null;
	
	}
	
	
}
