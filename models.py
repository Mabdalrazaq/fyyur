
from sqlalchemy.dialects.postgresql import ARRAY
from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy import Column, String, Integer, Boolean ,ForeignKey

db=SQLAlchemy()

def setup_db(app):
    db.app=app
    db.init_app(app)
    return db

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres=db.Column(ARRAY(db.String),nullable=False)
    website=db.Column(db.String)
    seeking_talent=db.Column(db.Boolean)
    seeking_description=db.Column(db.String)
    shows=db.relationship('Show',backref='venue')

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres=db.Column(ARRAY(db.String),nullable=False)
    website=db.Column(db.String)
    seeking_venue=db.Column(db.Boolean)
    seeking_description=db.Column(db.String)
    shows=db.relationship('Show',backref='artist')
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Show(db.Model):
  __tablename__='Show'
  id=db.Column(db.Integer,primary_key=True)
  artist_id=db.Column(db.Integer, db.ForeignKey('Artist.id'),nullable=False)
  venue_id=db.Column(db.Integer,db.ForeignKey('Venue.id'),nullable=False)
  start_time=db.Column(db.String,nullable=False)
