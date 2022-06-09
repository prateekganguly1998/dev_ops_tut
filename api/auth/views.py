from werkzeug.exceptions import Conflict, BadRequest
from flask_restx import Namespace, Resource, fields
from flask import request
from ..models.users import User
from werkzeug.security import generate_password_hash, check_password_hash
from http import HTTPStatus
from flask_jwt_extended import (create_access_token,
                                create_refresh_token, get_jwt_identity,
                                jwt_required)

auth_namespace = Namespace(
    'auth', description="a namespace for authentication")

signup_model = auth_namespace.model('SignUp', {
    'id': fields.Integer(),
    'username': fields.String(required=True, description='username'),
    'email': fields.String(required=True, description=' user email'),
    'password': fields.String(required=True, description='a password')
}
)

user_model = auth_namespace.model(
    'User', {
        'id': fields.Integer(),
        'username': fields.String(required=True, description='username'),
        'email': fields.String(required=True, description=' user email'),
        'password_hash': fields.String(required=True,
                                       description='a password'),
        'is_active': fields.Boolean(description='user active status'),
        'is_staff': fields.Boolean(description='is user a member of the staff')
    }
)

login_model = auth_namespace.model(
    'Login', {
        'email': fields.String(required=True, description=' user email'),
        'password': fields.String(required=True, description='a password')
    }
)


@auth_namespace.route('/signup')
class Signup(Resource):
    @auth_namespace.expect(signup_model)
    @auth_namespace.marshal_with(user_model)
    def post(self):
        """
        Create a new user
        """
        data = request.get_json()
        try:

            new_user = User(
                username=data.get('username'),
                email=data.get('email'),
                password_hash=generate_password_hash(data.get('password')),
            )

            new_user.save()

            return new_user, HTTPStatus.CREATED
        except Exception as exc:
            print(exc)
            raise Conflict(f"User with email {data.get('email')} exists")


@auth_namespace.route('/login')
class Login(Resource):
    @auth_namespace.expect(login_model)
    def post(self):
        """
        Generate a new JWT pair.
        """

        data = request.get_json()

        email = data.get('email')
        password = data.get('password')
        user = User.query.filter_by(email=email).first()

        if user is not None and check_password_hash(user.password_hash,
                                                    password):
            access_token = create_access_token(identity=user.username)
            refresh_token = create_refresh_token(identity=user.username)

            response = {'access_token': access_token,
                        'refresh_token': refresh_token}

            return response, HTTPStatus.OK
        raise BadRequest("Invalid Username or password")


@auth_namespace.route('/refresh')
class Refresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        username = get_jwt_identity()

        access_token = create_access_token(identity=username)
        return {"access_token": access_token}, HTTPStatus.OK
