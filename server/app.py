from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({"message": "Hello from Flask with CORS!"})

if __name__ == '__main__':
    app.run(debug=True)