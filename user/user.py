from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, app, login_manager
from itsdangerous import (JSONWebSignatureSerializer as Serializer, BadSignature)


@login_manager.user_loader
def load_user(email):
    return User.query.get(email)

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    email = db.Column(db.String(100), primary_key=True)
    password = db.Column(db.String(256), nullable=False)
    is_premium = db.Column(db.Boolean(), default=False, nullable=False)

    def set_password(self, pw: str):
        self.password = generate_password_hash(pw)

    def check_password(self, pw: str) -> bool:
        return check_password_hash(self.password, pw)

    def get_id(self) -> str:
        return self.email

    def generate_token(self):
        s = Serializer(app.config['SECRET_KEY'])
        return s.dumps({'email': self.email})

    @staticmethod
    def verify_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
            user = User.query.get(data['email'])
            return user
        except BadSignature:
            return None
    



