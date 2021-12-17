from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)
app.config['SECRET_KEY'] = ""
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@db/shortener'


db = SQLAlchemy()
auth = HTTPBasicAuth()
