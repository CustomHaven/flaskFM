from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from app import app, db
from models import User, Song, Playlist, Item
from flask import render_template, request, url_for, redirect, flash, jsonify

#A form for inputing new songs via Dashboard
class SongForm(FlaskForm):
  title = StringField(label = "Song Title:", validators=[DataRequired()])
  artist = StringField(label = "Artist:", validators=[DataRequired()])
  submit = SubmitField("Add Song")

#A function we made to check if an item to be added is already in the playlist
def exists(item, playlist):
  """Return a boolean
    True if playlist contains item. False otherwise.
    """
  for i in playlist: #for each item in playlist
    if i.song_id == item.song_id: #check if the primary key is equal
       return True
  return False

#The home page of FlaskFM
#Lists all the users currently in the database
#renders the home.html template providing the list of current users
@app.route('/profiles')
def profiles():
    # app.logger.info('This is info output')
    current_users = User.query.all() #change here to a database query Q16
    return render_template('users.html', current_users = current_users)

#Displays profile pages for a user with the user_id primary key
#renders the profile.html template for a specific user, song library and 
#the user's playlist 
@app.route('/profile/<int:user_id>')
def profile(user_id):
   user = User.query.filter_by(id = user_id).first_or_404(description = "No such user found.")
   songs = Song.query.all()
   my_playlist = Playlist.query.get(user.playlist_id) #change here to a database query Q17   

   return render_template('profile.html', user = user, songs = songs, my_playlist = my_playlist)

#Adds new songs to a user's playlist from the song library
#redirects back to the profile that issued the addition
@app.route('/add_item/<int:user_id>/<int:song_id>/<int:playlist_id>')
def add_item(user_id, song_id, playlist_id):
   new_item = Item(song_id = song_id, playlist_id = playlist_id)
   user = User.query.filter_by(id = user_id).first_or_404(description = "No such user found.")
   my_playlist = Playlist.query.filter_by(id = user.playlist_id).first()

   if not exists(new_item, my_playlist.items):
      # Q18 create a new Item
      song = Song.query.get(song_id)

      i1 = Item(song_id = song.id, playlist_id = playlist_id)
      #using db session add the new item
      #increase the counter for the song associated with the new item Q19
      song.n = song.n + 1
      #commit the database changes here Q20
      db.session.add(i1)
      db.session.commit()
   return redirect(url_for('profile', user_id = user_id))

#Remove an item from a user's playlist
#Redirects back to the profile that issues the removal
@app.route('/remove_item/<int:user_id>/<int:item_id>')
def remove_item(user_id, item_id):
   print("user_id", user_id, "item_id", item_id)
   #from the Item model, fetch the item with primary key item_id to be deleted
   #using db.session delete the item Q21
   db.session.delete(Item.query.get(item_id))
   #commit the deletion Q21
   db.session.commit()
   return redirect(url_for('profile', user_id = user_id))
   
#Display the Dashboard page with a form for adding songs
#Renders the dashboard template
@app.route('/dashboard', methods=["GET", "POST"])
def dashboard():
  form = SongForm()
  if request.method == 'POST' and form.validate():

    # My extra condition if we have the song we add the n other wise we go to the else and create new song 
    song_found = Song.query.filter((Song.title == form.title.data) & (Song.artist == form.artist.data)).first()
    if song_found:
       song_found.n = song_found.n + 1
       db.session.commit()
    else:
       new_song = Song(artist = form.artist.data, title = form.title.data, n = 1)
       #create a new song here Q22
       db.session.add(new_song)
       #add it to the database Q23
       db.session.commit()
       #commit to the database Q23
  else:
       flash(form.errors)
  sorted_entries = [s for s in Song.query.order_by(Song.n.desc()).all()] 
  # sorted_entries = Song.query.order_by(Song.n)
  unpopular_songs = sorted_entries

  if request.is_json:
    button_clicked = request.json.get("button_clicked")
    if button_clicked:
      unpopular_songs = sorted_entries
    else:
      unpopular_songs = unpopular_songs[:3]
    
    # Generate HTML for unpopular songs
    unpopular_songs_html = ""
    for song in unpopular_songs:
        unpopular_songs_html += f"<li><p>{song} only {song.n} times added {' :)' if song.n > 1 else ' :('}</p></li>"

    return jsonify({"unpopular_songs_html": unpopular_songs_html})
  
  print(len(unpopular_songs)) # toggling works
  
  # print(unpopular_songs)
  songs = Song.query.all()
  return render_template('dashboard.html', songs = songs, unpopular_songs = unpopular_songs, form = form)