import streamlit as st
import pickle
import pandas as pd
import requests
from functools import lru_cache

FALLBACK_POSTER_URL = "https://via.placeholder.com/500x750.png?text=No+Poster"
TMDB_API_KEY = "8265bd1679663a7ea12ac168da84d2e8"

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
        .app-subtitle {
            text-align: center;
            color: #7d8590;
            margin-top: -12px;
            margin-bottom: 24px;
        }
        .movie-card {
            background: linear-gradient(160deg, #0f172a 0%, #1e293b 100%);
            border-radius: 14px;
            padding: 15px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 10px 24px rgba(2, 6, 23, 0.25);
        }
        .movie-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 8px;
            margin-top: 8px;
        }
        .movie-title {
            color: #f8fafc;
            font-weight: bold;
            margin-top: 10px;
            font-size: 15px;
            min-height: 42px;
        }
        .movie-badge {
            background: #fde68a;
            color: #111827;
            font-size: 12px;
            font-weight: 700;
            border-radius: 999px;
            padding: 4px 9px;
            display: inline-block;
        }
        h1 {
            color: #0f172a;
            text-align: center;
            margin-bottom: 6px;
        }
    </style>
""", unsafe_allow_html=True)

@lru_cache(maxsize=1000)
def fetch_movie_details(movie_id):
    default_details = {
        "poster": FALLBACK_POSTER_URL,
        "has_real_poster": False,
        "rating": "N/A",
        "year": "N/A",
        "overview": "Overview not available.",
        "genres": "N/A",
    }

    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
        response = requests.get(url, timeout=8)
        response.raise_for_status()
        data = response.json()

        poster_path = data.get("poster_path")
        release_date = data.get("release_date") or ""
        vote_average = data.get("vote_average")
        genres = data.get("genres") or []

        default_details["poster"] = (
            f"https://image.tmdb.org/t/p/w500/{poster_path}" if poster_path else FALLBACK_POSTER_URL
        )
        default_details["has_real_poster"] = bool(poster_path)
        default_details["year"] = release_date[:4] if release_date else "N/A"
        default_details["rating"] = f"{float(vote_average):.1f}/10" if vote_average is not None else "N/A"
        default_details["overview"] = data.get("overview") or "Overview not available."
        default_details["genres"] = ", ".join([g.get("name", "") for g in genres if g.get("name")]) or "N/A"
        return default_details
    except Exception:
        return default_details


def recommend(movie):
    try:
        index = movies[movies['title'] == movie].index[0]
        distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
        recommendations = []
        
        for i in distances[1:number_of_results + 1]:
            movie_row = movies.iloc[i[0]]
            movies_id = movie_row['id']
            details = fetch_movie_details(int(movies_id))
            recommendations.append({
                "title": movie_row['title'],
                "movie_id": int(movies_id),
                "poster": details["poster"],
                "has_real_poster": details["has_real_poster"],
                "rating": details["rating"],
                "year": details["year"],
                "overview": details["overview"],
                "genres": details["genres"],
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
st.markdown("<div class='app-subtitle'>Discover similar movies with posters, ratings, and details</div>", unsafe_allow_html=True)

# Search section
col1, col2, col3 = st.columns([3, 1.2, 1])
with col1:
    movie_list = list(movies['title'].values)
    selected_movie = st.selectbox(
        "🔍 Select a movie you like:",
        movie_list,
        label_visibility="collapsed"
    )

with col2:
    number_of_results = st.selectbox(
        "Results",
        options=[5, 6, 7, 8, 9, 10],
        index=0,
        help="How many similar movies to show"
    )

with col3:
    cards_per_row = st.selectbox(
        "Grid",
        options=[2, 3, 4, 5],
        index=1,
        help="Cards per row (use 2-3 for smaller screens)"
    )

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

        # Display recommendations in a responsive-style grid
        for row_start in range(0, len(recommendations), cards_per_row):
            row_items = recommendations[row_start:row_start + cards_per_row]
            cols = st.columns(cards_per_row)

            for col, item in zip(cols, row_items):
                with col:
                    st.markdown('<div class="movie-card">', unsafe_allow_html=True)
                    st.image(item["poster"], use_container_width=True)
                    st.markdown(f'<div class="movie-title">{item["title"]}</div>', unsafe_allow_html=True)
                    st.markdown(
                        f'<div class="movie-meta"><span class="movie-badge">⭐ {item["rating"]}</span><span class="movie-badge">📅 {item["year"]}</span></div>',
                        unsafe_allow_html=True,
                    )

                    details_key = f'details_{item["movie_id"]}'
                    if details_key not in st.session_state:
                        st.session_state[details_key] = False

                    if st.button("Movie Details", key=f"btn_{item['movie_id']}", use_container_width=True):
                        st.session_state[details_key] = not st.session_state[details_key]

                    if st.session_state[details_key]:
                        st.caption(f"Genres: {item['genres']}")
                        st.caption(item["overview"])

                    st.markdown('</div>', unsafe_allow_html=True)