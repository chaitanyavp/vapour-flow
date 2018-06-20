import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.DataOutputStream;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.ArrayList;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

public class CommunicateWithFlask {
    
    public static void main(String[] args) throws IOException {
        String urlString = "http://127.0.0.1:5000/json";


        try {
            URL url = new URL(urlString);
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("POST");
            conn.setRequestProperty("Accept", "application/json");
            conn.setRequestProperty("Content-Type", "application/json; charset=utf-8");

    		conn.setRequestProperty("User-Agent", "baddiy");
    		conn.setRequestProperty("Accept-Language", "UTF-8");
    		
    		HashMap<String, String> params = new HashMap();
    		params.put("good", "bad");
    		
    		JSONObject good = new JSONObject();
    		good.putAll(params);
    	    
    		conn.setDoOutput(true);
    		OutputStreamWriter outputStreamWriter = new OutputStreamWriter(conn.getOutputStream());
            outputStreamWriter.write(good.toString());
            outputStreamWriter.flush();
            
//            BufferedReader in = new BufferedReader(new InputStreamReader(conn.getInputStream()));
//    		String inputLine;
//    		StringBuffer response = new StringBuffer();
//     
//    		while ((inputLine = in.readLine()) != null) {
//    			response.append(inputLine);
//    		}
//    		in.close();

            
            if (conn.getResponseCode() != 200) {
                throw new RuntimeException("Failed : HTTP error code : " + conn.getResponseCode());
            }

//            BufferedReader br = new BufferedReader(new InputStreamReader((conn.getInputStream())));
//            BufferedWriter writer = new BufferedWriter(new FileWriter("genre_rating.csv"));
//            
//            String output;
//            if ((output = br.readLine()) != null) {
//                JSONParser parser = new JSONParser();
//                JSONObject json = null;
////                try {
//////                    json = (JSONObject) parser.parse(output);
////                } catch (ParseException e) {
////                    e.printStackTrace();
////                    System.exit(1);
////                }
//                System.out.println(output);
//            }
//            writer.close();
            conn.disconnect();
        } catch (MalformedURLException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
