#Brandon Calvario - Python file
#Steven Jerep - GitHub creation and pushing code to repo
#Gerardo Martinez, Millonoel Rodriguez, HTML file creation and design
#12.14.2024
#Abstract:
#Our project uses the Spotify API to create custom playlists. 
#Users can select a music genre from predefined options, log in to their Spotify account, 
#and generate a playlist featuring tracks from their chosen genre. The application follows 
#OAuth 2.0 for secure user authentication and utilizes Spotify's Web API for operations such 
#as user profile retrieval, playlist creation, and track management. 

#Requirements:
#- Flask
#- requests
#- Spotify Developer credentials (Client ID, Client Secret, Redirect URI)

import os
import requests
from flask import Flask, request, redirect, session, url_for, render_template

app = Flask(__name__)
app.secret_key = 'a_secure_random_secret_key'

# Configuration - set these as environment variables or directly assign
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "2b62e0bfa99741f3b0f1c6d4306e66e3")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "2862a740a13c48419f033cb97127843e")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:5000/callback")

# Spotify endpoints
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com/v1"

# The scope we need to create and modify playlists
SCOPE = "playlist-modify-public"
STATE = "some_random_state_string_for_csrf_protection"

# Define track URIs for each genre
GENRE_TRACKS = {
    "Corrido": [
        "spotify:track:1hHnCReCPe1FUkGLTeuCaC",  
        "spotify:track:7ifMxHITc3NIipJO4R5NGb",  
        "spotify:track:1cTsVlOLx5xNDCov5sky3v",
        "spotify:track:4r2TKO3fX4crUdSzsJOCrz",
        "spotify:track:5ZwLG5AaxZuRLoIBZE5KR4",
        "spotify:track:2MeEuwplwbbjZ7hxRI6viw", 
        "spotify:track:1cvuESXANPuTV27IFPRtPu",
        "spotify:track:5jEk9xozawNIRrChjPUvrC",
        "spotify:track:0wuyTWGojaWKWGFYTtqDyY",
        "spotify:track:0k65AuLt2U4m5ISi9IyLtb"
    ],
    "Boom Bap": [
        "spotify:track:3gTTDjDha02XJ4xuS2KF0e",  
        "spotify:track:3QbsrWxq3JyNov94VzbNdB",
        "spotify:track:21IiEw3SqSLLcMmPQt44zC",
        "spotify:track:1SJnJJmrqRyE8YSdhEtbPv",
        "spotify:track:7tx1TUJrT6qxXFXAELqbev",
        "spotify:track:4kVxStqN7DeoZje5aidAn3",
        "spotify:track:0XgpiStoxq1IJncYlPrvZ5",
        "spotify:track:4G3dZN9o3o2X4VKwt4CLts",
        "spotify:track:1OnukNKu7NWY4ouTc7w26u",
        "spotify:track:5WHsa2d0VhV4Dog4vhIYUH"
        
    ],
    "Rock": [
        "spotify:track:4nRyBgsqXEP2oPfzaMeZr7",
        "spotify:track:5rTIpPWeO0IL4HWlGWrz5G",
        "spotify:track:2H73LN4HzhQXjdviJ2DgMG",
        "spotify:track:1G391cbiT3v3Cywg8T7DM1",
        "spotify:track:6LjDGj9Hn5ERX3uhrT9LGV", 
        "spotify:track:3Jl5GohfNwozDmpzmQBLDI",
        "spotify:track:30HCB1FoE77IfGRyNv4eFq",
        "spotify:track:7kjsCbksOZotNNHOvKsJJh",
        "spotify:track:6QewNVIDKdSl8Y3ycuHIei",
        "spotify:track:0hpwRLIx6qm98jiXxU0XKo"
    ],
    "Rap": [
        "spotify:track:5sxRbu2Oi9lgmLO8taA3Rf",  
        "spotify:track:1p1b9LdLJ0REuFJX9mYtFX",  
        "spotify:track:33ZXjLCpiINn8eQIDYEPTD",
        "spotify:track:2xTft6GEZeTyWNpdX94rkf",
        "spotify:track:2HbKqm4o0w5wEeEFXm2sD4",
        "spotify:track:30oTS7bm0aH3p7lqjEIu8q", 
        "spotify:track:4fv1OzrStC17Mqck9LGldk",
        "spotify:track:6DPrhGVJ1WTZvM9fKptnGe",
        "spotify:track:6ScJMrlpiLfZUGtWp4QIVt",
        "spotify:track:5xEm63lXBhJKZgjRDMWH3H"
    ],
    "Indie Rock": [
        "spotify:track:6OiRh4kttAs1YWglvTcYkB",  
        "spotify:track:4Du0BRUJvKybzxcRplp7HF",  
        "spotify:track:2HbYLDA1SigY1ilC94ieVu",
        "spotify:track:2Lumsra3kuU61wXkEKzKaK",
        "spotify:track:5H9wA29ptgnn7mXAHKhUKc",
        "spotify:track:3rzYUfyzdZW96cHXnGn1xI", 
        "spotify:track:15gkmegUbWk1FcRPjX8gq1",
        "spotify:track:3FtYbEfBqAlGO46NUDQSAt",
        "spotify:track:3HlK8txWAdtKMrbsqX40pl",
        "spotify:track:4dyx5SzxPPaD8xQIid5Wjj"
    ],
    "EDM": [
        "spotify:track:49X0LAl6faAusYq02PRAY6",  
        "spotify:track:5erkBzi1uzfVzRotIEDevu",  
        "spotify:track:52RK8UVEDgUAgpecOpTQM3",
        "spotify:track:3dxDj8pDPlIHCIrUPXuCeG",
        "spotify:track:0vZCG0H9KhtU7K8MEUVAoV",
        "spotify:track:4gdjZS54vHNBk467zeAqkq", 
        "spotify:track:5tfqO6elC42ZwXfIN1aSDk",
        "spotify:track:6Xe9wT5xeZETPwtaP2ynUz",
        "spotify:track:58BVwReCtnJTLHRq0XOHCi",
        "spotify:track:4lhqb6JvbHId48OUJGwymk"
    ],
}
#Main project interface, html file gets called here
#Genre file also gets selected here.
@app.route('/')
def home():
    return render_template('projectInterface.html')

@app.route('/select_genre', methods=['POST'])
def select_genre():
    selected_genre = request.form.get('genre')
    if selected_genre not in GENRE_TRACKS:
        return "Invalid genre selection", 400

    # Store genre in session
    session['selected_genre'] = selected_genre

    # Redirect to login with Spotify
    return redirect(url_for('login'))
#Sends you to the main spotify login page to link accounts
@app.route('/login')
def login():
    # Redirect user to Spotify's authorization page
    auth_url = (
        f"{SPOTIFY_AUTH_URL}?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&scope={SCOPE}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&state={STATE}"
    )
    return redirect(auth_url)
#error handling -  uses spotifys callback, uses the authorization code for 
# access token
@app.route('/callback')
def callback():
    # Spotify redirects back to our application with a code and state
    code = request.args.get('code')
    state = request.args.get('state')

    if state != STATE:
        return "State mismatch. Potential CSRF attack.", 400

    # Exchange the code for an access token
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }

    r = requests.post(SPOTIFY_TOKEN_URL, data=token_data)
    if r.status_code != 200:
        return f"Error retrieving token: {r.text}", r.status_code

    tokens = r.json()
    access_token = tokens['access_token']
    refresh_token = tokens.get('refresh_token')

    # Store tokens in session for subsequent calls
    session['access_token'] = access_token
    session['refresh_token'] = refresh_token

    return redirect(url_for('create_playlist'))
#Main Playlist creation function - creates playlist for users account.
@app.route('/create_playlist')
def create_playlist():
    access_token = session.get('access_token')
    selected_genre = session.get('selected_genre')

    if not access_token:
        return redirect(url_for('login'))
    # error handling  - no playlist selected
    if not selected_genre or selected_genre not in GENRE_TRACKS:
        return "No genre selected or invalid genre.", 400

    # Get current user’s ID
    user_profile = requests.get(
        f"{SPOTIFY_API_BASE_URL}/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    #Error handling - error within users profile input
    if user_profile.status_code != 200:
        return f"Error retrieving user profile: {user_profile.text}", user_profile.status_code

    user_id = user_profile.json()['id']

    # Create a new playlist - what they playlist will be named on users end 
    #in spotify.
    playlist_data = {
        "name": f"My {selected_genre} Playlist",
        "description": f"A playlist of {selected_genre} tracks created via the Spotify Web API",
        "public": True
    }
    #Request of token - checks if user is valid
    create_playlist_resp = requests.post(
        f"{SPOTIFY_API_BASE_URL}/users/{user_id}/playlists",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        },
        json=playlist_data
    )
    #Error handling - invalid token
    if create_playlist_resp.status_code != 201:
        return f"Error creating playlist: {create_playlist_resp.text}", create_playlist_resp.status_code

    playlist_id = create_playlist_resp.json()['id']

    # Add tracks from the selected genre
    track_uris = GENRE_TRACKS[selected_genre]

    add_tracks_resp = requests.post(
        f"{SPOTIFY_API_BASE_URL}/playlists/{playlist_id}/tracks",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        },
        json={"uris": track_uris}
    )
    #Error handling - Adding songs failed, or invalid link
    if add_tracks_resp.status_code != 201:
        return f"Error adding tracks: {add_tracks_resp.text}", add_tracks_resp.status_code
    #Success
    return render_template('playlistCreated.html', playlist_id=playlist_id)