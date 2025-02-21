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

# Establish a connection (or use a connection pool
def get_db_connection():
    conn = psycopg2.connect(**DATABASE_CONFIG)
    return conn

@app.route('/register', methods=['POST'])
def register_participant():
    data = request.get_json()
    gender = data.get('gender')
    education = data.get('education')
    age = data.get('age')
    experience = data.get('experience')
    consent = data.get('consent', True)  # Assuming consent is given if the form is submitted

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO participants (gender, education, age, experience, consent)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id;
    """, (gender, education, age, experience, consent))
    participant_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"participant_id": participant_id}), 200


@app.route('/submit', methods=['POST'])
def submit_response():
    data = request.get_json()
    participant_id = data.get('participant_id')  # Provided from the registration step
    map_number = data.get('map')
    response_text = data.get('response')
    timestamp = data.get('timestamp')
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO map_responses (participant_id, map_number, response, submitted_at)
        VALUES (%s, %s, %s, %s)
    """, (participant_id, map_number, response_text, timestamp))
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify({"message": "Response saved!"}), 200


if __name__ == '__main__':
    app.run(debug=True)
