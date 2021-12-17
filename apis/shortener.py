from flask import request, Blueprint, g, redirect
import string
import re
from datetime import datetime, timedelta

from .auth import needs_premium
from setup import app, db, auth

from user.user import User

alphabet = string.digits + string.ascii_uppercase + string.ascii_lowercase
DAYS_VALID = 30


url_app = Blueprint('url_app', __name__)

def b62encode(seed):
    if seed == 0:
        return alphabet[0]

    length = len(alphabet)
    enc = ''
    while seed != 0:
        enc = alphabet[seed % length] + enc
        seed //= length

    return enc if len(enc) == 7 else enc + ('=' * (7 - len(enc)))

@url_app.route('/api/random')
@auth.login_required
def generate_random_url():
    long_url = request.json.get('long_url')
    if long_url is None or not validate_url(long_url):
        return {'message': 'Invalid URL'}, 400
    user = g.user
    slug_count = SlugCount.increment()
    short_url = URL(id=b62encode(slug_count.count), url=long_url, owner=user.email)
    db.session.add(short_url)
    db.session.commit()
    return short_url.id, 201

@url_app.route('/api/custom')
@auth.login_required
@needs_premium
def generate_custom_url():
    long_url = request.json.get('long_url')
    custom_url = request.json.get('short_url')
    if long_url is None or not validate_url(long_url):
        return {'message': 'Invalid long URL'}, 400
    if custom_url is None:
        return {'message': 'Missing short URL'}, 400
    if len(custom_url) >= 249:
        return {'message': 'URL size must be under 250 characters'}, 400
    if URL.query.filter_by(id=custom_url).first() is not None:
        print(URL.query.filter_by(id=custom_url).first().url)
        print(custom_url)
        return {'message': 'URL already in use'}, 400
    user = g.user
    SlugCount.increment()
    short_url = URL(id=custom_url, url=long_url, owner=user.email)
    db.session.add(short_url)
    db.session.commit()
    return short_url.id, 201
    
@url_app.route('/<id>')
def url_redirect(id):
    url = URL.query.get(id)
    if url is None:
        return {'message': 'URL not found'}, 404
    url.times_accessed += 1
    db.session.commit()
    return redirect(url.url), 302

def validate_url(url):
    regex = re.compile(r'^(http|https)://[^ "]+$')
    return re.match(regex, url) is not None

class SlugCount(db.Model):
    __tablename__= 'slug'
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer)

    @staticmethod
    def get_count():
        return SlugCount.query.order_by(SlugCount.id).first().count

    @staticmethod
    def increment():
        slug_count = SlugCount.query.order_by(SlugCount.id).first()
        slug_count.count += 1
        db.session.commit()
        return slug_count

class URL(db.Model):
    __tablename__ = 'urls'
    id = db.Column(db.String(10), primary_key=True)
    url = db.Column(db.String(249), nullable=False)
    owner = db.Column(db.String(256), db.ForeignKey('users.email'))
    times_accessed = db.Column(db.Integer, default=0)
    created = db.Column(db.DateTime, default=datetime.utcnow())

    @staticmethod
    def clear_expired():
        limit = datetime.utcnow() - timedelta(seconds=1)
        URL.query.filter(URL.created <= limit).delete()
        db.session.commit()
