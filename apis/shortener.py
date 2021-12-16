from flask import request
from app import app
from .auth import needs_token, needs_premium
from user.user import User

@app.route('/random')
@needs_token
def generate_random_url():
    token = request.headers["X-API-KEY"]
    user = User.verify_token(token)

