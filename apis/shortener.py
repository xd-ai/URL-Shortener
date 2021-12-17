from flask import request, Blueprint, g, redirect
import string
import re
from datetime import datetime, timedelta

from .auth import needs_premium
from setup import db, auth

alphabet = string.digits + string.ascii_uppercase + string.ascii_lowercase
DAYS_VALID = 30
URL_LEN = 7

url_app = Blueprint('url_app', __name__)

def _b62encode(seed):
    """
    A base62 encoding function, with automatic padding
    """
    if seed == 0:
        return alphabet[0]

    length = len(alphabet)
    enc = ''
    while seed != 0:
        enc = alphabet[seed % length] + enc
        seed //= length

    return enc if len(enc) == URL_LEN else enc + ('=' * (URL_LEN - len(enc)))

@url_app.route('/api/random', methods=['GET'])
@auth.login_required
def generate_random_url():
    """
    Generates a random short url of fixed size(7)
    If the length of the Base62 encoding of the Slug is
    shorter, pads it with additional characters.
    However unlikely in a short run, if there are no more available urls,
    the fixed length should simply be increased.
    """
    long_url = request.json.get('long_url')
    if long_url is None or not validate_url(long_url):
        return {'message': 'Invalid URL'}, 400
    user = g.user
    slug_count = SlugCount.increment()
    short_url = URL(id=_b62encode(slug_count.count), url=long_url, owner=user.email)
    db.session.add(short_url)
    db.session.commit()
    return {'short_url': short_url.id}, 201

@url_app.route('/api/custom', methods=['GET'])
@auth.login_required
@needs_premium
def generate_custom_url():
    """
    Generates a custom URL for premium users.
    Must be under 250 characters long
    """
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
    return {'short_url': short_url.id}, 201
    
@url_app.route('/<id>')
def url_redirect(id):
    """
    Redirects short url to the original.
    Returns 404 if short url does not exist
    """
    url = URL.query.get(id)
    if url is None:
        return {'message': 'URL not found'}, 404
    url.times_accessed += 1
    db.session.commit()
    return redirect(url.url), 302

def validate_url(url):
    """
    Checks for URL validity.
    http://www.google.com - valid
    http://google - valid
    goo.gl - invalid
    """
    regex = re.compile(r'^(http|https)://[^ "]+$')
    return re.match(regex, url) is not None

class SlugCount(db.Model):
    """
    A Slug counter class to handle URL duplications.
    It stores a single number in the database and increments
    it for every new URL requested. With then Base62 conversion,
    it prevents entry collisions that would have been caused by
    another approach, such as hashing and slicing.
    """
    __tablename__= 'slug'
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer)

    @staticmethod
    def get_count() -> int:
        """
        Returns the current slug count
        """
        return SlugCount.query.order_by(SlugCount.id).first().count

    @staticmethod
    def increment():
        """
        Increments the slug.
        """
        slug_count = SlugCount.query.order_by(SlugCount.id).first()
        slug_count.count += 1
        db.session.commit()
        return slug_count

class URL(db.Model):
    """
    URL model class, referencing 'urls' table in the database.

    """
    __tablename__ = 'urls'
    id = db.Column(db.String, primary_key=True)
    url = db.Column(db.String(249), nullable=False)
    owner = db.Column(db.String(256), db.ForeignKey('users.email'))
    times_accessed = db.Column(db.Integer, default=0)
    created = db.Column(db.DateTime, default=datetime.utcnow())

    @staticmethod
    def clear_expired() -> None:
        """
        Deletes all short URLs that have reached their lifespan
        of DAYS_VALID time
        """
        limit = datetime.utcnow() - timedelta(seconds=1)
        URL.query.filter(URL.created <= limit).delete()
        db.session.commit()
