from flask_bcrypt import check_password_hash
from marshmallow import ValidationError
from RestApiImplementation.models_api import User
from RestApiImplementation.schemas import UserSchema, LoginSchema, UpdateUserSchema
from flask import request, jsonify, Response, Blueprint
from RestApiImplementation.auth import auth
import bcrypt
import base64

user = Blueprint("user", __name__)


from RestApiImplementation.utils_db import (
    create_entry,
    get_entry_by_username,
    update_entry_by_id,
    delete_entry_by_username
)


@user.route("/login", methods=["GET"])
def login_user():
    data = request.get_json(force=True)
    try:
        LoginSchema().load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400
    message = data["username"] + ":" + data["password"]
    message_bytes = message.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')
    user = User.query.filter_by(username=data["username"]).first()
    if user is not None and check_password_hash(user.password, data["password"]):
        return base64_message
    else:
        return Response(status=404, response="Invalid password or username !")


@user.route("/user", methods=["POST"])
def create_user():
    data = request.get_json(force=True)
    try:
        UpdateUserSchema().load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400
    pwd = request.json.get('password', None)
    hashed_pwd = bcrypt.hashpw(pwd.encode("utf-8"), bcrypt.gensalt())
    data.update({"password": hashed_pwd})
    return create_entry(User, UserSchema, **data)


@user.route("/user/<string:username>", methods=["GET"])
@auth.login_required
def get_user_by_username(username):
    user = User.query.filter_by(username=username).first()
    login_user = User.query.filter_by(username=auth.current_user()).first()
    if not user:
        return Response(status=404, response="Such username does not exist!")
    if login_user.user_status == 1 or login_user.username == username:
        return get_entry_by_username(User, UserSchema, username)
    return Response(status=401, response="You have no access to get this")


@user.route("/user", methods=["PUT"])
@auth.login_required
def update_user_by_id():
    data = request.get_json(force=True)
    try:
        UpdateUserSchema().load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400
    pwd = request.json.get('password', None)
    hashed_pwd = bcrypt.hashpw(pwd.encode("utf-8"), bcrypt.gensalt())
    data.update({"password": hashed_pwd})
    user = User.query.filter_by(username=auth.current_user()).first()
    return update_entry_by_id(User, UserSchema, user.id, **data)


@user.route("/user/<string:username>", methods=["DELETE"])
@auth.login_required
def delete_user_by_username(username):
    user = User.query.filter_by(username=username).first()
    login_user = User.query.filter_by(username=auth.current_user()).first()
    if not user:
        return Response(status=404, response="Such username does not exist!")
    if login_user.user_status == 1 or login_user.username == username:
        return delete_entry_by_username(User, UserSchema, user.username)
    return Response(status=401, response="You have no access to delete this")