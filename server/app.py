from flask import Flask, jsonify, session, request
from flask_cors import CORS
import os
import re
import mysql.connector.pooling
from passlib.hash import sha256_crypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = "abc123"
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = False
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
CORS(app, origins=["http://localhost:3000"])

'''if __name__ == '__main__':
    app.run(debug=True)'''

login_manager = LoginManager()
login_manager.init_app(app)

connection_pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="moviefinder_pool",
    user=os.getenv('USER'),
    host=os.getenv('HOST'),
    password=os.getenv('PASS'),
    database=os.getenv('DATABASE')
)

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
                return jsonify({'message': 'successfully logged in'}), 200
            else:
                return jsonify({'message': 'incorrect username or password'}), 401
        except:
            return jsonify({"message": "error handling request"}), 400

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

    else:
        return jsonify({'message': 'please check http request body, username, email, password are missing or method not POST '}), 400 

@app.route('/logout')
def logout():
    logout_user()
    return jsonify({"message": "successfully logged out"}), 200