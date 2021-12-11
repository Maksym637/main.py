from flask_bcrypt import check_password_hash
from flask_httpauth import HTTPBasicAuth

from RestApiImplementation.models_api import User

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):  # for authorisation !!!
    user = User.query.filter_by(username=username).first()
    if user is not None and check_password_hash(user.password, password):
        return username