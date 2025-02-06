from flask import Flask, jsonify, session, request, redirect, url_for
from flask_cors import CORS
import os
import re
import json
import requests
import json
import mysql.connector.pooling
from passlib.hash import sha256_crypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from dotenv import load_dotenv
import pandas as pd
import numpy as np
from oauthlib.oauth2 import WebApplicationClient

load_dotenv()
app = Flask(__name__)
# Configuration
GOOGLE_CLIENT_ID = os.getenv("CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("CLIENT_SECRET")
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)
app.config["SECRET_KEY"] = os.urandom(24)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
CORS(app, supports_credentials=True, origins=["https://localhost:3000", "https://192.168.50.200:3000"])
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

def create_movie_table():
    headers = ["genres", "keywords", "original_title", "overview", "popularity", "release_date", "runtime", "spoken_languages", "title", "cast", "director"]
    types = ["TEXT", "TEXT", "TEXT", "FLOAT", "TEXT", "FLOAT", "TEXT", "TEXT", "TEXT", "TEXT"]
    #keys = [1,2,3,4,5,6,7,8,9,10]
    data = pd.read_csv('../data/movie_dataset.csv', usecols=headers)
    data = data.replace(np.nan, 0)
    headers2 = ["keywords", "original_title", "overview", "popularity", "release_date", "runtime", "spoken_languages", "title", "cast", "director"]
    columns = ", ".join([f"{header} {types[index]}" for index, header in enumerate(headers2)])
    data = [tuple(row) for row in data.values]

    create_table_movies = f'CREATE TABLE IF NOT EXISTS movies (id INT AUTO_INCREMENT PRIMARY KEY, {columns});'
    create_table_genres = f'CREATE TABLE IF NOT EXISTS genres (id INT AUTO_INCREMENT PRIMARY KEY, genre TEXT);'
    create_table_bridge = f'CREATE TABLE IF NOT EXISTS movies_genres (movies_id INT, genres_id INT, PRIMARY KEY (movies_id, genres_id), FOREIGN KEY (movies_id) REFERENCES movies(id) ON DELETE CASCADE, FOREIGN KEY (genres_id) REFERENCES genres(id) ON DELETE CASCADE);'
    create_table_actors = f'CREATE TABLE IF NOT EXISTS actors (id INT AUTO_INCREMENT PRIMARY KEY, actor TEXT);'
    create_table_actors_bridge = f'CREATE TABLE IF NOT EXISTS movies_actors (movies_id INT, actors_id INT, PRIMARY KEY (movies_id, actors_id), FOREIGN KEY (movies_id) REFERENCES movies(id) ON DELETE CASCADE, FOREIGN KEY (actors_id) REFERENCES actors(id) ON DELETE CASCADE);'
    
    insert_statement_movies = f'INSERT INTO movies ({", ".join(headers2)}) VALUES (%s, %s ,%s, %s, %s, %s, %s, %s, %s, %s);'
    insert_statement_genres = f'INSERT INTO genres (genre) VALUES (%s);'
    insert_statement_actors = f'INSERT INTO genres (actor) VALUES (%s);'
    insert_statement_bridge = f'INSERT INTO movies_genres (movies_id, genres_id) VALUES (%s, %s);'
    insert_statement_actors_bridge = f'INSERT INTO movies_actors (movies_id, actors_id) VALUES (%s, %s);'

    try: 
        connection = connection_pool.get_connection()
        cursor = connection.cursor()
        cursor.execute(create_table_movies)
        cursor.execute(create_table_genres)
        cursor.execute(create_table_bridge)
        cursor.execute(create_table_actors)
        cursor.execute(create_table_actors_bridge)

        for row in data:
            row = list(row)
            genre_ids = []
            genres = str(row[0]) if row[0] else ""
            genres_list = genres.split()
            del row[0]
            for genre in genres_list:
                select_statement = f'SELECT id FROM genres WHERE genre = %s'
                cursor.execute(select_statement, (genre,))
                genres_id = cursor.fetchone()
                if(genres_id):
                    genre_ids.append(genres_id[0])
                else:
                    cursor.execute(insert_statement_genres, (genre,))
                    row_id = cursor.lastrowid
                    genre_ids.append(row_id)
            
            cursor.execute(insert_statement_movies, row) 
            movie_id = cursor.lastrowid
            for gen_id in genre_ids:
                cursor.execute('SELECT * FROM movies_genres WHERE movies_id = %s and genres_id = %s', (movie_id, gen_id))
                duplicate = cursor.fetchone()
                if(duplicate is None):
                    cursor.execute(insert_statement_bridge, (movie_id, gen_id))
        connection.commit()
    except Exception as e:
        print(f'error inserting {e}')
    finally:
        cursor.close()
        connection.close()


create_movie_table()

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

class User(UserMixin):
    def __init__(self, user):
        self.id = user['user_id']
        #self.username = user['username']

@login_manager.user_loader
def loader_user(user_id):
    try:
        connection = connection_pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT user_id, username FROM users WHERE user_id = %s;", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        return User(user) if user else None
    except Exception as e:
        print("Error loading user:", e)
        return None
        

@app.route('/api/data', methods=['GET'])
@login_required
def get_data():
    return jsonify({"message": "Hello from Flask with CORS!"}), 200

@app.route('/login', methods=['GET','POST'])
def get_user():
    if request.method == 'POST':
        try:
            result = request.get_json(silent=True)
            username = request.form.get('username') or result['username']
            password = request.form.get('password') or result['password']
            connection = connection_pool.get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            account = cursor.fetchone()
            cursor.close()
            connection.close()
            if sha256_crypt.verify(password, account['password']):
                user = User(account)
                login_user(user)
                return jsonify({'message': 'successfully logged in',
                                "username": f"{username}"}), 200
            else:
                return jsonify({'message': 'incorrect username or password'}), 401
        except Exception as e:
            return jsonify({"message": f"error handling request {e}"}), 400
        
            

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
            return jsonify({'message': f'error unknown server error {e}'}), 500
        finally:
            cursor.close()
            connection.close()

    else:
        return jsonify({'message': 'please check http request body, username, email, password are missing or method not POST '}), 400 

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