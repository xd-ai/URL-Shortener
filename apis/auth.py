from flask import request
from functools import wraps
from app import User

auth = {
    'apikey': {
        'type': 'apikey',
        'in': 'header',
        'name': 'X-API-KEY'
    }
}

def needs_token(fn):
    @wraps(fn)
    def decorated(*args, **kwargs):
        token = None
        try:
            token = request.headers['X-API-KEY']
        except KeyError:
            return {'message': 'Authentication token is missing'}, 401

        user = User.verify_token(token)
        if not user:
            return {'message': 'User not found'}, 401

        return fn(*args, **kwargs)

    return decorated

def needs_premium(fn):
    @wraps(fn)
    def decorated(*args, **kwargs):
        token = request.headers['X-API-KEY']
        user = User.verify_token(token)
        if not user.is_premium:
            return {'message': 'Missig premium access'}, 402
        
        return fn(*args, **kwargs)

    return decorated
