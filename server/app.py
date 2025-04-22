from flask import Flask, jsonify, session, request, redirect, url_for
from flask_cors import CORS, cross_origin
import os
import re
import sys
from werkzeug import Response
import json
import requests
import json
import mysql.connector.pooling
from passlib.hash import sha256_crypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from dotenv import load_dotenv
import pandas as pd
import numpy as np
sys.path.append(os.path.abspath('./faiss'))
from oauthlib.oauth2 import WebApplicationClient
from Recommender import Recommender
from urllib.parse import unquote
from dotenv import load_dotenv
from flasgger import Swagger

load_dotenv()

app = Flask(__name__)
swagger = Swagger(app)
# Configuration
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
GOOGLE_CLIENT_ID = os.getenv("CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("CLIENT_SECRET")
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)
app.config["SECRET_KEY"] = os.urandom(24)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config['SESSION_PERMANENT'] = True
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_SAMESITE"] = 'None'
app.config['CORS_HEADERS'] = 'Content-Type'

CORS(
    app, 
    supports_credentials=True, 
    origins=["https://127.0.0.1:3000", "https://192.168.50.200:3000", "https://localhost:5555", "https://localhost:3000"],
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "DELETE"]
)
client = WebApplicationClient(GOOGLE_CLIENT_ID)
login_manager = LoginManager()
login_manager.init_app(app)


connection_pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="moviefinder_pool",
    user=os.getenv('USER'),
    host=os.getenv('HOST'),
    password=os.getenv('PASS'),
    database=os.getenv('DATABASE')
)

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id
    def get_id(self):
        return self.id
        
@login_manager.user_loader
def load_user(user_id):
    try:
        with connection_pool.get_connection() as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT user_id as user_id, username FROM users WHERE user_id = %s;", (user_id,))
                user = cursor.fetchone()
        if user:
            return User(user['user_id'])
        else:
            return None
    except Exception as e:
        return None
    
@app.route('/api/data', methods=['GET'])
@login_required
def get_data():
    """
    Get basic protected data.
    ---
    security:
      - cookieAuth: []
    responses:
      200:
        description: Basic data returned successfully.
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Hello from Flask with CORS!"
    """
    return jsonify({"message": "Hello from Flask with CORS!"}), 200

@app.route('/api/search', methods=['POST'])
@login_required
async def get_recommendations():
    recommender = Recommender()
    req = request.get_json(silent=True) or {}
    print("Parsed JSON:", req)  # Debug line
    genre = req.get('genre', False)
    search = req.get('search', False)
    user_id = current_user.id
    try:
        if genre: 
            select_movies_statement = "SELECT movies.*, GROUP_CONCAT(DISTINCT keywords.keyword) AS keywords, GROUP_CONCAT(DISTINCT genres.genre) AS genres, GROUP_CONCAT(DISTINCT actors.actor) as actors FROM movies \
                JOIN users_movies ON users_movies.movies_id = movies.id \
                JOIN movies_keywords ON movies.id = movies_keywords.movies_id JOIN keywords ON movies_keywords.keywords_id = keywords.id \
                JOIN movies_genres ON movies.id = movies_genres.movies_id JOIN genres ON movies_genres.genres_id = genres.id \
                JOIN movies_actors ON movies.id = movies_actors.movies_id JOIN actors ON movies_actors.actors_id = actors.id \
                WHERE genres.genre = %s AND users_movies.users_id = %s GROUP BY movies.id;"
            with connection_pool.get_connection() as connection:
                with connection.cursor(dictionary=True) as cursor:
                    cursor.execute(select_movies_statement, (genre, user_id))
                    movies = cursor.fetchall()
            if not movies:
                return jsonify({'message': f'No movies favourited in selected genre, please favourite some {genre} movies or get recommendations by text'}), 400
            result = await recommender.get_recommendation(movies)
        else: 
            result = await recommender.get_recommendation(search)
        for movie in result:
            title = movie.get("title", "")
        return jsonify({'movies': result})
    except Exception as e:
        return jsonify({'error: ': str(e)})
    
@app.route('/api/add-favourite', methods=['POST'])
@login_required
def add_favourite():
    user_id = current_user.id
    req = request.get_json(silent=True)
    select_movie_statement = "SELECT movies.id FROM movies WHERE title = %s;"
    insert_favourite_statement = 'INSERT INTO users_movies (users_id, movies_id) VALUES (%s, %s);'
    if "title" in req:
        title = req['title']
    else:
        return jsonify({'message': 'no movie title'}), 400
    try:
        with connection_pool.get_connection() as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(select_movie_statement, (title,))
                movie_id = cursor.fetchone()
                if movie_id:
                    cursor.execute(insert_favourite_statement, (user_id, movie_id['id']))
                    connection.commit()
                else:
                    return jsonify({'message': 'no movie with that title'}), 400
        return jsonify({'message': 'success'}), 200
    except Exception as e:
        return jsonify({'message': f'unknown server error'}), 500
    
@app.route('/api/delete-favourite', methods=['DELETE'])
@login_required
def delete_favourite():
    user_id = current_user.id
    req = request.get_json(silent=True)
    select_movie_statement = "SELECT movies.id FROM movies WHERE title = %s;"
    delete_favourite_statement = 'DELETE FROM users_movies WHERE (users_id, movies_id) = (%s, %s);'
    if "title" in req:
        title = req['title']
    else:
        return jsonify({'message': 'no movie title'}), 400
    try:
        with connection_pool.get_connection() as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(select_movie_statement, (title,))
                movie_id = cursor.fetchone()
                if movie_id:
                    cursor.execute(delete_favourite_statement, (user_id, movie_id['id']))
                    connection.commit()
                else:
                    return jsonify({'message': 'no movie with that title'}), 400
        return jsonify({'message': 'success'}), 200
    except Exception as e:
        return jsonify({'message': f'unknown server error'}), 500
    
@app.route("/api/top-popular-movies", methods=["GET"])
@login_required
def get_top_popular_movies():
    try:
        df = pd.read_csv("../data/movie_dataset.csv", dtype={"title": str})

        if "title" not in df.columns or "popularity" not in df.columns:
            return jsonify({"error": "Dataset missing required columns"}), 400

        df = df.dropna(subset=["title", "popularity"]).drop_duplicates(subset="title")
        top_movies = df.sort_values(by="popularity", ascending=False).head(15)

        tmdb_api_key = os.environ.get("TMDB_API_KEY")
        if not tmdb_api_key:
            return jsonify({"error": "TMDB API key is not set"}), 500

        movie_data = []

        for title in top_movies["title"].tolist():
            # Call TMDB Search API to get poster_path for each title
            tmdb_search_url = "https://api.themoviedb.org/3/search/movie"
            params = {
                "api_key": tmdb_api_key,
                "query": title,
            }

            response = requests.get(tmdb_search_url, params=params)
            if response.status_code == 200:
                results = response.json().get("results")
                if results:
                    poster_path = results[0].get("poster_path")  # Take first match
                else:
                    poster_path = None
            else:
                poster_path = None

            movie_data.append({
                "title": title,
                "poster_path": poster_path
            })

        return jsonify({"top_10_popular_movies": movie_data}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/login', methods=['GET','POST'])
def get_user():
    if request.method == 'POST':
        try:
            result = request.get_json(silent=True)
            username = request.form.get('username') or result['username']
            password = request.form.get('password') or result['password']
            connection = connection_pool.get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT users.username, users.user_id as user_id, users.password FROM users WHERE username = %s", (username,))
            account = cursor.fetchone()
            cursor.close()
            connection.close()
            if not account:
                return jsonify({'message': 'incorrect username'}), 401
            if sha256_crypt.verify(password, account['password']):
                user_id = account['user_id']
                user = User(user_id)
                login_user(user)
                return jsonify({'message': 'successfully logged in',
                                "username": f"{username}"}), 200
            else:
                return jsonify({'message': 'incorrect password'}), 401
        except Exception as e:
            return jsonify({"message": f"error handling request {e}"}), 500
        
            

@app.route('/register', methods=['GET', 'POST'])
def register():
    result = request.get_json(silent=True)
    if request.method == 'POST' and 'username' in request.form or result and 'password' in request.form or result and 'email' in request.form or result:
        try:
            # Retrieve account details from form or json 
            username = request.form.get('username') or result['username']
            password = request.form.get('password') or result['password']
            email = request.form.get('email') or result['email']

            # Check username and email are in the correct format and use correct characters
            if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                return jsonify({'message': 'incorrectly formatted email'}), 400
            elif not re.match(r'[a-zA-z0-9]+', username):
                return jsonify({'message': 'incorrectly formatted username characters must be a-z, A-z, 0-9'}), 400
            
            # Create pool connection and make db calls
            connection = connection_pool.get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute('SELECT username FROM users WHERE username = %s;', (username,))
            is_username = cursor.fetchone()
            cursor.execute('SELECT email FROM users WHERE email = %s;', (email,))
            is_email = cursor.fetchone()

            # Check for duplicate entries
            if is_username:
                return jsonify({"message": "username already exists"})
            if is_email:
                return jsonify({"message": "email already exists"})
            else:
                # Hash password and make new user insert
                password = sha256_crypt.hash(password)
                cursor.execute('INSERT INTO users (username, password, email) VALUES (%s, %s, %s);', (username, password, email))
                connection.commit()
            return jsonify({'message': 'successfully created account'}), 200
        except Exception as e: 
            return jsonify({'message': f'error unknown server error'}), 500
        finally:
            cursor.close()
            connection.close()

    else:
        return jsonify({'message': 'please check http request body, username, email, password are missing or method not POST '}), 400 

@app.route("/api/get-account", methods=['GET'])
@login_required
def get_account():
    try:
        select_account_statement = 'SELECT users.email, users.username FROM users WHERE users.user_id = %s;'
        with connection_pool.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(select_account_statement, (current_user.id,))
                account = cursor.fetchone()
        if account:
            return jsonify({'account': account}), 200
        else: 
            return jsonify({'message': 'no account with that id'})
    except Exception as e:
        return jsonify({'message': 'unknown server error'})


@app.route("/api/get-favourites", methods=['GET'])
@login_required
def get_favourites():
    try:
        select_favourited_movies = "SELECT movies.id, movies.title FROM movies\
                JOIN users_movies ON users_movies.movies_id = movies.id \
                WHERE users_movies.users_id = %s GROUP BY movies.id;"
        with connection_pool.get_connection() as connection:
            with connection.cursor(dictionary=True) as cursor:
                
                    cursor.execute(select_favourited_movies, (current_user.id,))
                    movies = cursor.fetchall()
        return jsonify({"movies": movies})
    except Exception as e:
            return jsonify({'message': f'unknown server error {e}'}), 500

@app.route("/api/get-similar-movies", methods=['POST'])
@login_required
def get_similar_movies():
    try:
        req = request.get_json(silent=True)
        
        if req is None or "movie_id" not in req:
            return jsonify({"message": "movie_id is required"}), 400

        movie_id = req['movie_id']

        select_similar_movies_statement = """
            SELECT m2.id, m2.title, m2.overview
            FROM movies m2
            JOIN movies_genres mg2 ON m2.id = mg2.movies_id
            JOIN movies_genres mg ON mg.genres_id = mg2.genres_id
            WHERE mg.movies_id = %s
            AND m2.id != mg.movies_id
            LIMIT 15;
        """

        # Using connection pool and handling connection within a context manager
        with connection_pool.get_connection() as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(select_similar_movies_statement, (movie_id,))
                similar_movies = cursor.fetchall()

        if not similar_movies:
            return jsonify({"message": "No similar movies found"}), 404

        return jsonify({"similar_movies": similar_movies}), 200

    except Exception as e:
        return jsonify({"message": f"Unknown server error: {str(e)}"}), 500

@app.route("/api/get-movies", methods=['GET'])
@login_required
def get_movies():
    query = None
    select_favourited_movies = "SELECT movies.id FROM movies\
                JOIN users_movies ON users_movies.movies_id = movies.id \
                WHERE users_movies.users_id = %s GROUP BY movies.id;"
    if 'limit' in request.args:
        limit = int(request.args.get('limit'))
        print(limit)
        show_records = 40
        if limit == 0:
            max_limit = 40
        elif limit < 4800: 
            max_limit = limit + 40
        else:
            show_records = 2
        select_movies_statement = "SELECT movies.title, movies.id, movies.overview, GROUP_CONCAT(genres.genre) as genre FROM movies JOIN movies_genres ON movies.id = movies_genres.movies_id JOIN genres ON movies_genres.genres_id = genres.id GROUP BY movies.id LIMIT %s OFFSET %s;"
    else:
        return jsonify({'message': 'must include limit'}), 400
    if 'query' in request.args:
        query = request.args.get('query')
        print(query)
        query = f"%{query}%"
        select_movies_statement = "SELECT movies.title, movies.id, movies.overview, GROUP_CONCAT(genres.genre) as genre FROM movies JOIN movies_genres ON movies.id = movies_genres.movies_id JOIN genres ON movies_genres.genres_id = genres.id WHERE movies.title LIKE %s GROUP BY movies.id;"
    try: 
        with connection_pool.get_connection() as connection:
            with connection.cursor(dictionary=True) as cursor:
                if query:
                    cursor.execute(select_movies_statement, (query,))
                else:
                    cursor.execute(select_movies_statement, (show_records, max_limit,))
                movies = cursor.fetchall()
                favourites = cursor.execute(select_favourited_movies, (current_user.id,))
                favourites = cursor.fetchall()
        if movies:
            return jsonify({
                'movies': movies,
                'limit': max_limit,
                "favourites": favourites
            }), 200
        else:
            return jsonify({'message': 'error, no movies received, check limit parameter'}), 400
    except Exception as e:
            return jsonify({'message': f'unknown server error {e}'}), 500


@app.route("/google-login")
def login():
    # Generate Login URL and send redirect to URL
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@app.route("/google-login/callback")
def callback():
    # Get authorization code 
    code = request.args.get("code")
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    # Prepare and send a request to get tokens
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse token
    client.parse_request_body_response(json.dumps(token_response.json()))
    # User token to make user detail get request
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    
    # Get user details from Google response
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400
    
    # Check if user email already exists on db
    connection = connection_pool.get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT user_id FROM users WHERE email = %s;', (users_email,))
    user_id = cursor.fetchone()
    # If exists follow login session flow
    if user_id:
        user = User(user_id)
        login_user(user)
        return redirect('https://localhost:3000/')
    # If not exists then register user and follow login flow
    else: 
        cursor.execute('INSERT INTO users (username, email, google_id) VALUES (%s, %s, %s);', (users_name, users_email, unique_id,))
        connection.commit()
        cursor.execute('SELECT LAST_INSERT_ID() AS user_id;')
        user_id = cursor.fetchone()
        user = User(user_id)
        login_user(user)
        return redirect('https://localhost:3000/')



@app.route('/logout')
def logout():
    logout_user()
    return jsonify({"message": "successfully logged out"}), 200

if __name__ == '__main__':
    app.run(port=443, ssl_context=("cert.pem", "key.pem"))