from flask import Flask, render_template, request, redirect, session, url_for
import spotipy
from spotipy.oauth2 import SpotifyOAuth


app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Spotify credentials
app.config['SESSION_COOKIE_NAME'] = 'spotify-login-session'
client_id = '162ac8a3eda14927ad6f7e8334dcdf5d'
client_secret = 'c347844247af40e4848a852005a02e73'
redirect_uri = 'http://localhost:5000/callback'

sp_oauth = SpotifyOAuth(client_id=client_id,
                        client_secret=client_secret,
                        redirect_uri=redirect_uri,
                        scope="user-modify-playback-state user-read-playback-state")

USERNAME = 'admin'
PASSWORD = 'password'


@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect('/login')
    return redirect('http://localhost:8501')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            return redirect('/')
        else:
            error = 'Invalid Credentials. Please try again.'
            return render_template('login.html', error=error)
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True, port=5001)
    from datetime import timedelta
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)
