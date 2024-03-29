from flask_httpauth import HTTPBasicAuth

from RestApiImplementation.models_api import Session, User
from flask_bcrypt import check_password_hash
from flask import jsonify
from functools import wraps
import sqlalchemy

auth = HTTPBasicAuth()

session = Session()


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


# @app.errorhandler(InvalidUsage)
# def handle_invalid_usage(error):
#     response = jsonify(error.to_dict())
#     response.status_code = error.status_code
#     return response


def db_lifecycle(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if isinstance(e, ValueError):
                return jsonify({'message': e.args[0], 'type': 'ValueError'}), 400
            elif isinstance(e, AttributeError):
                return jsonify({'message': e.args[0], 'type': 'AttributeError'}), 400
            elif isinstance(e, KeyError):
                return jsonify({'message': e.args[0], 'type': 'KeyError'}), 400
            elif isinstance(e, TypeError):
                return jsonify({'message': e.args[0], 'type': 'TypeError'}), 400
            elif isinstance(e, sqlalchemy.exc.IntegrityError):
                return jsonify({'message': "duplicate unique value", 'type': 'IntegrityError'}), 400
            elif isinstance(e, sqlalchemy.exc.IntegrityError):
                return jsonify({'message': "duplicate unique value", 'type': 'IntegrityError'}), 400
            else:
                raise e

    return wrapper


def session_lifecycle(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            rez = func(*args, **kwargs)
            session.commit()
            return rez
        except Exception as e:
            session.rollback()
            raise e

    return wrapper


@db_lifecycle
@session_lifecycle
def create_entry(model_class, model_schema, **kwargs):
    entry = model_class(**kwargs)
    session.add(entry)
    return jsonify(model_schema().dump(entry))


@db_lifecycle
def get_entries(model_class, model_schema):
    entries = session.query(model_class).all()
    return jsonify(model_schema(many=True).dump(entries))


@db_lifecycle
def get_entry_by_id(model_class, model_schema, id):
    entry = session.query(model_class).filter_by(id=id).first()
    if entry is None:
        raise InvalidUsage("Object not found", status_code=404)
    return jsonify(model_schema().dump(entry))


@db_lifecycle
def get_entry_by_username(model_class, model_schema, username):
    entry = session.query(model_class).filter_by(username=username).first()
    if entry is None:
        raise InvalidUsage("Object not found", status_code=404)
    return jsonify(model_schema().dump(entry))


@db_lifecycle
@session_lifecycle
def update_entry_by_id(model_class, model_schema, id, **kwargs):
    entry = session.query(model_class).filter_by(id=id).first()
    if entry is None:
        raise InvalidUsage("Object not found", status_code=404)
    for key, value in kwargs.items():
        setattr(entry, key, value)
    return jsonify(model_schema().dump(entry))


@db_lifecycle
@session_lifecycle
def delete_entry_by_id(model_class, model_schema, id):
    entry = session.query(model_class).filter_by(id=id).first()
    if entry is None:
        raise InvalidUsage("Object not found", status_code=404)
    session.delete(entry)
    return jsonify(model_schema().dump(entry))


@db_lifecycle
def get_entry_by_ids(model_class, model_schema, user_id, auditorium_id):
    entry = session.query(model_class).filter_by(user_id=user_id, auditorium_id=auditorium_id).first()
    if entry is None:
        raise InvalidUsage("Object not found", status_code=404)
    return jsonify(model_schema().dump(entry))


@db_lifecycle
def get_entries_by_id_many(model_class, model_schema, user_id):
    entries = session.query(model_class).filter_by(user_id=user_id).all()
    return jsonify(model_schema(many=True).dump(entries))


@db_lifecycle
@session_lifecycle
def delete_entry_by_ids(model_class, model_schema, user_id, auditorium_id):
    entry = session.query(model_class).filter_by(user_id=user_id, auditorium_id=auditorium_id).first()
    if entry is None:
        raise InvalidUsage("Object not found", status_code=404)
    session.delete(entry)
    return jsonify(model_schema().dump(entry))


@db_lifecycle
@session_lifecycle
def delete_entry_by_username(model_class, model_schema, username):
    entry = session.query(model_class).filter_by(username=username).first()
    if entry is None:
        raise InvalidUsage("Object not found", status_code=404)
    session.delete(entry)
    return jsonify(model_schema().dump(entry))


@db_lifecycle
def check_time(model_class, model_schema, id, main_start, main_end):
    entries = session.query(model_class).all()
    for entry in entries:
        if entry.auditorium_id != id:
            continue
        start = entry.start
        end = entry.end
        # start = entry.json.get('start', None)
        # start = entry.strptime(start, '%Y-%m-%d %H:%M:%S')
        # end = entry.json.get('end', None)
        # end = entry.strptime(end, '%Y-%m-%d %H:%M:%S')

        if start < main_start and (end > main_start and end < main_end):
            raise InvalidUsage("TIME RESERVED -> 1", status_code=404)

        if start > main_start and end < main_end:
            raise InvalidUsage("TIME RESERVED -> 2", status_code=404)

        if (start > main_start and start < main_end) and end > main_end:
            raise InvalidUsage("TIME RESERVED -> 3", status_code=404)

        if start < main_start and end > main_end:
            raise InvalidUsage("TIME RESERVED -> 4", status_code=404)