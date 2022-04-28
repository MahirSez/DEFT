import java.awt.List;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.net.URL;


public class ThreePhaseCommit {

	public static int PID;
	public static int totalNumber;
	public static NetController net;
	public static Log myLog;
	public static Playlist myPlaylist;
	
	public static String logFileName;
	public static String upsetFileName;
	public static String playlistFileName;
	
	public static final boolean verbose = true;
	
	public static void main(String[] args) {

		if(args.length != 1) {
			System.out.println("Error: you must provide a configuration file!");
			System.exit(1);
		}
		
		//URL location = ThreePhaseCommit.class.getProtectionDomain().getCodeSource().getLocation();
		String location = System.getProperty("user.dir");
		
		//Read the configuration file
		Config conf;
		net = null;
		try {
			conf = new Config(location+"/config/" + args[0]);
			net = new NetController(conf);
		} catch (FileNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			System.out.println("Error, could not read config file!");
			System.exit(1);
			e.printStackTrace();
		}
		
		logFileName = location+"/logs/" + "log_" + PID + ".txt";
		playlistFileName = location+"/playlists/" + "playlist_" + PID + ".txt";
		upsetFileName = location+"/logs/" + "upset_" + PID + ".txt";
		
		//myPlaylist = new Playlist(location.getFile()+"../playlists/" + "example_playlist");

		myLog = new Log();
		
		if(PID == totalNumber - 1) {
			Client myClient = new Client();
			myClient.run();
			
		}
		else {
			myPlaylist = new Playlist(playlistFileName);
			Node myNode = new Node();
			myNode.run();
		}
		
		System.out.println("Node "+PID+" as terminated.");
		net.shutdown();
		
	}

}
