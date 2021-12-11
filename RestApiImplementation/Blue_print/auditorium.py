from flask_httpauth import HTTPBasicAuth
from RestApiImplementation.models_api import Auditorium, User
from RestApiImplementation.schemas import AuditoriumSchema, CreateAuditoriumSchema
from flask import request, Response, jsonify, Blueprint
from marshmallow import ValidationError
from RestApiImplementation.auth import auth

auditorium = Blueprint("auditorium", __name__)

from RestApiImplementation.utils_db import (
    create_entry,
    get_entries,
    get_entry_by_id,
    update_entry_by_id,
    delete_entry_by_id,
)


@auditorium.route("/auditorium", methods=["POST"])
def create_auditorium():
    auditorium_data = request.get_json(force=True)
    try:
       CreateAuditoriumSchema().load(auditorium_data)
    except ValidationError as err:
        return jsonify(err.messages), 400
    auditorium_data = AuditoriumSchema().load(request.get_json())
    return create_entry(Auditorium, AuditoriumSchema, **auditorium_data)


@auditorium.route("/auditorium", methods=["GET"])
@auth.login_required
def get_auditorium():
    return get_entries(Auditorium, AuditoriumSchema)


@auditorium.route("/auditorium/<int:id>", methods=["GET"])
@auth.login_required
def get_auditorium_by_id(id):
    exist_aud = Auditorium.query.filter_by(id=id).first()
    if not exist_aud:
        return Response(status=404, response="Such auditorium does not exist")
    return get_entry_by_id(Auditorium, AuditoriumSchema, id)


@auditorium.route("/auditorium/<int:id>", methods=["PUT"])
def update_auditorium_by_id(id):
    auditorium_data = AuditoriumSchema().load(request.get_json())
    return update_entry_by_id(Auditorium, AuditoriumSchema, id, **auditorium_data)


@auditorium.route("/auditorium/<int:id>", methods=["DELETE"])
def delete_auditorium_by_id(id):
    exist_aud = Auditorium.query.filter_by(id=id).first()
    if not exist_aud:
        return Response(status=404, response="Such auditorium does not exist")
    return delete_entry_by_id(Auditorium, AuditoriumSchema, id)