# Movie Recommendation System

A content-based movie recommendation web app built with Streamlit.

Users can select a movie and instantly get similar movie suggestions with posters, ratings, release year, genres, and overview details.

## Features

- Content-based recommendations using a precomputed similarity matrix
- Interactive Streamlit UI with responsive movie cards
- TMDB poster + metadata integration
- Fallback thumbnail when poster is unavailable
- Adjustable number of recommendations (5 to 10)
- Adjustable grid layout (2 to 5 cards per row)
- Per-movie details toggle (genres + overview)
- Session state support so results remain visible after interactions

## Project Structure

- app.py: Main Streamlit application
- movie.ipynb: Notebook used during model/data preparation
- movies_dict.pkl: Serialized movie metadata used by the app
- similarity.pkl: Serialized similarity matrix used for recommendations
- movies.pkl: Additional serialized data file
- requirements.txt: Python dependencies
- Procfile: Deployment startup command
- setup.sh: Streamlit server config setup for deployment
- Data/tmdb_5000_movies.csv: Raw movies dataset
- Data/tmdb_5000_credits.csv: Raw credits dataset

## Tech Stack

- Python
- Streamlit
- Pandas
- Requests
- Pickle (serialized model/data artifacts)
- TMDB API

## How Recommendations Work

This app uses a content-based filtering approach.

1. Movie metadata is cleaned and transformed during preprocessing (see movie.ipynb).
2. A similarity matrix is generated and stored in similarity.pkl.
3. At runtime, the selected movie index is matched against similarity scores.
4. Top N similar movies are returned and enriched with TMDB details.

## Prerequisites

- Python 3.9+
- pip
- Internet connection (required for fetching TMDB posters/details)

## Installation

1. Clone the repository.
2. Move into the project folder.
3. Create and activate a virtual environment.
4. Install dependencies.

Windows PowerShell example:

python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

## Run Locally

Important: run with Streamlit, not with plain Python.

streamlit run app.py

Then open the local URL shown in terminal (usually http://localhost:8501).

## Deployment

This project already includes deployment helpers:

- Procfile
- setup.sh

Procfile command:

web: sh setup.sh && streamlit run app.py

setup.sh creates Streamlit config with:

- headless mode enabled
- dynamic port from PORT environment variable
- CORS disabled for platform compatibility

## Configuration Notes

Current app.py uses a hardcoded TMDB API key.

Recommended production approach:

1. Store key in environment variable TMDB_API_KEY.
2. Read it in app.py using os.getenv.
3. Do not commit secrets in source control.

## Usage

1. Select a movie from the dropdown.
2. Choose number of results.
3. Choose cards per row for your screen.
4. Click Get Recommendations.
5. Click Movie Details on a card to show/hide overview and genres.

## Troubleshooting

### 1) Missing ScriptRunContext warning
Cause: app started with python app.py.
Fix: run streamlit run app.py.

### 2) Posters not loading / timeout
Cause: TMDB API/network timeout.
Fix: app automatically shows fallback thumbnails; check internet/firewall if persistent.

### 3) Recommendations not showing
Check that these files exist in the project root:

- movies_dict.pkl
- similarity.pkl

### 4) Dependency issues
Recreate virtual environment and reinstall requirements:

deactivate
Remove-Item -Recurse -Force .\venv
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

## Known Limitations

- Recommendation quality depends on preprocessing quality in movie.ipynb
- TMDB dependency means posters/details need internet
- Hardcoded API key should be replaced before production use

## Future Improvements

- Move TMDB key to environment variable
- Add search with fuzzy matching
- Add loading skeletons for improved UX
- Add unit tests for recommendation logic
- Add CI checks and formatter/linter pipeline

## Author

Developed as a Movie Recommendation project using Streamlit and TMDB integration.

If this project helped you, consider starring the repository and sharing feedback.
