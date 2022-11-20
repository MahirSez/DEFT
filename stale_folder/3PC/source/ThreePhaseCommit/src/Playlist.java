import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.HashMap;
import java.util.Set;
import java.util.StringTokenizer;


public class Playlist {

	private String fileN;
	
	Playlist(String filename) {
		this.fileN = filename;	
		File f = new File(fileN);
		if(!f.exists())
			try {
				f.createNewFile();
			} catch (IOException e) {
				e.printStackTrace();
			}
	}
	
	public void add(String songName, String URL) {
		if(ThreePhaseCommit.verbose){
			System.out.println("playlist: add \"" + songName + "\" \"" + URL + "\"");
		}
		HashMap<String, String> theHashing = parse();
		if(theHashing.containsKey(songName)) {
			return;
		}
		theHashing.put(songName, URL);
		write(theHashing);
	}
	
	public void delete(String songName) {
		if(ThreePhaseCommit.verbose){
			System.out.println("playlist: delete \"" + songName + "\"");
		}
		HashMap<String, String> theHashing = parse();
		if(!theHashing.containsKey(songName)) {
			return;
		}
		theHashing.remove(songName);	
		write(theHashing);
	}
	
	public void edit(String songName, String URL) {
		if(ThreePhaseCommit.verbose){
			System.out.println("playlist: edit \"" + songName + "\" \"" + URL + "\"");
		}
		HashMap<String, String> theHashing = parse();
		if(!theHashing.containsKey(songName)) {
			return;
		}
		theHashing.put(songName, URL);	
		write(theHashing);
	}
	
	private HashMap<String, String> parse() {
		
		HashMap<String, String> map = new HashMap<String, String>();
		BufferedReader br;
		try {
			br = new BufferedReader(new FileReader(fileN));
			String line;
			while ((line = br.readLine()) != null) {
			   // process the line.
				//System.out.println(line);
				String song = null;
				String url = null;
				StringTokenizer st = new StringTokenizer(line, "\t");
				while(st.hasMoreTokens())
				{
					if(song==null) song = st.nextToken();
					else url= st.nextToken();
				}
				//System.out.println("song = "+ song+ " url = " + url);
				map.put(song, url);
			}
			br.close();
			

			
		} catch (Exception e) {
			System.out.println(e);
			e.printStackTrace();
		}
		
		
		return map;
	}
	
	private void write(HashMap<String, String> mapToWrite) {
		String tmpName = this.fileN + "_tmp";
		try {
			PrintWriter out = new PrintWriter(new FileWriter(tmpName));
			Set<String> keys = mapToWrite.keySet();
			
			for(String key: keys)
			{
				String line =  key + "\t" + mapToWrite.get(key) + "\n";
				out.write(line);
			}
			out.close();
			
			
			File tmpFile = new File(tmpName);
			File destFile = new File(this.fileN);
			boolean ret = tmpFile.renameTo(destFile);          //atomically update file
			assert( ret); // <test>
			
			
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
	
	
}
