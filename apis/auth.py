from flask import g
from functools import wraps


def needs_premium(fn):
    """
    A wrapper for endpoints that require premium access
    Always use this AFTER the login wrapper as it depends
    on the data stored by the mentioned
    """
    @wraps(fn)
    def decorated(*args, **kwargs):
        user = g.user
        if not user.is_premium:
            return {'message': 'Missig premium access'}, 402
        
        return fn(*args, **kwargs)

    return decorated
