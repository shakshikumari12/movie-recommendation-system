import streamlit as st
import pandas as pd
import pickle
import requests
import time

# Load TMDb API Key (Secure storage recommended)
API_KEY = "2c66edeead18783ccf207c60a1fc0847"

# Apply custom CSS for Netflix-style UI
st.markdown("""
    <style>
        .movie-card {
            text-align: center;
            transition: transform 0.3s;
        }
        .movie-card:hover {
            transform: scale(1.05);
        }
        .movie-title {
            font-size: 16px;
            font-weight: bold;
            margin-top: 5px;
        }
        img {
            border-radius: 10px;
            width: 150px;
            height: 225px;
        }
        
        .stButton>button {
            background-color: #e50914; /* Netflix Red */
            color: white;
            border-radius: 5px;
            padding: 10px 20px;
            font-size: 16px;
            font-weight: bold;
        }
        h1, h2, h3, h4, h5, h6, p{
            color: white !important;
        }
        .stApp {
            background-color: black;
        }
        
        
    </style>
""", unsafe_allow_html=True)


# Cache movie posters
@st.cache_data
def fetch_poster(movie_id):
    """Fetch movie poster from TMDb with retry logic."""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"

    for _ in range(3):  # Retry up to 3 times
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()

            if data.get('poster_path'):
                return f"https://image.tmdb.org/t/p/w500/{data['poster_path']}"
        except requests.exceptions.RequestException:
            time.sleep(1)  # Wait before retrying

    return "https://via.placeholder.com/500x750?text=No+Image+Available"


# Load movie data
movies_dict = pickle.load(open('movie_dictionary.pkl', 'rb'))
movies = pd.DataFrame.from_dict(movies_dict) if isinstance(movies_dict, dict) else pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))


# Cache recommendations
@st.cache_data
def recommend(movie):
    """Fetch recommended movies."""
    indices = movies[movies['title'] == movie].index.tolist()
    if not indices:
        return [], []  # Handle missing movie case

    movie_index = indices[0]
    distances = similarity[movie_index]
    movies_list = sorted(enumerate(distances), key=lambda x: x[1], reverse=True)[1:10]  # Get top 9 movies

    recommended_movies, recommended_posters = [], []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_posters


# Streamlit App
st.title('🎬 Movie Recommendation System')

# Dropdown for selecting a movie
selected_movie_name = st.selectbox('Select a movie:', movies['title'].values)

if st.button('Recommend'):
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie_name)

    if recommended_movie_names:
        num_movies = len(recommended_movie_names)
        num_cols = 5  # Set max columns per row

        # Create rows dynamically
        for i in range(0, num_movies, num_cols):
            cols = st.columns(num_cols)
            for j in range(num_cols):
                if i + j < num_movies:
                    with cols[j]:
                        st.image(recommended_movie_posters[i + j], use_container_width=True)
                        st.markdown(f"<p class='movie-title'>{recommended_movie_names[i + j]}</p>", unsafe_allow_html=True)

    else:
        st.error("No recommendations found. Try another movie.")

#names ,posters = recommend(selected_movie_name)
  # for i in recommendations:
   # st.write(i)


#this is the made in heaven