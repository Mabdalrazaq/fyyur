#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
Flask,
render_template,
request,
Response,
flash,
redirect,
url_for,
jsonify,
abort)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from sqlalchemy import func
from datetime import datetime
import json
import sys
from models import Venue,Artist,Show, setup_db
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db=setup_db(app)
migrate=Migrate(app,db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#



# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  # cities=Venue.query.with_entities(Venue.city, func.count(Venue.city)).group_by(Venue.city).all()
  cities=[]
  for venue in Venue.query.distinct(Venue.city):
    cities.append(venue.city)
  data=[]
  for city in cities:
    print(city)
    obj={
      "city":city,
      "state":"",
      "venues":[]
    }
    for venue in Venue.query.all():
      if venue.city==city:
        obj["state"]=venue.state
        obj["venues"].append({
          "id":venue.id,
          "name":venue.name,
          "num_upcoming_shows":len(venue.shows)
        })
    data.append(obj)

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term=request.form.get('search_term','')
  venues=Venue.query.filter(Venue.name.ilike('%'+search_term+'%')).all()
  response={
    "count":len(venues),
    "data":[]
  }
  for venue in venues:
    obj={
      "id":venue.id,
      "name":venue.name,
      "num_upcoming_shows":len(venue.shows)
    }
    response["data"].append(obj)

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue=Venue.query.get(venue_id)
  # pastShows=list(filter(lambda s: s.start_time < datetime.datetime.now(),venue.shows))
  past_shows=[]
  upcoming_shows=[]
  for show in venue.shows:
    obj={
      "artist_id": show.artist_id,
      "artist_name": Artist.query.get(show.artist_id).name,
      "artist_image_link": Artist.query.get(show.artist_id).image_link,
      "start_time": show.start_time
    }
    if (show.start_time<datetime.now().strftime("%Y-%m-%d %H:%M:%S")):
      past_shows.append(obj)
    else:
      upcoming_shows.append(obj)

  data={
    "id":venue.id,
    "name":venue.name,
    "genres": venue.genres,
    "address":venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows":upcoming_shows,
    "past_shows_count":len(past_shows),
    "upcoming_shows_count":len(upcoming_shows)
  }
  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try: 
    form=request.form
    seeking_talent=form.get("seeking_talent",False)
    if(seeking_talent=="y"):
      seeking_talent=True
    venue=Venue(name=form["name"],
    address=form["address"],
    phone=form["phone"],
    city=form["city"],
    state=form["state"],
    genres=form.getlist("genres"),
    facebook_link=form["facebook_link"],
    website=form["website"],
    image_link=form["image_link"],
    seeking_description=form["seeking_description"],
    seeking_talent=seeking_talent)

    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + venue.name + ' was successfully listed!')
    db.session.close()
    return render_template('pages/home.html')
  except:
    db.session.rollback()
    db.session.close()
    print(sys.exc_info())
    flash('An error occurred. Venue ' + form["name"] + ' could not be listed.')
    abort(400)

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    Venue.query.get(venue_id).delete()
    db.session.commit()
    db.session.close()
    return jsonify({"success":True})
  except:
    db.session.rollback()
    db.session.close()
    print(sys.exc_info())
    abort(400)
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data=[]
  for artist in Artist.query.all():
    data.append({
      "id":artist.id,
      "name":artist.name
    })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term=request.form.get('search_term','')
  artists=Artist.query.filter(Artist.name.ilike('%'+search_term+'%')).all()
  response={
    "count":len(artists),
    "data":[]
  }
  for artist in artists:
    obj={
      "id":artist.id,
      "name":artist.name,
      "num_upcoming_shows":len(artist.shows)
    }
    response["data"].append(obj)
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  artist=Artist.query.get(artist_id)
  # pastShows=list(filter(lambda s: s.start_time < datetime.datetime.now(),venue.shows))
  past_shows=[]
  upcoming_shows=[]
  for show in artist.shows:
    obj={
      "venue_id": show.venue_id,
      "venue_name": Venue.query.get(show.venue_id).name,
      "venue_image_link": Venue.query.get(show.venue_id).image_link,
      "start_time": show.start_time
    }
    if (show.start_time<datetime.now().strftime("%Y-%m-%d %H:%M:%S")):
      past_shows.append(obj)
    else:
      upcoming_shows.append(obj)

  data={
    "id":artist.id,
    "name":artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows":upcoming_shows,
    "past_shows_count":len(past_shows),
    "upcoming_shows_count":len(upcoming_shows)
  }
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist=Artist.query.get(artist_id)
  artistData={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.description,
    "image_link": artist.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artistData)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    form=request.form
    artist=Artist.query.get(artist_id)
    artist.name=form["name"]
    artist.genres=form["genres"]
    artist.city=form["city"]
    artist.state=form["state"]
    artist.phone=form["phone"]
    artist.website=form["website"]
    artist.facebook_link=form["facebook_link"]
    artist.seeking_venue=form["seeking_venue"]
    artist.seeking_description=form["seeking_description"]
    artist.image_link=form["image_link"]
    db.session.commit()
    db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))
  except:
    db.session.rollback()
    db.session.close()
    print(sys.exc_info())
    abort(400)

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue=Venue.query.get(venue_id)
  venueData={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.description,
    "image_link": venue.image_link
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venueData)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    form=request.form
    venue= Venue.query.get(venue_id)
    venue.name=form["name"]
    venue.genres=form["genres"]
    venue.address=form["address"]
    venue.city=form["city"]
    venue.state=form["state"]
    venue.phone=form["phone"]
    venue.website=form["website"]
    venue.facebook_link=form["facebook_link"]
    venue.seeking_talent=form["seeking_talent"]
    venue.seeking_description=form["seeking_description"]
    venue.image_link=form["image_link"]
    db.session.commit()
    db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))
  except:
    db.session.rollback()
    db.session.close()
    print(sys.exc_info())
    abort(400)

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try: 
    form=request.form
    seeking_venue=False
    if form.get("seeking_venue","")=="y":
      seeking_venue=True
    print(json.dumps(form,indent=4))
    artist=Artist(name=form["name"],
    phone=form["phone"],
    city=form["city"],
    state=form["state"],
    genres=form.getlist("genres"),
    facebook_link=form["facebook_link"],
    seeking_venue=seeking_venue,
    seeking_description=form["seeking_description"],
    website=form["website"],
    image_link=form["image_link"])
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + artist.name + ' was successfully listed!')
    db.session.close()
    return render_template('pages/home.html')
  except:
    print(sys.exc_info())
    db.session.rollback()
    db.session.close()
    flash('An error occurred. Venue ' + form["name"] + ' could not be listed.')
    abort(400)


  # on successful db insert, flash success
  # flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  # return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows=Show.query.all()
  data=[]
  for show in shows:
    data.append({
      "venue_id":show.venue_id,
      "venue_name":Venue.query.get(show.venue_id).name,
      "artist_id":show.artist_id,
      "artist_name":Artist.query.get(show.artist_id).name,
      "artist_image_link":Artist.query.get(show.artist_id).image_link,
      "start_time":show.start_time
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try: 
    form=request.form
    show=Show(venue_id=form["venue_id"],artist_id=form["artist_id"],start_time=form["start_time"])
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
    db.session.close()
    return render_template('pages/home.html')
  except:
    db.session.rollback()
    db.session.close()
    print(sys.exc_info())
    flash('An error occurred. Show could not be listed.')
    abort(400)

  # on successful db insert, flash success
  # flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
