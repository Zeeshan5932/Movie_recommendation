import streamlit as st
import pickle
import pandas as pd
import requests
from functools import lru_cache

FALLBACK_POSTER_URL = "https://via.placeholder.com/500x750.png?text=No+Poster"

# Page config
st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
    <style>
        .movie-card {
            background-color: #1f1f2e;
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s;
        }
        .movie-card:hover {
            transform: scale(1.05);
        }
        .movie-title {
            color: #fff;
            font-weight: bold;
            margin-top: 10px;
            font-size: 14px;
        }
        h1 {
            color: #ff6b6b;
            text-align: center;
            margin-bottom: 30px;
        }
    </style>
""", unsafe_allow_html=True)

@lru_cache(maxsize=1000)
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
        data = requests.get(url, timeout=8)
        data = data.json()
        if data.get('poster_path'):
            return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
        else:
            return None
    except Exception:
        return None


def recommend(movie):
    try:
        index = movies[movies['title'] == movie].index[0]
        distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
        recommendations = []
        
        for i in distances[1:6]:
            movie_row = movies.iloc[i[0]]
            movies_id = movie_row['id']
            poster = fetch_poster(int(movies_id))
            recommendations.append({
                "title": movie_row['title'],
                "poster": poster if poster else FALLBACK_POSTER_URL,
                "has_real_poster": bool(poster),
            })
        
        return recommendations
    except Exception as e:
        st.error(f"Error in recommendation: {str(e)}")
        return []
   


# Load data
@st.cache_resource
def load_data():
    movies_data = pd.DataFrame(pickle.load(open('movies_dict.pkl', 'rb')))
    similarity_data = pickle.load(open('similarity.pkl', 'rb'))
    return movies_data, similarity_data

movies, similarity = load_data()

# Title with emoji
st.markdown("<h1>🎬 Movie Recommender System</h1>", unsafe_allow_html=True)

# Search section
col1, col2 = st.columns([3, 1])
with col1:
    movie_list = list(movies['title'].values)
    selected_movie = st.selectbox(
        "🔍 Select a movie you like:",
        movie_list,
        label_visibility="collapsed"
    )

with col2:
    search_button = st.button('🔎 Get Recommendations', use_container_width=True)

# Show recommendations
if search_button:
    with st.spinner('⏳ Finding similar movies...'):
        recommendations = recommend(selected_movie)

    if len(recommendations) == 0:
        st.error("❌ Could not find recommendations. Please try another movie.")
    else:
        real_posters_count = sum(1 for item in recommendations if item["has_real_poster"])
        if real_posters_count < len(recommendations):
            st.info("Some posters could not be loaded from TMDB, so fallback thumbnails are shown.")

        st.success(f"✅ Found {len(recommendations)} recommendations for '{selected_movie}'")
        st.markdown("---")
        
        # Display recommendations in a grid
        cols = st.columns(5)
        for idx, item in enumerate(recommendations):
            with cols[idx]:
                st.markdown(f'<div class="movie-card">', unsafe_allow_html=True)
                st.image(item["poster"], use_container_width=True)
                st.markdown(f'<div class="movie-title">{item["title"]}</div>', unsafe_allow_html=True)
                st.markdown(f'</div>', unsafe_allow_html=True)