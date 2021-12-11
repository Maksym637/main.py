import base64
import pytest

from RestApiImplementation.models_api import User, Session, Auditorium, Access
from RestApiImplementation.app import app
import json

from RestApiImplementation.schemas import UserSchema
from RestApiImplementation.utils_db import delete_entry_by_username

session = Session()
app_context = app.app_context()
app_context.push()

client = app.test_client()


@pytest.fixture
def db_user():
    user_1 = User(username="user1", email="user1@gmail.com",
                  password="$2b$12$d6WEU3NWbpZjtIVOk8bPOeP6Mg47m6X2TcRxzwaqSqyPSJRun2b5O", phone="1111",
                  user_status=False)
    with Session() as session:
        session.add(user_1)
        session.commit()
    yield
    delete_entry_by_username(User, UserSchema, "user1")


# ALL TESTS WITH USERS

def test_login_user():
    url = '/login'
    response = client.get(url, data=json.dumps({"username": "user3", "password": "pas3"}))
    assert response.status_code == 200


def test_login_user_error():
    url = '/login'
    response = client.get(url, data=json.dumps({"username": "user3", "password": "WRONG"}))
    assert response.status_code == 404


def test_create_and_delete_user():
    send_data = {
        "username": "user1",
        "email": "user1@gmail.com",
        "password": "pas1",
        "phone": "1111"
    }

    # create
    url_create = '/user'
    response = client.post(url_create, data=json.dumps(send_data), content_type='application/json')
    assert response.status_code == 200

    # delete_by_username
    url_delete_by_username = '/user/user1'
    headers = {"Authorization": f"Basic dXNlcjE6cGFzMQ=="}
    response = client.delete(url_delete_by_username, headers=headers)
    assert response.status_code == 200


def test_create_user_error():
    send_data = {
        "username": "WRONG",
        "email": "WRONG@gmail.com",
        "password": "WRONG",
        "phone": 1111
    }
    url_create = '/user'
    response = client.post(url_create, data=json.dumps(send_data), content_type='application/json')
    assert response.status_code == 400


def test_get_user(db_user):
    url = '/user/user1'
    headers = {"Authorization": f"Basic dXNlcjE6cGFzMQ=="}
    response = client.get(url, headers=headers)
    assert response.status_code == 200


def test_get_user_error_1(db_user):
    url = '/user/user10'
    headers = {"Authorization": f"Basic dXNlcjE6cGFzMQ=="}
    response = client.get(url, headers=headers)
    assert response.status_code == 404


def test_get_user_error_2(db_user):
    url = '/user/user2'
    headers = {"Authorization": f"Basic dXNlcjE6cGFzMQ=="}
    response = client.get(url, headers=headers)
    assert response.status_code == 401


def test_put_user():
    send_new_data = {
        "first_name": "AAA1",
        "last_name": "BBB2",
        "password": "pas2"
    }
    url = '/user'
    headers = {"Authorization": f"Basic dXNlcjI6cGFzMg=="}
    response_put = client.put(url, data=json.dumps(send_new_data), content_type='application/json', headers=headers)
    assert response_put.status_code == 200


def test_put_user_error():
    send_new_data = {
        "first_name": "AAA1",
        "last_name": 12,
        "password": "pas2"
    }
    url = '/user'
    headers = {"Authorization": f"Basic dXNlcjI6cGFzMg=="}
    response_put = client.put(url, data=json.dumps(send_new_data), content_type='application/json', headers=headers)
    assert response_put.status_code == 400


# ALL TESTS WITH AUDITORIUM

def test_create_update_and_delete_auditorium():
    # create
    send_data = {
        "auditorium_number": 10,
        "max_people_count": 100
    }
    url = '/auditorium'
    response = client.post(url, data=json.dumps(send_data), content_type='application/json')
    assert response.status_code == 200
    assert response.json["max_people_count"] == 100

    auditorium = Auditorium.query.filter_by(auditorium_number=10).first()
    url_put = f'/auditorium/{auditorium.id}'

    # update
    send_new_data = {
        "max_people_count": 150
    }
    response_put = client.put(url_put, data=json.dumps(send_new_data), content_type='application/json')
    assert response_put.status_code == 200

    # update_error
    url_put_error = f'/auditorium/5000'
    response_put = client.put(url_put_error, data=json.dumps(send_new_data), content_type='application/json')
    assert response_put.status_code == 500

    url_delete = f'/auditorium/{auditorium.id}'

    # delete
    response_delete = client.delete(url_delete)
    assert response_delete.status_code == 200


def test_create_auditorium_error():
    send_data = {
        "auditorium_number": "30",
        "max_people_count": "300",
        "is_free": "something",
    }
    url = '/auditorium'
    response = client.post(url, data=json.dumps(send_data), content_type='application/json')
    assert response.status_code == 400


def test_get_auditorium(db_user):
    url = '/auditorium'
    headers = {"Authorization": f"Basic dXNlcjE6cGFzMQ=="}
    response = client.get(url, headers=headers)
    assert response.status_code == 200


def test_get_auditorium_by_id(db_user):
    obj = session.query(Auditorium).first()
    url = f'/auditorium/{obj.id}'
    headers = {"Authorization": f"Basic dXNlcjE6cGFzMQ=="}
    response_delete = client.get(url, headers=headers)
    assert response_delete.status_code == 200


def test_delete_auditorium_error():
    url_delete = f'/auditorium/400'
    response_delete = client.delete(url_delete)
    assert response_delete.status_code == 404


# ALL TESTS WITH ACCESS (RESERVATION)

def test_create_and_delete_access():
    # create
    send_data = {
        "auditorium_id": "196",
        "user_id": "1",
        "start": "2022-04-28 11:15:00",
        "end": "2022-04-28 12:45:00",
    }
    url = '/access'
    headers = {"Authorization": f"Basic dXNlcjI6cGFzMg=="}
    response = client.post(url, data=json.dumps(send_data), headers=headers)
    assert response.status_code == 200

    # delete
    auditorium = Auditorium.query.filter_by(id=send_data["auditorium_id"]).first()
    url_delete = f'/access/{auditorium.id}'
    headers = {"Authorization": f"Basic dXNlcjI6cGFzMg=="}
    response = client.delete(url_delete, headers=headers)
    assert response.status_code == 200


def test_create_error_1():
    send_data = {
        "auditorium_id": "196",
        "user_id": "1",
        "start": "2010-04-28 11:15:00",
        "end": "2010-04-28 12:45:00"
    }
    url = '/access'
    headers = {"Authorization": f"Basic dXNlcjI6cGFzMg=="}
    response = client.post(url, data=json.dumps(send_data), headers=headers)
    assert response.status_code == 400


def test_create_error_2():
    send_data = {
        "auditorium_id": "196",
        "user_id": "1",
    }
    url = '/access'
    headers = {"Authorization": f"Basic dXNlcjI6cGFzMg=="}
    response = client.post(url, data=json.dumps(send_data), headers=headers)
    assert response.status_code == 404


def test_create_error_3():
    send_data = {
        "auditorium_id": "196",
        "user_id": "76",
        "start": "2022-04-28 11:15:00",
        "end": "2022-04-28 12:45:00"
    }
    url = '/access'
    headers = {"Authorization": f"Basic dXNlcjI6cGFzMg=="}
    response = client.post(url, data=json.dumps(send_data), headers=headers)
    assert response.status_code == 401


def test_create_error_4():
    send_data = {
        "auditorium_id": "Hello",
        "user_id": "1",
        "start": "2022-04-28 11:15:00",
        "end": "2022-04-28 12:45:00"
    }
    url = '/access'
    headers = {"Authorization": f"Basic dXNlcjI6cGFzMg=="}
    response = client.post(url, data=json.dumps(send_data), headers=headers)
    assert response.status_code == 400


def test_get_access():
    # create
    send_data = {
        "auditorium_id": "196",
        "user_id": "1",
        "start": "2030-04-28 11:15:00",
        "end": "2030-04-28 12:45:00"
    }
    url = '/access'
    headers = {"Authorization": f"Basic dXNlcjI6cGFzMg=="}
    client.post(url, data=json.dumps(send_data), headers=headers)

    # get
    user = User.query.filter_by(id=send_data["user_id"]).first()
    url_get = f'/access/{user.id}'
    headers = {"Authorization": f"Basic dXNlcjI6cGFzMg=="}
    response = client.get(url_get, headers=headers)
    assert response.status_code == 200

    # get_error
    url_get_error = f'/access/76'
    headers = {"Authorization": f"Basic dXNlcjI6cGFzMg=="}
    response = client.get(url_get_error, headers=headers)
    assert response.status_code == 404

    # delete
    auditorium = Auditorium.query.filter_by(id=send_data["auditorium_id"]).first()
    url_delete = f'/access/{auditorium.id}'
    headers = {"Authorization": f"Basic dXNlcjI6cGFzMg=="}
    response = client.delete(url_delete, headers=headers)
    assert response.status_code == 200


# TOKENS user2 : dXNlcjI6cGFzMg==    |     user3 : dXNlcjM6cGFzMw==