#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import form
from forms import *
from flask_migrate import Migrate
import sys
import itertools
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database - done

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120), unique=True)
    genres = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120), unique=True)
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(300))
    shows = db.relationship('Show', backref='venue', lazy='dynamic')

    def __repr__(self):
      return f'''< venue 
                        id: {self.id},
                      name: {self.name},
                      city: {self.city},
                     state: {self.state} >'''

    # TODO: implement any missing fields, as a database migration using Flask-Migrate - done

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120), nullable=True, unique=True)
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(300))
    shows = db.relationship('Show', backref='artist', lazy='dynamic')

    def __repr__(self):
      return f'''< artist 
               id: {self.id},
             name: {self.name},
             city: {self.city},
            state: {self.state}>'''

    # TODO: implement any missing fields, as a database migration using Flask-Migrate - done

class Show(db.Model):
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artist.id'), nullable=False)
    start_time = db.Column(db.DateTime(), nullable=False)

    def __repr__(self):
      return f'''\n
            Show: {self.id} 
           Venue: {self.venue.name} 
          Artist: {self.artist.name}
      start_time: {self.start_time} '''


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration. - done

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
  # Stand out
  # Show Recent Listed Artists and Recently Listed Venues on the homepage, - done 
  # returning results for Artists and Venues sorting by newly created. - done
  # Limit to the 10 most recently listed items. - done

  recent_venues = Venue.query.order_by(Venue.id).limit(10).all()
  recent_artists = Artist.query.order_by(Artist.id).limit(10).all()

  return render_template('pages/home.html', recent_venues = recent_venues, recent_artists = recent_artists)


#  Venues
#  --------------------------------------------------------------------------#

@app.route('/venues')
def venues():
  # TODO: replace with real venues data. - done
  #       num_shows should be aggregated based on number of upcoming shows per venue. - done
  current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  venue_query = Venue.query.group_by(Venue.id, Venue.state, Venue.city).all()
  city_and_state = ''
  data = []
  for venue in venue_query:
      upcoming_shows = venue.shows.filter(Show.start_time > current_time).all()
      if city_and_state == venue.city + venue.state:
          data[len(data) - 1]["venues"].append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": len(upcoming_shows)
          })
      else:
          city_and_state = venue.city + venue.state
          data.append({
            "city": venue.city,
            "state": venue.state,
            "venues": [{
              "id": venue.id,
              "name": venue.name,
              "num_upcoming_shows": len(upcoming_shows)
            }]
          })

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive. - done
  # seach for Hop should return "The Musical Hop". - done
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee" - done
  
    # Stand out
  # TODO: Implement Search Venues by City and State - done
  # Searching by "San Francisco, CA" should return all venues in San Francisco, CA. - done
  
  search_term = request.form.get('search_term', '')
  q1 = Venue.query.all()
  venue_list = []

  for venue in q1:
    city_and_state = venue.city + ', ' + venue.state
    if city_and_state == search_term:
      venue_list.append(venue)  


  q2 = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  venue_list += q2
 
  response = {
    "count": len(venue_list),
    "data": []
  }
  for venue in venue_list:
    response["data"].append({
      "id": venue.id,
      "name": venue.name
    })
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id - done
  # TODO: replace with real venue data from the venues table, using venue_id - done 
  current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  venue_query = Venue.query.get(venue_id)
  past_shows_query = venue_query.shows.filter(Show.start_time < current_time).all()
  past_shows = []
  for show in past_shows_query:
      past_shows.append({
        "artist_id":show.artist_id,
        "artist_name":show.artist.name,
        "artist_image_link":show.artist.image_link,
        "start_time":str(show.start_time),
      })

  upcoming_shows_query = venue_query.shows.filter(Show.start_time > current_time).all()
  upcoming_shows = []
  for show in upcoming_shows_query:
      upcoming_shows.append({
        "artist_id":show.artist_id,
        "artist_name":show.artist.name,
        "artist_image_link":show.artist.image_link,
        "start_time":str(show.start_time),
      })


  data = {
    "id": venue_query.id,
    "name": venue_query.name,
    "genres": venue_query.genres,
    "address": venue_query.address,
    "city": venue_query.city,
    "state": venue_query.state,
    "phone": venue_query.phone,
    "website": venue_query.website,
    "facebook_link": venue_query.facebook_link,
    "seeking_talent": venue_query.seeking_talent,
    "seeking_description": venue_query.seeking_description,
    "image_link": venue_query.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    
  }
  
  # data1={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"], # missing in venue
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com", 
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.", # missing in venue
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #   "past_shows": [{
  #     "artist_id": 4,
  #     "artist_name": "Guns N Petals",
  #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }], # missing in venue
  #   "upcoming_shows": [], # missing in venue
  #   "past_shows_count": 1, # missing in venue
  #   "upcoming_shows_count": 0, # missing in venue
  # }
  # data2={
  #   "id": 2,
  #   "name": "The Dueling Pianos Bar",
  #   "genres": ["Classical", "R&B", "Hip-Hop"],
  #   "address": "335 Delancey Street",
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "914-003-1132",
  #   "website": "https://www.theduelingpianos.com",
  #   "facebook_link": "https://www.facebook.com/theduelingpianos",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 3,
  #   "name": "Park Square Live Music & Coffee",
  #   "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
  #   "address": "34 Whiskey Moore Ave",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "415-000-1234",
  #   "website": "https://www.parksquarelivemusicandcoffee.com",
  #   "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #   "past_shows": [{
  #     "artist_id": 5,
  #     "artist_name": "Matt Quevedo",
  #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [{
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 1,
  # }
  # old_data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead - done
  # TODO: modify data to be the data object returned from db insertion - done
  form = VenueForm(request.form, meta={'csrf': False})
  if form.validate():
    try:
      # venue = Venue(
      #   name = form.name.data,
      #   city = form.city.data,
      #   state = form.state.data,
      #   address = form.address.data,
      #   phone = form.phone.data,
      #   genres = form.genres.data,
      #   facebook_link = form.facebook_link.data 
      # )
      venue = Venue()
      form.populate_obj(venue)
      db.session.add(venue)
      db.session.commit()
      # on successful db insert, flash success
      flash('Venue: ' + request.form['name'] + ' was successfully listed!')
    except:
      # TODO: on unsuccessful db insert, flash an error instead. - done
      # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
      error = True
      db.session.rollback()
      flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')
      flash(f'{sys.exc_info()}')
    finally:
      db.session.close()
  else:
    messages = []
    for field, errors in form.errors.items():
      for error in errors:
        messages.append(field + ' : ' + error + '\n')
    flash('The Venue data is not valid. Please try again.')
    for message in messages:
      flash(message)
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>/delete', methods=['POST'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash(f'Venue: {venue.name} was successfully deleted!')
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    abort(500)
  else:
    return redirect(url_for('index'))

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage - done


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database - done
  artist_query = Artist.query.order_by(Artist.name).all()
  # data=[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }, {
  #   "id": 5,
  #   "name": "Matt Quevedo",
  # }, {
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  # }]
  return render_template('pages/artists.html', artists=artist_query)



@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive. - done
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band". - done
  # search for "band" should return "The Wild Sax Band". - done

  # Stand out
  # TODO: Implement Search Artists by City and State, and Search Venues by City and State. - done
  # Searching by "San Francisco, CA" should return all artists or venues in San Francisco, CA. - done

  search_term = request.form.get('search_term', '')
  q1 = Artist.query.all()
  artist_list = []

  for artist in q1:
    city_and_state = artist.city + ', ' + artist.state
    if city_and_state == search_term:
      artist_list.append(artist)

  q2 = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  artist_list += q2


  response = {
    "count": len(artist_list),
    "data": []
  }

  for artist in artist_list:
    response["data"].append({
      "id": artist.id,
      "name": artist.name
    })

  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artist/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id - done
  current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  artist_query = Artist.query.get(artist_id)
  past_shows_query = artist_query.shows.filter(Show.start_time < current_time).all()
  past_shows = []
  for show in past_shows_query:
      past_shows.append({
        "venue_id":show.venue_id,
        "venue_name":show.venue.name,
        "venue_image_link":show.venue.image_link,
        "start_time":str(show.start_time),
      })

  upcoming_shows_query = artist_query.shows.filter(Show.start_time > current_time).all()
  upcoming_shows = []
  for show in upcoming_shows_query:
      upcoming_shows.append({
        "venue_id":show.venue_id,
        "venue_name":show.venue.name,
        "venue_image_link":show.venue.image_link,
        "start_time":str(show.start_time),
      })

  data = {
    "id": artist_query.id,
    "name": artist_query.name,
    "genres": artist_query.genres,
    "address": artist_query.address,
    "city": artist_query.city,
    "state": artist_query.state,
    "phone": artist_query.phone,
    "website": artist_query.website,
    "facebook_link": artist_query.facebook_link,
    "seeking_venue": artist_query.seeking_venue,
    "seeking_description": artist_query.seeking_description,
    "image_link": artist_query.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    
  }

  # data1={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "past_shows": [{
  #     "venue_id": 1,
  #     "venue_name": "The Musical Hop",
  #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 5,
  #   "name": "Matt Quevedo",
  #   "genres": ["Jazz"],
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "300-400-5000",
  #   "facebook_link": "https://www.facebook.com/mattquevedo923251523",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "past_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  #   "genres": ["Jazz", "Classical"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "432-325-5432",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 3,
  # }
  # old_data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Artist record in the db, instead - done
  # TODO: modify data to be the data object returned from db insertion - done
  form = ArtistForm(request.form, meta={'csrf': False})
  if form.validate():
      try:
        # alternative way to populate fields from line 603:
        # artist = Artist(
        #   name = form.name.data,
        #   city = form.city.data,
        #   state = form.state.data,
        #   phone = form.phone.data,
        #   genres = form.genres.data,
        #   facebook_link = form.facebook_link.data 
        # )
        
        artist = Artist()
        form.populate_obj(artist)
        db.session.add(artist)
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist: ' + request.form['name'] + ' was successfully listed!')
      except:
        # TODO: on unsuccessful db insert, flash an error instead. - done
        # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        error = True
        db.session.rollback()
        flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
        flash(f'{sys.exc_info()}')
      finally:
        db.session.close()
  else:
    messages = []
    for field, errors in form.errors.items():
      for error in errors:
        messages.append(field + ' : ' + error + '\n')
    flash('The Artist data is not valid. Please try again.')
    for message in messages:
      flash(message)

  # on successful db insert, flash success - done
  # TODO: on unsuccessful db insert, flash an error instead. - done
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.') - done
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data. - done
  #       num_shows should be aggregated based on number of upcoming shows per venue. - done
  shows_query = Show.query.all()
  data = []
  for query in shows_query:
    data.append({
      "venue_id": query.venue_id,
      "venue_name": query.venue.name,
      "artist_id": query.artist_id,
      "artist_name": query.artist.name,
      "artist_image_link": query.artist.image_link,
      "start_time": str(query.start_time)
    })
  # old_data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form - done
  # TODO: insert form data as a new Show record in the db, instead - done
  form = ShowForm(request.form, meta={'csrf': False})
  if form.validate():
    try:
      show = Show(
        artist_id = form.artist_id.data,
        venue_id = form.venue_id.data,
        start_time = form.start_time.data
      )
      db.session.add(show)
      db.session.commit()
      # on successful db insert, flash success - done
      flash('Show of date: ' + request.form['start_time'] + ' was successfully listed!')
    except:
      # TODO: on unsuccessful db insert, flash an error instead. - done
      # e.g., flash('An error occurred. Show ' + data.name + ' could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
      error = True
      db.session.rollback()
      flash('An error occurred. Show of date: ' + str(form.start_time.data) + ' could not be listed.')
      flash(f'{sys.exc_info()}')
    finally:
      db.session.close()
  else:
    messages = []
    for field, errors in form.errors.items():
      for error in errors:
        messages.append(field + ' : ' + error + '\n')
    flash('The Show data is not valid. Please try again.')
    for message in messages:
      flash(message)
  return render_template('pages/home.html')


#  Update Venues & Artists
#  ----------------------------------------------------------------
@app.route('/artist/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)

  # Alternative loading of data from line 735:
  # form.name.data = artist.name
  # form.state.data = artist.state
  # form.city.data = artist.city
  # form.phone.data = artist.phone
  # form.genres.data = artist.genres
  # form.facebook_link.data = artist.facebook_link

  artist={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id> - done
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artist/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes - done
  form_artist = ArtistForm(request.form)
  db_artist = Artist.query.get(artist_id)
  error = False
  try:
    db_artist.name = form_artist.name.data
    db_artist.city = form_artist.city.data
    db_artist.state = form_artist.state.data
    db_artist.phone = form_artist.phone.data
    db_artist.genres = form_artist.genres.data
    db_artist.facebook_link = form_artist.facebook_link.data
    db.session.add(db_artist)
    db.session.commit()
  except ValueError as e:
    print(e)
    error = True
    db.session.rollback()
  finally:
    if not error:
      flash(f'Artist: {db_artist.name} was successfully updated!')
    else:
      flash('An error occurred. Artist could not be updated.')
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm(obj=venue)
  # Alterntive loading of data from line 792:
  # form.name.data = venue.name
  # form.city.data = venue.city
  # form.state.data = venue.state
  # form.address.data = venue.address
  # form.phone.data = venue.phone
  # form.genres.data = venue.genres
  # form.facebook_link.data = venue.facebook_link
  # form.image_link.data = venue.image_link
  # form.website.data = venue.website
  # form.seeking_talent.data = venue.seeking_talent
  # form.seeking_description.data = venue.seeking_description

  venue={
    "id": venue.id,
    "name": venue.name,
    # "genres": venue.genres,
    # "city": venue.city,
    # "state": venue.state,
    # "address": venue.address,
    # "phone": venue.phone,
    # "website": venue.website,
    # "facebook_link": venue.facebook_link,
    # "seeking_talent": venue.seeking_talent,
    # "seeking_description": venue.seeking_description,
    # "image_link": venue.image_link
  }
  # TODO: populate form with values from venue with ID <venue_id> - done
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing - done
  # venue record with ID <venue_id> using the new attributes - done
  db_venue = Venue.query.get(venue_id)
  form_venue = VenueForm(request.form)
  error = False
  try:

    db_venue.name = form_venue.name.data
    db_venue.city = form_venue.city.data
    db_venue.state = form_venue.state.data
    db_venue.phone = form_venue.phone.data
    db_venue.genres = form_venue.genres.data
    db_venue.facebook_link = form_venue.facebook_link.data
    db_venue.image_link = form_venue.image_link.data
    db_venue.website = form_venue.website.data
    db_venue.seeking_talent = form_venue.seeking_talent.data
    db_venue.seeking_description = form_venue.seeking_description.data

    db.session.add(db_venue)
    db.session.commit()
  except ValueError as e:
    print(e)
    error = True
    db.session.rollback()
  finally:
    if not error:
      flash(f'Venue: {db_venue.name} was successfully updated!')
    else:
      flash('An error occurred. Venue could not be updated.')
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))




#  Error Handlers
#  --------------------------------------------------------------- 
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
