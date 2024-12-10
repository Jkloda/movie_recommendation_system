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

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

class User(UserMixin):
    def __init__(self, user):
        self.id = user['user_id']
        self.username = user['username']

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
            
            username = request.form.get('username') or result['username']
            password = request.form.get('password') or result['password']
            email = request.form.get('email') or result['email']

            if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                return jsonify({'message': 'incorrectly formatted email'}), 400
            elif not re.match(r'[a-zA-z0-9]+', username):
                return jsonify({'message': 'incorrectly formatted username characters must be a-z, A-z, 0-9'}), 400
            
            connection = connection_pool.get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute('SELECT username FROM users WHERE username = %s;', (username,))
            is_username = cursor.fetchone()
            cursor.execute('SELECT email FROM users WHERE email = %s;', (email,))
            is_email = cursor.fetchone()

            if is_username:
                return jsonify({"message": "username already exists"})
            if is_email:
                return jsonify({"message": "email already exists"})
            else:
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
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@app.route("/google-login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    # Prepare and send a request to get tokens! Yay tokens!
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

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))
    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400
    
    return json.dumps({unique_id: unique_id, users_email: users_email, users_name: users_name})


@app.route('/logout')
def logout():
    logout_user()
    return jsonify({"message": "successfully logged out"}), 200

if __name__ == '__main__':
    app.run(port=443, ssl_context=("cert.pem", "key.pem"))