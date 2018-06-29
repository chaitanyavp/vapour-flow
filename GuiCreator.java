import java.net.ConnectException;

import javafx.application.Application;
import javafx.event.ActionEvent;
import javafx.event.EventHandler;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.control.TextField;
import javafx.scene.layout.GridPane;
import javafx.scene.layout.StackPane;
import javafx.scene.text.Font;
import javafx.scene.text.FontWeight;
import javafx.scene.text.Text;
import javafx.stage.Stage;

public class GuiCreator extends Application {

  private String stats[];

  @Override
  public void start(Stage mainPage) {
    stats = new String[] {"No", "No", ""};
    SteamPullRest steamCom = new SteamPullRest();

    Button grabUserData = new Button();
    grabUserData.setText("Grab User data");
    Button trainModel = new Button();
    trainModel.setText("Train model");
    trainModel.setDisable(true);
    Button makePredict = new Button();
    makePredict.setText("Make Prediction");
    makePredict.setDisable(true);

    GridPane grid = new GridPane();
    grid.setAlignment(Pos.TOP_CENTER);
    grid.setHgap(15);
    grid.setVgap(10);
    grid.setPadding(new Insets(25, 25, 25, 25));

    Text scenetitle = new Text("Welcome");
    scenetitle.setFont(Font.font("Tahoma", FontWeight.NORMAL, 20));
    Text resultText = new Text("");
    resultText.setFont(Font.font("Tahoma", FontWeight.NORMAL, 20));
    grid.add(scenetitle, 0, 0, 2, 1);
    grid.add(grabUserData, 2, 1, 2, 1);
    grid.add(trainModel, 0, 2, 2, 1);
    grid.add(makePredict, 2, 3, 2, 1);
    grid.add(resultText, 0, 4, 2, 1);

    Label userIDLabel = new Label("Steam User ID:");
    grid.add(userIDLabel, 0, 1);

    TextField userIDField = new TextField();
    grid.add(userIDField, 1, 1);

    Label appIDLabel = new Label("Steam AppID:");
    grid.add(appIDLabel, 0, 3);

    TextField appIDField = new TextField();
    grid.add(appIDField, 1, 3);

    grabUserData.setOnAction(new EventHandler<ActionEvent>() {
      @Override
      public void handle(ActionEvent event) {
        // try {
        steamCom.handleUserIDInput(userIDField.getText());
        // }
        // catch(ConnectException c){
        //
        // }
        stats[0] = "User Data Downloaded, " + userIDField.getText();
        setTitle(scenetitle);
        trainModel.setDisable(false);
      }
    });

    trainModel.setOnAction(new EventHandler<ActionEvent>() {
      @Override
      public void handle(ActionEvent event) {
        steamCom.handleTrainModel();
        stats[1] = userIDField.getText();
        setTitle(scenetitle);
        makePredict.setDisable(false);
      }
    });

    makePredict.setOnAction(new EventHandler<ActionEvent>() {
      @Override
      public void handle(ActionEvent event) {
        String hours = steamCom.handlePredict(Long.parseLong(appIDField.getText()));
        stats[2] = hours += " hours on " + appIDField.getText();
        setResult(resultText);
      }
    });

    mainPage.setTitle("VapourFlow Steam Tool");
    mainPage.setScene(new Scene(grid, 650, 350));
    mainPage.show();
  }

  private void setTitle(Text title) {
    title.setText(stats[0] + " data on file.\n" + stats[1] + " model trained and active.");
  }

  private void setResult(Text result) {
    if (!stats[2].equals("")) {
      result.setText(stats[1] + " is predicted to spend "+stats[2]+".");
    } else {
      result.setText("");
    }
  }

  public static void main(String[] args) {
    launch(args);
  }
}
