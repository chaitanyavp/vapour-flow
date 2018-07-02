# vapour-flow
A machine learning program which uses Tensorflow and the Steam API to predict how long a player would spend on a game. 
Trains a deep neural network regressor using personalized player data and game genres from Steam API.

To compile and use:

1. Make sure you have Python 3.6 (64-bit) and a JRE as well as JDK.
2. ```pip install -r dependencies.txt```
3. Add json-simple-1.1.jar to your java project build path.
4. Get your own Steam API key and save it in a file called api.key
5. Run app.py
6. Compile and run GuiCreator.java

The Steam User ID that the program asks for is the 64-bit number associated with your Steam profile, and the AppID can be found in the url of any game's store page. 

Disclaimer: If you decide to fork and use this program, you will be using your own Steam API key and I am not responsible for any breaches of Valve's terms and conditions you may decide to do. Please read their API terms before proceeding.
