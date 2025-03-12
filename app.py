from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os
import json  # Add this import at the top of your file

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
    try:
        # Log the data to check what's being received
        print(f"Received data: {data}")

        participant_id = data.get('participant_id', 'anonymous')
        print(f"participant_id type: {type(participant_id)}, value: {participant_id}")

        question_id = data.get('question_id')
        participant_response= data.get('participant_response')
        change_condition = data.get('change_condition')
        confidence = data.get('confidence', 0)
        reaction_time = data.get('reaction_time', 0)

        # Log the variables
        print(f"participant_id: {participant_id}, question_id: {question_id}, participant_response: {participant_response}, change_condition: {change_condition}")
        
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO responses (participant_id, question_id, participant_response, change_condition, confidence, reaction_time)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (participant_id, question_id, participant_response, change_condition, confidence, reaction_time))
        
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Response saved!"}), 200

    except Exception as e:
        # Log the error and send the error response
        app.logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500



@app.route('/register', methods=['POST'])
def register_participant():
    data = request.get_json()
    gender = data.get('gender')
    education = data.get('education')
    age = data.get('age')
    experience = data.get('experience')
    consent = data.get('consent', True)
    
    try:
        # Create a connection to the database
        conn = get_db_connection()
        cur = conn.cursor()

        # Insert the participant's data, without the need to specify created_at (it will be automatically set)
        cur.execute("""
            INSERT INTO participants (gender, education, age, experience, consent)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING participant_id;
        """, (gender, education, age, experience, consent))
        
        # Fetch the participant_id
        participant_id = cur.fetchone()[0]
        
        conn.commit()  # Commit the changes
        cur.close()
        conn.close()

        if participant_id:
            return jsonify({"participant_id": participant_id}), 200
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

