import streamlit as st
import requests
import base64
import random
import pandas as pd

# ---------------------------- CONFIG ----------------------------
CLIENT_ID = "c6075ed4579a4c3a8317649086ff8c00"
CLIENT_SECRET = "97de82bd86eb40959eb2c2950500dde4"

# ------------------------ AUTH FUNCTION -------------------------
def get_token(client_id, client_secret):
    auth_string = f"{client_id}:{client_secret}"
    auth_base64 = base64.b64encode(auth_string.encode()).decode()

    headers = {
        "Authorization": f"Basic {auth_base64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "client_credentials"
    }

    response = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

# ------------------------ SEARCH FUNCTION ------------------------
def search_tracks(query, token, limit=10):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "q": query,
        "type": "track",
        "limit": limit
    }
    response = requests.get("https://api.spotify.com/v1/search", headers=headers, params=params)
    response.raise_for_status()
    return response.json()["tracks"]["items"]

# ------------------------ MOOD MAPPING ------------------------
def map_text_to_mood(text):
    text = text.lower()
    if any(word in text for word in ["happy", "joy", "excited"]):
        return "Happy"
    elif any(word in text for word in ["sad", "down", "depressed"]):
        return "Sad"
    elif any(word in text for word in ["energetic", "pumped", "active"]):
        return "Energetic"
    elif any(word in text for word in ["calm", "relaxed", "peaceful"]):
        return "Calm"
    elif any(word in text for word in ["love", "romantic", "crush"]):
        return "Romantic"
    else:
        return None

# ---------------------------- CUSTOM CSS ----------------------------
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ---------------------------- STREAMLIT UI ----------------------------
st.set_page_config(
    page_title="Spotify Mood-Based Recommender",
    layout="wide",
    page_icon="🎧",
    initial_sidebar_state="expanded"
)

# Inject custom CSS
local_css("style.css")

# Main header with gradient
st.markdown("""
<div class="header">
    <h1>🎵 Spotify Mood-Based Recommender</h1>
    <p class="subheader">Discover music that matches your current mood</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for additional features
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <h2>Your Music Journey</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Mood examples
    with st.expander("💡 Mood Examples"):
        st.markdown("""
        - **Happy**: "I'm feeling joyful today!"
        - **Sad**: "I'm feeling a bit down"
        - **Energetic**: "I need something pumped up"
        - **Calm**: "I want to relax"
        - **Romantic**: "I'm feeling love in the air"
        """)
    
    # About section
    with st.expander("ℹ️ About"):
        st.markdown("""
        This app recommends Spotify tracks based on your current mood.
        It uses the Spotify API to find songs that match your emotional state.
        """)

# Main content
col1, col2 = st.columns([3, 1])

with col1:
    # Mood input with better styling
    with st.container():
        st.markdown("### 🌈 How are you feeling today?")
        user_input = st.text_input(
            "Describe your mood (e.g., 'I'm feeling relaxed' or 'I need energy')",
            label_visibility="collapsed",
            key="mood_input"
        )

    # Genre filter with icons
    with st.container():
        st.markdown("### 🎶 Filter by genre (optional)")
        genre = st.selectbox(
            "Select a genre",
            ["", "Pop", "Rock", "Hip-Hop", "Classical", "Bollywood"],
            label_visibility="collapsed"
        )

# Favorite and history tracking
if "favorites" not in st.session_state:
    st.session_state.favorites = []
if "history" not in st.session_state:
    st.session_state.history = []

if user_input:
    mood = map_text_to_mood(user_input)
    if not mood:
        st.warning("Could not detect mood from your input. Try using words like happy, sad, calm, etc.")
    else:
        query = f"{mood} {genre}" if genre else mood
        try:
            token = get_token(CLIENT_ID, CLIENT_SECRET)
            tracks = search_tracks(query, token)

            # History logging
            st.session_state.history.extend(tracks)

            # Display all tracks with enhanced cards
            st.markdown(f"## 🎧 Recommended songs for: {query}")
            
            for track in tracks:
                with st.container():
                    st.markdown("---")
                    cols = st.columns([1, 4])
                    with cols[0]:
                        st.image(track["album"]["images"][0]["url"], width=150)
                    with cols[1]:
                        st.markdown(f"### {track['name']}")
                        st.markdown(f"**Artist:** {track['artists'][0]['name']}")
                        st.markdown(f"**Album:** {track['album']['name']}")
                        
                        # Popularity meter
                        popularity = track["popularity"]
                        st.markdown(f"""
                        <div class="popularity-container">
                            <span class="popularity-label">Popularity:</span>
                            <div class="popularity-bar" style="width: {popularity}%"></div>
                            <span class="popularity-value">{popularity}%</span>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Spotify link button
                        st.markdown(f"""
                        <a href="{track['external_urls']['spotify']}" target="_blank" class="spotify-button">
                            🎵 Play on Spotify
                        </a>
                        """, unsafe_allow_html=True)
                        
                        # Audio preview
                        if track.get("preview_url"):
                            st.audio(track["preview_url"], format="audio/mp3")
                        
                        # Save button
                        if st.button(f"💖 Save {track['name']}", key=track["id"]):
                            st.session_state.favorites.append({
                                "track_name": track["name"],
                                "artist": track["artists"][0]["name"],
                                "spotify_url": track["external_urls"]["spotify"],
                                "album": track["album"]["name"],
                                "mood": mood,
                                "genre": genre if genre else "Not specified"
                            })
                            st.success(f"Saved {track['name']} to favorites!")

            # Surprise Me feature with better styling
            st.markdown("---")
            if st.button("🎲 Surprise Me!", key="surprise_me"):
                random_track = random.choice(tracks)
                st.balloons()
                with st.container():
                    st.markdown("## 🎁 Your Surprise Track!")
                    cols = st.columns([1, 3])
                    with cols[0]:
                        st.image(random_track["album"]["images"][0]["url"], width=200)
                    with cols[1]:
                        st.markdown(f"### {random_track['name']}")
                        st.markdown(f"**Artist:** {random_track['artists'][0]['name']}")
                        st.markdown(f"**Album:** {random_track['album']['name']}")
                        st.markdown(f"""
                        <a href="{random_track['external_urls']['spotify']}" target="_blank" class="spotify-button">
                            🎵 Play on Spotify
                        </a>
                        """, unsafe_allow_html=True)
                        if random_track.get("preview_url"):
                            st.audio(random_track["preview_url"], format="audio/mp3")

        except Exception as e:
            st.error(f"Error: {e}")

# Favorites section with download
if st.session_state.favorites:
    st.markdown("---")
    st.markdown("## 💖 Your Favorite Tracks")
    df_fav = pd.DataFrame(st.session_state.favorites)
    
    # Display favorites as a table with Spotify links
    for _, row in df_fav.iterrows():
        with st.container():
            cols = st.columns([4, 1])
            with cols[0]:
                st.markdown(f"### {row['track_name']}")
                st.markdown(f"**Artist:** {row['artist']} | **Album:** {row['album']}")
                st.markdown(f"**Mood:** {row['mood']} | **Genre:** {row['genre']}")
            with cols[1]:
                st.markdown(f"""
                <a href="{row['spotify_url']}" target="_blank" class="spotify-button-small">
                    🎵 Play
                </a>
                """, unsafe_allow_html=True)
            st.markdown("---")
    
    # Download button
    csv = df_fav.to_csv(index=False)
    st.download_button(
        "📥 Download Favorites as CSV",
        csv,
        "spotify_favorites.csv",
        "text/csv",
        key='download-csv'
    )

# History section with better display
if st.session_state.history:
    with st.expander("⏳ Recently Played Tracks", expanded=False):
        for track in st.session_state.history[-10:][::-1]:  # Show most recent first
            st.markdown(f"""
            <div class="history-item">
                <span class="track-name">{track['name']}</span>
                <span class="track-artist">by {track['artists'][0]['name']}</span>
                <a href="{track['external_urls']['spotify']}" target="_blank" class="history-spotify-link">🎵</a>
            </div>
            """, unsafe_allow_html=True)

# Add some custom JavaScript for animations
st.markdown("""
<script>
// Simple animation for buttons
document.addEventListener('DOMContentLoaded', function() {
    const buttons = document.querySelectorAll('.stButton button');
    buttons.forEach(button => {
        button.addEventListener('mouseover', function() {
            this.style.transform = 'scale(1.02)';
            this.style.transition = 'transform 0.2s';
        });
        button.addEventListener('mouseout', function() {
            this.style.transform = 'scale(1)';
        });
    });
});
</script>
""", unsafe_allow_html=True)