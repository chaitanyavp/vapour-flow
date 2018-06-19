package quiz2;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.HashMap;
import java.util.ArrayList;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

public class CommunicateWithFlask {
    
    public static void main(String[] args) throws IOException {
        String urlString = "http://127.0.0.1:5000";


        try {
            URL url = new URL(urlString);
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("GET");
            conn.setRequestProperty("Accept", "application/json");

            if (conn.getResponseCode() != 200) {
                throw new RuntimeException("Failed : HTTP error code : " + conn.getResponseCode());
            }

            BufferedReader br = new BufferedReader(new InputStreamReader((conn.getInputStream())));
            BufferedWriter writer = new BufferedWriter(new FileWriter("genre_rating.csv"));
            
            String output;
            if ((output = br.readLine()) != null) {
                JSONParser parser = new JSONParser();
                JSONObject json = null;
//                try {
////                    json = (JSONObject) parser.parse(output);
//                } catch (ParseException e) {
//                    e.printStackTrace();
//                    System.exit(1);
//                }
                System.out.println(output);
            }
            writer.close();
            conn.disconnect();
        } catch (MalformedURLException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}