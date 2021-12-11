from flask import Flask
from flask_httpauth import HTTPBasicAuth
app = Flask(__name__)
# auth = HTTPBasicAuth()
from RestApiImplementation.Blue_print.user import user
from RestApiImplementation.Blue_print.auditorium import auditorium
from RestApiImplementation.Blue_print.access import access
# auth = HTTPBasicAuth()
# app = Flask(__name__)
app.register_blueprint(user)
app.register_blueprint(auditorium)
app.register_blueprint(access)


@app.route("/api/v1/hello-world-7")
def index():
    return "Hello World 7!"


def hello():
    print("Hello there")