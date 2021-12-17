from flask import request, g
from functools import wraps


def needs_premium(fn):
    @wraps(fn)
    def decorated(*args, **kwargs):
        user = g.user
        if not user.is_premium:
            return {'message': 'Missig premium access'}, 402
        
        return fn(*args, **kwargs)

    return decorated
