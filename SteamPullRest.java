import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.HashMap;

import javax.swing.JOptionPane;

import java.util.ArrayList;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

public class SteamPullRest {

  private static HashMap<String, Integer> numbers;

  public static void main(String[] args) throws IOException {
    String steamID = "76561198069391194"; // beta
    // String steamID = "76561198170201429"; //Pran
    // String steamID = "76561198094806813"; //quick

    ArrayList<String> lines = null;
    File f = new File("userfiles/userdata_" + steamID + ".csv");
    if (f.exists() && !f.isDirectory()) {
      int useData = JOptionPane.showConfirmDialog(null, "Player data already on file. Use this?",
          "Player data already on file", JOptionPane.YES_NO_OPTION);
      if (useData == 0) {
        lines = readFromFile("userfiles/userdata_" + steamID + ".csv");
      }
    }

    if (lines == null) {
      lines = downloadSteamData(steamID);
    }

    CommunicateWithFlask comm = new CommunicateWithFlask();
    comm.sendCreateGet();
    comm.sendPost(null, lines);
    comm.sendTrainGet();
    comm.sendPredictPut("Civ 6", "False,False,False,False,False,False,False,False,False,True");
  }

  private static ArrayList<String> downloadSteamData(String steamID) {
    String key = getApiKey(); // Enter api key
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

    ArrayList<String> lines = new ArrayList<String>();

    try {

      URL url = new URL(urlString);
      HttpURLConnection conn = (HttpURLConnection) url.openConnection();
      conn.setRequestMethod("GET");
      conn.setRequestProperty("Accept", "application/json");

      if (conn.getResponseCode() != 200) {
        throw new RuntimeException("Failed : HTTP error code : " + conn.getResponseCode());
      }

      BufferedReader br = new BufferedReader(new InputStreamReader((conn.getInputStream())));
      BufferedWriter writer =
          new BufferedWriter(new FileWriter("userfiles/userdata_" + steamID + ".csv"));

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
            String output_string = getGameString(appID);
            output_string += playTime + "\n";

            writer.write(output_string);
            System.out.println(playTime);
          }
        }
      }
      writer.close();
      conn.disconnect();

    } catch (MalformedURLException e) {

      e.printStackTrace();

    } catch (IOException e) {

      e.printStackTrace();

    }

    return lines;
  }

  private static ArrayList<String> getGenres(long appID) {
    String genreUrl =
        "https://store.steampowered.com/api/appdetails/?appids=" + appID + "&filters=genres";
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
          Object appData = appResults.get("data");
          if (appData != null
              && appData.getClass().toString().equals("class org.json.simple.JSONObject")) {
            JSONArray genresReturned = (JSONArray) ((JSONObject) appData).get("genres");
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

  private static String getGameString(long appID) {
    ArrayList<String> genreList = getGenres(appID);

    String outputString = "";
    String[] nums = convertGenreToBool(genreList);
    for (String num : nums) {
      if (outputString.length() != 0) {
        outputString += ",";
      }
      outputString += num;
    }

    for (String genre : genreList) {
      System.out.print(genre + " ");
    }

    return outputString;
  }

  private static String[] convertGenreToBool(ArrayList<String> genreList) {
    String[] genreLine =
        {"False", "False", "False", "False", "False", "False", "False", "False", "False", "False"};
    for (String genre : genreList) {
      if (numbers.containsKey(genre)) {
        genreLine[numbers.get(genre)] = "True";
      }
    }
    return genreLine;
  }

  private static ArrayList<String> readFromFile(String path) {
    BufferedReader reader;
    try {
      reader = new BufferedReader(new FileReader(path));
    } catch (FileNotFoundException e1) {
      e1.printStackTrace();
      return null;
    }

    String line;
    ArrayList<String> lines = new ArrayList<String>();
    try {
      while ((line = reader.readLine()) != null) {
        lines.add(line);
      }
    } catch (IOException e) {
      e.printStackTrace();
    }

    return lines;
  }

  private static String getApiKey() {
    BufferedReader reader;
    try {
      reader = new BufferedReader(new FileReader("api.key"));
    } catch (FileNotFoundException e1) {
      e1.printStackTrace();
      return null;
    }

    String line = "";
    try {
      line = reader.readLine();
    } catch (IOException e) {
      e.printStackTrace();
    }

    return line;
  }

}
