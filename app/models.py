from flask_sqlalchemy import SQLAlchemy
from passlib.hash import pbkdf2_sha256 as sha256

db = SQLAlchemy()


class Account(db.Model):
    """
    Create an Account table
    """

    # Ensures table will be named in plural and not signular as is the name of the model
    __tablename__ = "accounts"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(60), index=True, unique=True)
    username = db.Column(db.String(60), index=True, unique=True)
    first_name = db.Column(db.String(60), index=True)
    last_name = db.Column(db.String(60), index=True)
    password = db.Column(db.String(128))
    department_id = db.Column(db.Integer)  # for future use
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    is_admin = db.Column(db.Boolean, default=False)

    """
    Save account details in Database
    """

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    """
    Find user by username
    """

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    """
    Return all the user data in json from available in DB
    """

    @classmethod
    def get_all(cls):
        def to_json(x):
            return {
                'username': x.username,
                'password': x.password
            }

        return {'users': [to_json(user) for user in Account.query.all()]}

    @classmethod
    def delete_all(cls):
        try:
            num_rows_deleted = db.session.query(cls).delete()
            db.session.commit()
            return {'message': f'{num_rows_deleted} row(s) deleted'}
        except:
            return {'message': 'Something went wrong'}

    """
    generate hash from password by encryption using sha256
    """

    @staticmethod
    def generate_hash(password):

        return sha256.hash(password)

    """
    Verify hash and password
    """

    @staticmethod
    def verify_hash(password, hash_):

        return sha256.verify(password, hash_)


class Role(db.Model):
    """
    Create a Role table
    """
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True)
    description = db.Column(db.String(200))
    accounts = db.relationship('Account', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role: {}>'.format(self.name)


class RevokedTokenModel(db.Model):
    """
    Revoked Token Model class
    """

    __tablename__ = 'revoked_tokens'
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(120))

    """
    Save token in DB
    """

    def add(self):
        db.session.add(self)
        db.session.commit()

    """
    Checking that token is blacklisted
    """

    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti=jti).first()
        return bool(query)
