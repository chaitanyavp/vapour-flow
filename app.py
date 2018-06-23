from flask import Flask
from flask import request
import sys
import dnnregressor

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!"


@app.route('/json', methods=["POST"])
def json_example():
    json_dict = request.get_json()
    if json_dict is not None:
        print(request.mimetype, json_dict['good'], file=sys.stderr)
        print(type(json_dict['list']), file=sys.stderr)
        write_data_to_file(json_dict['list'])
        return "good"
    else:
        return "bad"


@app.route('/train', methods=["GET"])
def train_data():
    dnnregressor.main([""])
    return "good"


@app.route('/predict', methods=["PUT"])
def make_prediction():
    json_dict = request.get_json()
    print(request.data, file=sys.stderr)
    if json_dict is not None:
        print(request.mimetype, json_dict['gameline'], file=sys.stderr)
        return "good"
    else:
        return "bad"


def write_data_to_file(line_list):
    out_file = open("steam_data.csv", 'w+')
    for line in line_list:
        out_file.write(line+"\n")

if __name__ == "__main__":
    app.run("127.0.0.1", "5000")
