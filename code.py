#Brandon Calvario
#12/06/2024
#Main Python code to produce website, uses Flask, and Spotify's API to generate a playlist for user.

import os
from flask import Flask, request, redirect, session, url_for, render_template
import spotipy
from spotipy.oauth2 import SpotifyOAuth


app = Flask(__name__)
app.secret_key = os.urandom(24) 
app.config[''] = 'SpotifyPlaylistGenerator'


SPOTIFY_CLIENT_ID = '' 
SPOTIFY_CLIENT_SECRET = '' 
SPOTIFY_REDIRECT_URI = ''


scope = ''
sp_oauth = SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID,
                        client_secret=SPOTIFY_CLIENT_SECRET,
                        redirect_uri=SPOTIFY_REDIRECT_URI,
                        scope=scope)

#Login information
@app.route('/')
def home():
    auth_url = sp_oauth.get_authorize_url()
    return render_template('home.html', auth_url=auth_url)

#Authentication callback
@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['token_info'] = token_info
    return redirect(url_for('generate_playlist'))

#Generator ( Generates the playlist )
@app.route('/generate_playlist', methods=['GET', 'POST'])
def generate_playlist():
    token_info = session.get('token_info', None)
    if not token_info:
        return redirect('/')
    
    sp = spotipy.Spotify(auth=token_info['access_token'])

    if request.method == 'POST':
        playlist_name = request.form.get('playlist_name')
        genre = request.form.get('genre')

        recommendations = sp.recommendations(seed_genres=[genre], limit=20)
        track_uris = [track['uri'] for track in recommendations['tracks']]

        user_id = sp.current_user()['id']
        playlist = sp.user_playlist_create(user_id, playlist_name, public=True)
        sp.playlist_add_items(playlist['id'], track_uris)

        return render_template('playlist_success.html', playlist_name=playlist_name, playlist_url=playlist['external_urls']['spotify'])

    genres = sp.recommendation_genre_seeds()
    return render_template('generate_playlist.html', genres=genres['genres'])