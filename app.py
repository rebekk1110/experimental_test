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
        change_condition = data.get('change_condition')
        change_response = data.get('change_response')
        change_confidence = data.get('change_confidence')
        reaction_time = data.get('reaction_time', 0)
        original_color = data.get('original_color')
        color_response = data.get('color_response')
        color_confidence = data.get('color_confidence', 0)

        # Log the variables
        print(f"participant_id: {participant_id}, question_id: {question_id}, "
              f"change_response: {change_response}, change_condition: {change_condition}, "
              f"change_confidence: {change_confidence}, reaction_time: {reaction_time}, original_color: {original_color}, "
              f"color_response: {color_response}, color_confidence: {color_confidence}")

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO responses 
              (participant_id, question_id, change_response, change_condition, change_confidence, reaction_time , original_color, color_response, color_confidence)
            VALUES 
              (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
              participant_id, question_id, change_response, change_condition, 
              change_confidence, reaction_time, 
              original_color, color_response, color_confidence
        ))
        
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



@app.route('/complete', methods=['POST'])
def complete_survey():
    data = request.get_json()
    participant_id = data.get('participant_id')
    if not participant_id:
        return jsonify({"error": "Missing participant_id"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE participants 
            SET completed = true 
            WHERE participant_id = %s
        """, (participant_id,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Survey marked as completed"}), 200
    except Exception as e:
        app.logger.error("Error in /complete: %s", e)
        return jsonify({"error": str(e)}), 500

@app.route('/finalize', methods=['POST'])
def finalize_participant():
    data = request.get_json()
    participant_id = data.get('participant_id')
    effort = data.get('effort')
    feedback = data.get('feedback')

    if not participant_id:
        return jsonify({"error": "Missing participant_id"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE participants
            SET effort = %s,
                feedback = %s
            WHERE participant_id = %s
        """, (effort, feedback, participant_id))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Participant record updated with final data!"}), 200
    except Exception as e:
        app.logger.error("Error in /finalize: %s", e)
        return jsonify({"error": str(e)}), 500

@app.route("/")
def home():
    return "Hello, Flask is running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

