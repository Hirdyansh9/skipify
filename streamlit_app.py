import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
import time

# Spotify credentials
client_id = '162ac8a3eda14927ad6f7e8334dcdf5d'
client_secret = 'c347844247af40e4848a852005a02e73'
redirect_uri = 'http://localhost:5000/callback'  # Spotify OAuth setup
sp_oauth = SpotifyOAuth(client_id=client_id,
                        client_secret=client_secret,
                        redirect_uri=redirect_uri,
                        scope="user-modify-playback-state user-read-playback-state")

# Function to fetch token info


def fetch_token_info():
    response = requests.get('http://localhost:5000/get_token')
    if response.status_code == 200:
        return response.json().get('token_info')
    return None

# Fetch access token


def get_token():
    token_info = sp_oauth.get_access_token(as_dict=True)
    return token_info


# Initialize session state
if 'trims' not in st.session_state:
    st.session_state.trims = []
if 'token_info' not in st.session_state:
    st.session_state.token_info = get_token()

sp = spotipy.Spotify(auth=st.session_state.token_info['access_token'])

st.title("Skipify")

# Logout button
if st.button("Logout"):
    st.session_state.clear()
    st.success("You have been logged out.")
    st.stop()

# Input for the Spotify track link
track_link = st.text_input("Enter Spotify Track Link:")

if track_link:
    track_id = track_link.split("/")[-1].split("?")[0]
    track_info = sp.track(track_id)
    track_duration_ms = track_info['duration_ms']

    st.write(f"Track: {track_info['name']} by {track_info['artists'][0]['name']}"
             )
    st.write(f"Duration: {track_duration_ms // 1000} seconds")

    if 'trims' not in st.session_state:
        st.session_state.trims = []

    def seconds_to_mmss(seconds):
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def mmss_to_seconds(mmss):
        minutes, seconds = map(int, mmss.split(':'))
        return minutes * 60 + seconds

    start_time_sec = st.slider(
        "Start Time (seconds)", 0, track_duration_ms // 1000, 0)
    end_time_sec = st.slider(
        "End Time (seconds)", 0, track_duration_ms // 1000, track_duration_ms // 1000)

    st.write(f"Trim Range: {seconds_to_mmss(start_time_sec)} - {seconds_to_mmss(end_time_sec)}"
             )

    if st.button("Add Trim"):
        if start_time_sec < end_time_sec:
            play_trim = st.radio("Play or Skip this trim?", ('Play', 'Skip'))
            st.session_state.trims.append({
                'song_uri': track_info['uri'],
                'start_time': start_time_sec,
                'end_time': end_time_sec,
                'action': play_trim
            })
            st.success(f"Trim range added: {seconds_to_mmss(start_time_sec)} - {seconds_to_mmss(end_time_sec)} ({play_trim})"
                       )
        else:
            st.error("Start time must be less than end time.")

    if st.session_state.trims:
        st.write("### Saved Trims")

        for idx, trim in enumerate(st.session_state.trims):
            st.write(f"**Trim {idx + 1}:** {seconds_to_mmss(trim['start_time'])} - {seconds_to_mmss(trim['end_time'])} ({trim['action']})"
                     )

        if st.button("Listen"):
            for trim in st.session_state.trims:
                start_ms = trim['start_time'] * 1000
                end_ms = trim['end_time'] * 1000
                if trim['action'] == 'Play':
                    sp.start_playback(uris=[track_info['uri']])
                    sp.seek_track(position_ms=start_ms)

                    while True:
                        playback = sp.current_playback()
                        current_position = playback['progress_ms']

                        if current_position >= end_ms or not playback['is_playing']:
                            sp.pause_playback()
                            break
                        time.sleep(0.5)
                else:
                    sp.seek_track(position_ms=end_ms)

            last_trim_end = st.session_state.trims[-1]['end_time'] * 1000
            if last_trim_end < track_duration_ms:
                remaining_time_ms = track_duration_ms - last_trim_end
                if remaining_time_ms > 0:
                    sp.next_track()

                    while True:
                        playback = sp.current_playback()
                        current_position = playback['progress_ms']

                        if current_position >= track_duration_ms or not playback['is_playing']:
                            sp.pause_playback()
                            break
                        time.sleep(0.5)

    if st.button("Clear All Trims"):
        st.session_state.trims = []
        st.success("All trims cleared.")
