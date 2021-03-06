from flask import request, Blueprint, g, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from setup import app, db, auth
from itsdangerous import (JSONWebSignatureSerializer as Serializer, BadSignature)

user_app = Blueprint('user_app', __name__)

@user_app.route('/api/users', methods=['POST'])
def new_user():
    """
    Creates a new user
    """
    email = request.json.get('email')
    password = request.json.get('password')
    is_premium = request.json.get('premium')
    if email is None or password is None:
        return {'message': 'Invalid credentials'}, 400
    if User.query.filter_by(email=email).first() is not None:
        return {'message': 'Email already registered'}, 409
    user = User(email=email, is_premium=is_premium)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return {'message': 'User created'}, 200

@user_app.route('/api/token', methods=['GET'])
@auth.login_required
def get_token():
    """
    Returns a auth token for the user logged in, which can be used
    for future authentications, instead of credentials
    """
    return jsonify({'token': g.user.generate_token().decode("utf-8")}), 200


@auth.verify_password
def verify_password(email, password):
    """
    verify_password function for HTTPAuth
    """
    user = User.verify_token(email)
    if not user:
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return False
    g.user = user
    return True

class User(db.Model):
    """
    The User Class Model, referencing to 'users' table in the database
    
    Should ALWAYS be initialized like this: User(email=myemail, is_premium=premium)
    NEVER initialize with a password without calling .hash_password before committing.
    """
    __tablename__ = 'users'

    email = db.Column(db.String(100), primary_key=True)
    password = db.Column(db.String(256), nullable=False)
    is_premium = db.Column(db.Boolean(), default=False, nullable=False)

    def hash_password(self, pw: str):
        """
        Hashes the password to be stored in the database
        """
        self.password = generate_password_hash(pw)

    def check_password(self, pw: str) -> bool:
        """
        Checks for the correct password by comparing the hashes
        """
        return check_password_hash(self.password, pw)

    def generate_token(self):
        """
        Generates an auth token for the user
        """
        s = Serializer(app.config['SECRET_KEY'])
        return s.dumps({'email': self.email})

    @staticmethod
    def verify_token(token):
        """
        Verifies the auth token and returns the user if found, None if not found
        """
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
            user = User.query.get(data['email'])
            return user
        except BadSignature:
            return None
    



