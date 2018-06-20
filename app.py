from flask import Flask
from flask import request

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

@app.route('/json-example')
def json_example():
    return 'Todo...'