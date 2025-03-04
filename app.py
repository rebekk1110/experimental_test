from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from your GitHub Pages site


def get_db_connection():
    db_url = os.environ.get("DATABASE_URL", "postgresql://rebekka:91p51XObu43ghFbjnLvDZvBhKIwpi2cR@dpg-cuveog0gph6c73erc2gg-a/cb_db_20d4")
    if not db_url:
        raise ValueError("DATABASE_URL environment variable not set.")
    return psycopg2.connect(db_url, sslmode='require')


@app.route('/submit', methods=['POST'])
def submit_response():
    data = request.get_json()
    participant_id = data.get('participant_id', 'anonymous')
    question_id = data.get('question_id')
    complexity = data.get('complexity')
    change_condition = data.get('change_condition')
    participant_response = data.get('participant_response')

    try:
        confidence = int(data.get('confidence', 0))  # Default to 0 if missing
        reaction_time = int(data.get('reaction_time', 0))
    except ValueError:
        confidence = 0
        reaction_time = 0
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO responses 
        (participant_id, question_id, complexity, change_condition, participant_response, confidence, reaction_time)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (participant_id, question_id, complexity, change_condition, participant_response, confidence, reaction_time))
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
            RETURNING participant_id;
        """, (gender, education, age, experience, consent))
        
        participant_id = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()

        if participant_id:
            return jsonify({"participant_id": participant_id[0]}), 200
        else:
            return jsonify({"error": "Failed to get participant_id"}), 500

    except Exception as e:
        app.logger.error("Error in /register: %s", e)
        return jsonify({"error": str(e)}), 500
        
@app.route("/")
def home():
    return "Hello, Flask is running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

