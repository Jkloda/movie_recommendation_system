from flask import Flask, jsonify, session
from flask_cors import CORS
import os
import mysql.connector.pooling
from flask_login import LoginManager
from dotenv import load_dotenv

load_dotenv()
login_manager = LoginManager()

app = Flask(__name__)
login_manager.init_app(app)
CORS(app, origins=["http://localhost:3000"])

connection_pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="moviefinder_pool",
    user=os.getenv('USER'),
    host=os.getenv('HOST'),
    password=os.getenv('PASS'),
    database=os.getenv('DATABASE')
)

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({"message": "Hello from Flask with CORS!"})

@app.route('/api/getuser', methods=['GET'])
def get_user():
    try:
        connection = connection_pool.get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = 'username'")
        details = cursor.fetchall()
        cursor.close()
        connection.close()
        return jsonify({"details": details})
    except:
        return jsonify({"message": "error"})

if __name__ == '__main__':
    app.run(debug=True)