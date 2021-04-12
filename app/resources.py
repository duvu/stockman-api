from flask_restful import Resource, reqparse
from app.models import Account, RevokedTokenModel
from flask import request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
import pdb

parser = reqparse.RequestParser()
parser.add_argument('username', help='username cannot be blank', required=True)
parser.add_argument('password', help='password cannot be blank', required=True)


class AccountRegistration(Resource):
    """
    User Registration Api
    """

    def post(self):
        data = parser.parse_args()
        username = data['username']

        # Checking that user is already exist or not
        if Account.find_by_username(username):
            return {'message': f'User {username} already exists'}

        # create new user
        new_user = Account(
            username=username,
            password=Account.generate_hash(data['password'])
        )

        try:
            # Saving user in DB and Generating Access and Refresh token
            new_user.save_to_db()
            access_token = create_access_token(identity=username)
            refresh_token = create_refresh_token(identity=username)
            return {
                'message': f'User {username} was created',
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        except:
            raise
            # return {'message': 'Something went wrong'}, 500


class AccountLogin(Resource):
    """
    Account Login Api
    """

    def post(self):
        data = parser.parse_args()
        username = data['username']
        # Searching user by username
        current_user = Account.find_by_username(username)

        # user does not exists
        if not current_user:
            return {'message': f'User {username} doesn\'t exist'}

        # user exists, comparing password and hash
        if Account.verify_hash(data['password'], current_user.password):
            # generating access token and refresh token
            access_token = create_access_token(identity=username)
            refresh_token = create_refresh_token(identity=username)
            return {
                'message': f'Logged in as {username}',
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        else:
            return {'message': "Wrong credentials"}


class AccountLogout(Resource):
    """
    Account logout Api
    """

    @jwt_required
    def post(self):
        jti = get_jwt()['jti']
        try:
            # Revoking access token
            revoked_token = RevokedTokenModel(jti=jti)
            revoked_token.add()
            return {'message': 'Access token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500


class AccountogoutRefresh(Resource):
    """
    Account Logout Refresh Api
    """

    @jwt_required(refresh=True)
    def post(self):

        jti = get_jwt()['jti']

        try:

            revoked_token = RevokedTokenModel(jti=jti)

            revoked_token.add()

            pdb.set_trace()

            return {'message': 'Refresh token has been revoked'}

        except:

            return {'message': 'Something went wrong'}, 500


class TokenRefresh(Resource):
    """
    Token Refresh Api
    """

    @jwt_required(refresh=True)
    def post(self):
        # Generating new access token
        current_user = get_jwt_identity()

        access_token = create_access_token(identity=current_user)

        return {'access_token': access_token}

    class AllUsers(Resource):

        def get(self):
            """
            return all user api
            """
            return Account.get_all()

        def delete(self):
            """
            delete all user api
            """
            return Account.delete_all()


class SecretResource(Resource):
    """
    Secrest Resource Api
    You can create crud operation in this way
    """

    @jwt_required
    def get(self):
        return {'answer': 'You are accessing super secret blueprint'}
