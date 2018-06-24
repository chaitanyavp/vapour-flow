from flask import Flask
from flask import request
import sys
from steam_data_regressor import SteamDataRegressor

app = Flask(__name__)

regressor = None

@app.route("/")
def hello():
    return "Hello World!"


@app.route('/create', methods=["GET"])
def create_model():
    global regressor
    regressor = SteamDataRegressor()
    regressor.create_model()
    print("model created", file=sys.stderr)
    return "good"


@app.route('/json', methods=["POST"])
def store_data():
    json_dict = request.get_json()
    if json_dict is not None:
        print(request.mimetype, json_dict['good'], file=sys.stderr)
        print(type(json_dict['list']), file=sys.stderr)
        _write_data_to_file(json_dict['list'])
        return "good"
    else:
        return "bad"


@app.route('/train', methods=["GET"])
def train_data():
    global regressor
    if regressor is not None:
        regressor.prepare_existing_model()
        return "good"
    else:
        return "bad"


@app.route('/predict', methods=["PUT"])
def make_prediction():
    json_dict = request.get_json()
    print(request.data, file=sys.stderr)
    if json_dict is not None and json_dict['gameName'] is not None and json_dict['gameGenres'] is not None:
        global regressor
        genres = json_dict['gameGenres'].split(',')
        assert len(genres) == 10
        predict_x = {
            'Action': [genres[0]],
            'Adventure': [genres[1]],
            'Casual': [genres[2]],
            'Indie': [genres[3]],
            'Massively_Multiplayer': [genres[4]],
            'Racing': [genres[5]],
            'RPG': [genres[6]],
            'Simulation': [genres[7]],
            'Sports': [genres[8]],
            'Strategy': [genres[9]]
        }
        return regressor.make_prediction(predict_x, [json_dict['gameName']])
    else:
        return "bad"


def _write_data_to_file(line_list):
    out_file = open("steam_data.csv", 'w+')
    for line in line_list:
        out_file.write(line+"\n")

if __name__ == "__main__":
    app.run("127.0.0.1", "5000")
