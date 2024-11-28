from flask import Flask, jsonify, session, request
from flask_cors import CORS
import os
import mysql.connector.pooling
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

@app.route('/api/login', methods=['GET','POST'])
def get_user():
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            password = request.form.get('password')
            connection = connection_pool.get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            account = cursor.fetchone()
            cursor.close()
            connection.close()
            if account['password'] == password:
                user = User(account)
                login_user(user)
                return jsonify({'message': 'successfully logged in'}), 200
            else:
                return jsonify({'message': 'incorrect username or password'}), 401
        except:
            return jsonify({"message": "error handling request"}), 400

@app.route('/api/logout')
def logout():
    logout_user()
    return jsonify({"message": "successfully logged out"}), 200