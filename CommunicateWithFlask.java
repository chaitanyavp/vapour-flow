import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.DataOutputStream;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.ProtocolException;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.ArrayList;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

public class CommunicateWithFlask {

	private String urlString;

	public CommunicateWithFlask() {
		urlString = "http://127.0.0.1:5000";
	}

	public void sendPost(HashMap<String, String> params, ArrayList<String> lines) throws IOException, RuntimeException {
		URL url = new URL(urlString+"/json");
		HttpURLConnection conn = (HttpURLConnection) url.openConnection();
		conn.setRequestMethod("POST");
		conn.setRequestProperty("Accept", "application/json");
		conn.setRequestProperty("Content-Type", "application/json; charset=utf-8");

		conn.setRequestProperty("User-Agent", "baddiy");
		conn.setRequestProperty("Accept-Language", "UTF-8");

		JSONArray arr = new JSONArray();
		arr.addAll(0, lines);

		JSONObject good = new JSONObject();
		if (params != null) {
			good.putAll(params);
		}
		good.put("list", arr);
		if (good.get("good") == null) {
			good.put("good", "bad");
		}

		conn.setDoOutput(true);
		OutputStreamWriter outputStreamWriter = new OutputStreamWriter(conn.getOutputStream());
		outputStreamWriter.write(good.toString());
		outputStreamWriter.flush();

		if (conn.getResponseCode() != 200) {
			throw new RuntimeException("Failed : HTTP error code : " + conn.getResponseCode());
		}
		outputStreamWriter.close();
		conn.disconnect();
	}

	public void sendCreateGet() throws IOException, RuntimeException {
		try {
			URL url = new URL(urlString + "/create");
			HttpURLConnection conn = (HttpURLConnection) url.openConnection();
			conn.setRequestMethod("GET");
			conn.setRequestProperty("Accept", "application/json");
			if (conn.getResponseCode() != 200) {
				throw new RuntimeException("Failed : HTTP error code : " + conn.getResponseCode());
			}
		} catch (MalformedURLException e) {
			e.printStackTrace();
		}

	}

	public void sendTrainGet() throws IOException, RuntimeException {
		try {
			URL url = new URL(urlString + "/train");
			HttpURLConnection conn = (HttpURLConnection) url.openConnection();
			conn.setRequestMethod("GET");
			conn.setRequestProperty("Accept", "application/json");
			if (conn.getResponseCode() != 200) {
				throw new RuntimeException("Failed : HTTP error code : " + conn.getResponseCode());
			}
		} catch (MalformedURLException e) {
			e.printStackTrace();
		}
	}

	public String sendPredictPut(String gameName, String gameGenres) throws IOException, RuntimeException {
		try {
			URL url = new URL(urlString + "/predict");
			HttpURLConnection conn = (HttpURLConnection) url.openConnection();
			conn.setRequestMethod("PUT");
			conn.setRequestProperty("Accept", "application/json");
			conn.setRequestProperty("Content-Type", "application/json; charset=utf-8");

			JSONObject good = new JSONObject();
			good.put("gameName", gameName);
			good.put("gameGenres", gameGenres);

			conn.setDoOutput(true);
			OutputStreamWriter outputStreamWriter = new OutputStreamWriter(conn.getOutputStream());
			outputStreamWriter.write(good.toString());
			outputStreamWriter.flush();

			if (conn.getResponseCode() != 200) {
				throw new RuntimeException("Failed : HTTP error code : " + conn.getResponseCode());
			}

			BufferedReader br = new BufferedReader(new InputStreamReader((conn.getInputStream())));
			String output;
			if ((output = br.readLine()) != null) {
				br.close();
				conn.disconnect();
				return output;
			}
		} catch (MalformedURLException e) {
			e.printStackTrace();
		}
		return "0";
	}
}
