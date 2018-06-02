import java.io.BufferedReader;
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

public class SteamPullRest {
	
	private static HashMap<String, Integer> numbers;
	
	public static void main(String[] args) throws IOException {
		String key = ""; //Enter api key
		String steamID = "76561198069391194";
		String urlString = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=" + key 
				+ "&steamid=" + steamID + "&format=json";
		numbers = new HashMap<String, Integer>();
		numbers.put("Action", 0);
		numbers.put("Adventure", 1);
		numbers.put("Casual", 2);
		numbers.put("Indie", 3);
		numbers.put("Massively Multiplayer", 4);
		numbers.put("Racing", 5);
		numbers.put("RPG", 6);
		numbers.put("Simulation", 7);
		numbers.put("Sports", 8);
		numbers.put("Strategy", 9);
		
		try {

			URL url = new URL(urlString);
			HttpURLConnection conn = (HttpURLConnection) url.openConnection();
			conn.setRequestMethod("GET");
			conn.setRequestProperty("Accept", "application/json");

			if (conn.getResponseCode() != 200) {
				throw new RuntimeException("Failed : HTTP error code : " + conn.getResponseCode());
			}
			
			BufferedReader br = new BufferedReader(new InputStreamReader((conn.getInputStream())));

			String output;

			if ((output = br.readLine()) != null) {
				JSONParser parser = new JSONParser();
				JSONObject json = null;
				try {
					json = (JSONObject) parser.parse(output);
				} catch (ParseException e) {
					e.printStackTrace();
					System.exit(1);
				}
				JSONArray gamesList = (JSONArray) ((JSONObject) json.get("response")).get("games");
				for (Object game : gamesList) {
					long playTime = (long) ((JSONObject) game).get("playtime_forever");
					long appID = (long) ((JSONObject) game).get("appid");
					if (playTime > 0) {
						System.out.print(appID + " ");
						ArrayList<String> genreList = getGenres(appID);
						for (String genre : genreList) {
							System.out.print(genre + " ");
						}
						System.out.println(playTime);
					}
				}
			}
			conn.disconnect();

		} catch (MalformedURLException e) {

			e.printStackTrace();

		} catch (IOException e) {

			e.printStackTrace();

		}

	}

	private static ArrayList<String> getGenres(long appID) {
		String genreUrl = "https://store.steampowered.com/api/appdetails/?appids=" + appID + "&filters=genres";
		ArrayList<String> genreList = new ArrayList<String>();
		try {
			URL url = new URL(genreUrl);
			HttpURLConnection conn = (HttpURLConnection) url.openConnection();
			conn.setRequestMethod("GET");
			conn.setRequestProperty("Accept", "application/json");

			if (conn.getResponseCode() != 200) {
				throw new RuntimeException("Failed : HTTP error code : " + conn.getResponseCode());
			}

			BufferedReader br = new BufferedReader(new InputStreamReader((conn.getInputStream())));
			String output;

			if ((output = br.readLine()) != null) {
				JSONParser parser = new JSONParser();
				JSONObject json = null;
				try {
					json = (JSONObject) parser.parse(output);
				} catch (ParseException e) {
					e.printStackTrace();
					System.exit(1);
				}

				JSONObject appResults = ((JSONObject) json.get(((Long) appID).toString()));
				if (appResults != null) {
					JSONObject appData = (JSONObject) appResults.get("data");
					if (appData != null) {
						JSONArray genresReturned = (JSONArray) appData.get("genres");
						for (Object genre : genresReturned) {
							String genreName = (String) ((JSONObject) genre).get("description");
							if (genreName != null) {
								genreList.add(genreName);
							}
						}
					}
				}
			}
			conn.disconnect();

		} catch (MalformedURLException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}

		return genreList;
	}

	private static int[] convertGenreToInt(ArrayList<String> genreList) {
		int[] genreLine = { 0, 0, 0, 0, 0, 0, 0, 0, 0 };
		for (String genre : genreList) {
			if (numbers.containsKey(genre)) {
				genreLine[numbers.get(genre)] = 1;
			}
		}
		return genreLine;
	}

}
