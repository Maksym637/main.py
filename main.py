from flask import Flask

app = Flask(__name__)
# Hello Program!
@app.route("/api/v1/hello-world-7")
def hello_world():
    return "Hello World 7"