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
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import datetime
from sqlalchemy import func

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
# uncomment it first run
db.create_all()

migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

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
    rating = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate - checked

    # added fields
    website = db.Column(db.String(200))
    genres = db.Column(db.ARRAY(db.String(150)))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(1000))

    # foreign relationship
    shows = db.relationship('Show', backref='venue')


  
class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    # change type genres to array of strings
    genres = db.Column(db.ARRAY(db.String(150)))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate - checked

    # added fields
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(1000))

    #foreign relationship
    shows = db.relationship('Show', backref='artist')
    

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration. - checked

class Show(db.Model):
  __tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.DateTime)
  
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)




#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(str(value))
  print("this is format_datetime")
  print(date)
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
  print("hello")
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.  ✅
  data = []
  test = db.session.query(func.array_agg(Venue.name), func.array_agg(Venue.id), Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
  print(test)

  # get unique cities
  cities = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state).all()
  for city in cities:
    venues = db.session.query(Venue).filter(Venue.city == city[0]).filter(Venue.state == city[1]).all()
    for venue in venues:
      venue.num_upcoming_shows = len(db.session.query(Show).filter(Show.venue_id == Venue.id).all())
      print(venue.num_upcoming_shows)
    data.append({
      'city': city[0].capitalize(),
      'state': city[1],
      'venues': venues
    })
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee" -- ✅

  # get search args
  lookup = request.form['search_term']
  r = db.session.query(Venue).filter(Venue.name.contains(lookup)).all()

  # assign upcoming shows count
  for i in r:
    upcoming_shows = db.session.query(Show).filter(Show.venue_id == i.id, Show.start_time >= datetime.today()).all()
    i.num_upcoming_shows = len(upcoming_shows)
    print(i.num_upcoming_shows)

  response =  {
    "count": len(r),
    "data": r
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  print(request.args)
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id -- ✅
  # Get past and upcoming events
  data = db.session.query(Venue).filter(Venue.id == venue_id).first()
  print(data.genres)
  past_shows = db.session.query(Show).filter(Show.venue_id == data.id, Show.start_time < datetime.today()).all()
  upcoming_shows = db.session.query(Show).filter(Show.venue_id == data.id, Show.start_time >= datetime.today()).all()

  for i in past_shows:
    i.start_time = i.start_time.strftime("%Y-%m-%dT%H:%M:%S")
  for i in upcoming_shows:
    i.start_time = i.start_time.strftime("%Y-%m-%dT%H:%M:%S")

  data.past_shows = past_shows
  data.upcoming_shows = upcoming_shows
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
  # TODO: modify data to be the data object returned from db insertion - ✅
  # check if venue exist.
  # seeking_talent = lambda x: True if x == "yes" else False
  submittedForm = VenueForm(request.form)

  if db.session.query(Venue).filter(Venue.name == submittedForm.name.data).first():
    flash('Venue ' + submittedForm.name.data + ' already exist.')
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)

  # form submission
  error = False
  try:
    seeking_talent = lambda x: True if x == "yes" else False
    venue = Venue(
      name = submittedForm.name.data,
      city = submittedForm.city.data.lower(),
      state = submittedForm.state.data,
      address = submittedForm.address.data,
      phone = submittedForm.phone.data,
      genres = submittedForm.genres.data,
      facebook_link = submittedForm.facebook_link.data,
      seeking_talent = (lambda x: True if x == "Yes" else False)(submittedForm.seeking_talent.data),
      seeking_description = submittedForm.seeking_description.data
      )
    db.session.add(venue)
    db.session.commit()
    print("success")
  except:
    error = True
    db.session.rollback()
    flash('error occured')
  finally:
    db.session.close()
  if not error:
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return redirect('/')

  # TODO: on unsuccessful db insert, flash an error instead. -- ✅
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database -- ✅

  data = db.session.query(Artist).all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  # get data
  data = db.session.query(Artist).filter(Artist.id == artist_id).first()
  past_shows = db.session.query(Show).filter(Show.artist_id == data.id, Show.start_time < datetime.today()).all()
  upcoming_shows = db.session.query(Show).filter(Show.artist_id == data.id, Show.start_time >= datetime.today()).all()
  
  print(data.genres)
  for i in past_shows:
    i.start_time = i.start_time.strftime("%Y-%m-%dT%H:%M:%S")
  for i in upcoming_shows:
    i.start_time = i.start_time.strftime("%Y-%m-%dT%H:%M:%S")

  data.past_shows = past_shows
  data.upcoming_shows = upcoming_shows
  # get upcoming and past shows
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # populate form -- ✅
  form = ArtistForm()
  artist = db.session.query(Artist).filter(Artist.id == artist_id).first()
  form.name.process_data(artist.name)
  form.city.process_data(artist.city)
  form.phone.process_data(artist.phone)
  form.state.process_data(artist.state)
  form.genres.process_data(artist.genres)
  form.facebook_link.process_data(artist.facebook_link)
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes -- ✅
  submittedForm = ArtistForm(request.form)

  a = db.session.query(Artist).filter(Artist.id == artist_id).first()
  if not a:
    flash('Artist ' + submittedForm.name.data + ' does not exist.')
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)

  # form submission
  error = False
  try:
    a.name = submittedForm.name.data,
    a.city = submittedForm.city.data.lower(),
    a.state = submittedForm.state.data,
    a.phone = submittedForm.phone.data,
    a.genres = submittedForm.genres.data,
    a.facebook_link = submittedForm.facebook_link.data,

    db.session.commit()
    print("artist successfully updated")
  except:
    error = True
    db.session.rollback()
    flash('error occured')
  finally:
    db.session.close()
  if not error:
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully edited!')
    return redirect('/')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # populate form -- ✅
  form = VenueForm()
  venue = db.session.query(Venue).filter(Venue.id == venue_id).first()
  form.name.process_data(venue.name)
  form.address.process_data(venue.address)
  form.city.process_data(venue.city)
  form.phone.process_data(venue.phone)
  form.state.process_data(venue.state)
  form.genres.process_data(venue.genres)
  form.facebook_link.process_data(venue.facebook_link)

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes -- ✅
  submittedForm = VenueForm(request.form)

  v = db.session.query(Venue).filter(Venue.id == venue_id).first()
  if not v:
    flash('Venue ' + submittedForm.name.data + ' does not exist.')
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)

  # form submission
  error = False
  try:
    v.name = submittedForm.name.data,
    v.city = submittedForm.city.data.lower(),
    v.state = submittedForm.state.data,
    v.address = submittedForm.address.data,
    v.phone = submittedForm.phone.data,
    v.genres = submittedForm.genres.data,
    v.facebook_link = submittedForm.facebook_link.data,

    db.session.commit()
    print("successfully updated")
  except:
    error = True
    db.session.rollback()
    flash('error occured')
  finally:
    db.session.close()
  if not error:
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully edited!')
    return redirect('/')

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  # done - ✅
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion - ✅

  submittedForm = ArtistForm(request.form)
  if db.session.query(Artist).filter(Artist.name == submittedForm.name.data).first():
    flash('Artist ' +submittedForm.name.data + ' already exist.')
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)

  # form submission
  error = False
  try:
    print(submittedForm.genres.data)
    artist = Artist(
      name = submittedForm.name.data,
      city = submittedForm.city.data.lower(),
      state = submittedForm.state.data,
      phone = submittedForm.phone.data,
      genres = submittedForm.genres.data,
      facebook_link = submittedForm.facebook_link.data
      )

    db.session.add(artist)
    db.session.commit()
    print("success")
  except:
    error = True
    db.session.rollback()
    flash('error occured')
  finally:
    db.session.close()
  if not error:
    # on successful db insert, flash success

    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return redirect('/')

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.') - ✅
  # return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue. -- ✅
  data = db.session.query(Show).all()
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead -- ✅
  submittedForm = ShowForm(request.form)
  # check if user & venue exist.
  if not db.session.query(Artist).filter(Artist.id == submittedForm.artist_id.data).first():
    flash('Artist ID' + submittedForm.artist_id.data + ' does not exists.')
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)
  elif not db.session.query(Venue).filter(Venue.id == submittedForm.venue_id.data).first():
    flash('Venue ID ' + submittedForm.venue_id.data + ' does not exists.')
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)

  if db.session.query(Show).filter(Show.artist_id == submittedForm.artist_id.data).first() and db.session.query(Show).filter(Show.venue_id == submittedForm.venue_id.data).first() and db.session.query(Show).filter(Show.start_time == submittedForm.start_time.data).first():
    flash('Artist' + submittedForm.artist_id.data +
          ' event already exist on that time.')
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)

  # form submission
  error = False
  try:
    show = Show(
      artist_id = submittedForm.artist_id.data,
      venue_id = submittedForm.venue_id.data,
      start_time = submittedForm.start_time.data
      )
    print(show.start_time)
    db.session.add(show)
    db.session.commit()
    print("success")
  except:
    error = True
    db.session.rollback()
    flash('error occured')
  finally:
    db.session.close()
  if not error:
    # on successful db insert, flash success

    flash('Event was successfully listed!')
    return redirect('/')

  # on successful db insert, flash success
  flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  # return render_template('pages/home.html')

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
    app.run(port=5440)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
