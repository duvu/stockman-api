# third-party imports
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
# local imports
from app import resources
from config import app_config

db = SQLAlchemy()
# JwtManager object
jwt = JWTManager()

def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')

    # SqlAlchemy object
    db.init_app(app)
    jwt.init_app(app)

    # Generating tables before first request is fetched
    @app.before_first_request
    def create_tables():
        db.create_all()

    api = Api(app)

    api.add_resource(resources.AccountRegistration, '/registration')
    api.add_resource(resources.AccountLogin, '/login')
    api.add_resource(resources.AccountLogout, '/logout/access')
    api.add_resource(resources.AccountogoutRefresh, '/logout/refresh')
    api.add_resource(resources.TokenRefresh, '/token/refresh')
    # api.add_resource(resources.AllUsers, '/users')
    api.add_resource(resources.SecretResource, '/secret')

    migrate = Migrate(app, db)
    from app import models

    return app
