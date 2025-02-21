from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from your GitHub Pages site

# Local database configuration for testing
DATABASE_CONFIG = {
    'dbname': 'test1',
    'user': 'Rebekka',
    'password': 'rebekka',
    'host': 'localhost',
    'port': 5432  # or your configured port
}

def get_db_connection():
    # Use the DATABASE_URL environment variable if it exists (e.g., on Render)
    db_url = os.environ.get('DATABASE_URL')
    if db_url:
        return psycopg2.connect(db_url)
    else:
        return psycopg2.connect(**DATABASE_CONFIG)

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

@app.route('/register', methods=['POST'])
def register_participant():
    data = request.get_json()
    gender = data.get('gender')
    education = data.get('education')
    age = data.get('age')
    experience = data.get('experience')
    consent = data.get('consent', True)
    
    try:
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
    except Exception as e:
        app.logger.error("Error in /register: %s", e)
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
