from flask_httpauth import HTTPBasicAuth
from marshmallow import ValidationError
from sqlalchemy import and_
from RestApiImplementation.models_api import Access, User, Auditorium
from RestApiImplementation.schemas import AccessSchema, CreateAccessSchema
from flask import request, jsonify, Response, Blueprint
from datetime import datetime, timedelta
from RestApiImplementation.auth import auth

access = Blueprint("access", __name__)

from RestApiImplementation.utils_db import (
    create_entry,
    get_entries,
    delete_entry_by_ids,
    get_entries_by_id_many,
    check_time
)


@access.route("/access", methods=["POST"])
@auth.login_required
def create_access():
    user = User.query.filter_by(username=auth.current_user()).first()
    access_data = request.get_json(force=True)

    # warn: you can not book auditorium for another person
    if user.id != int(access_data.get('user_id')):
        return Response(status=401, response="You can't book auditorium for another person!")
    try:
        CreateAccessSchema().load(access_data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    # set time
    start = request.json.get('start', None)
    end = request.json.get('end', None)
    if start is None or end is None:
        return Response(status=404, response="You must reserve your auditorium!")
    start = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
    end = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
    if start < datetime.now() or end < datetime.now():
        return Response(status=400, response="You can't book auditorium in the past")
    time = end - start
    if time <= timedelta(hours=1):
        return Response(status=400, response="Invalid access time (too short)")
    if time >= timedelta(hours=5):
        return Response(status=400, response="Invalid access time (too long)")

    auditorium_id = int(request.json.get('auditorium_id', None))
    check_time(Access, AccessSchema, auditorium_id, start, end)

    access_data = AccessSchema().load(request.get_json())
    return create_entry(Access, AccessSchema, **access_data)


@access.route("/access/<int:user_id>", methods=["GET"])
@auth.login_required
def get_access(user_id):
    exist_user = User.query.filter_by(id=user_id).first()
    if not exist_user:
        return Response(status=404, response="Such user does not exist so there are no reservation for him")

    login_user = User.query.filter_by(username=auth.current_user()).first()
    if login_user.user_status == 1:
        return get_entries(Access, AccessSchema)

    # access = Access.query.filter_by(user_id=user_id).first()
    access_user = Access.query.filter(and_(Access.user_id == login_user.id, Access.user_id == user_id)).first()
    if not access_user:
        return Response(status=404, response="You do not have access to see such reservations")
    return get_entries_by_id_many(Access, AccessSchema, user_id)


@access.route("/access/<int:auditorium_id>", methods=["DELETE"])
@auth.login_required
def delete_access_by_two_ids(auditorium_id):
    exist_aud = Auditorium.query.filter_by(id=auditorium_id).first()
    if not exist_aud:
        return Response(status=404, response="Such auditorium does not exist")

    access = Access.query.filter_by(auditorium_id=auditorium_id).first()
    login_user = User.query.filter_by(username=auth.current_user()).first()
    if login_user.user_status == 1:
        return delete_entry_by_ids(Access, AccessSchema, access.user_id, auditorium_id)

    access_user = Access.query.filter(and_(Access.user_id == login_user.id, Access.auditorium_id == auditorium_id)).first()
    if not access_user:
        return Response(status=404, response="You do not have access to this auditorium")
    return delete_entry_by_ids(Access, AccessSchema, access.user_id, auditorium_id)