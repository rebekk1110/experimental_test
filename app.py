from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from your GitHub Pages site

# Database configuration (update these with your settings)
DATABASE_CONFIG = {
    'dbname': 'test1',
    'user': 'Rebekka',
    'password': 'rebekka',
    'host': 'localhost',
    'port': 5432  # or your configured port
}

# Establish a connection (or use a connection pool)
def get_db_connection():
    conn = psycopg2.connect(**DATABASE_CONFIG)
    return conn

@app.route('/submit', methods=['POST'])
def submit_response():
    data = request.get_json()
    user_id = data.get('user_id')
    response_text = data.get('response')
    timestamp = data.get('timestamp')
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO responses (user_id, response, timestamp) VALUES (%s, %s, %s)",
        (user_id, response_text, timestamp)
    )
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify({"message": "Response saved!"}), 200

if __name__ == '__main__':
    app.run(debug=True)
