from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import json
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

app = Flask(__name__)
socketio = SocketIO(app)

# Load FAQ data from JSON file
def load_faq_data():
    with open('faq.json') as f:
        return json.load(f)

faq_data = load_faq_data()

# Function to get the closest FAQ response using fuzzy matching
def get_faq_response(user_message):
    
    # Filter entries that contain both 'message' and 'response' keys
    valid_entries = [entry for entry in faq_data if 'message' in entry and 'response' in entry]
    if not valid_entries:
        return "Sorry, no valid FAQs found."

    # Extract all questions for fuzzy matching
    message = [entry['message'] for entry in valid_entries]

    # Use fuzzy matching to find the best match for the user's message
    closest_match, score = process.extractOne(user_message, message, scorer=fuzz.token_sort_ratio)

    # Set a threshold for fuzzy matching, and return a default response if no close match is found
    if score < 50:
        return "Sorry, I don't have an answer for that."
    
    print(f"Closest match: {closest_match}, Score: {score}")


    # Return the corresponding answer for the matched question
    for entry in valid_entries:
        if entry['message'] == closest_match:
            return entry['response']

    return "Sorry, something went wrong."

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('send_message')
def handle_message(data):
    user_message = data.get('message', '')
    print(f"Message from client: {user_message}")
    
    response = get_faq_response(user_message)
    print(f"Server response: {response}")
    
    emit('receive_message', {'message': response}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='127.0.0.1', port=5000)
