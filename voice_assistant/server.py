"""
Voice Assistant Web Application with Server-Side Processing
"""

from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
import pyttsx3
import io
import base64
import datetime
import random

app = Flask(__name__)

# Initialize speech recognizer
recognizer = sr.Recognizer()

# We'll simulate text-to-speech since actual TTS in web requires more complex setup
def get_response(command):
    """
    Process voice commands and generate responses.
    """
    command = command.lower()
    
    # Time-related commands
    if "time" in command or "date" in command:
        now = datetime.datetime.now()
        return f"The current time is {now.strftime('%I:%M %p')} on {now.strftime('%A, %B %d, %Y')}"
    
    # Weather-related commands (simulated)
    elif "weather" in command:
        # In a real app, you would call a weather API
        weather_data = {
            "London": "15°C, Partly Cloudy",
            "New York": "18°C, Sunny",
            "Tokyo": "22°C, Clear",
            "Paris": "16°C, Overcast",
            "Sydney": "25°C, Sunny"
        }
        
        # Extract city if mentioned
        for city in weather_data.keys():
            if city.lower() in command:
                return f"The current weather in {city} is {weather_data[city]}"
        
        # Default to London
        return f"The current weather in London is {weather_data['London']}"
    
    # News-related commands (simulated)
    elif "news" in command or "headlines" in command:
        headlines = [
            "Scientists discover new species in deep ocean",
            "Stock markets reach all-time high",
            "New breakthrough in renewable energy technology",
            "International summit addresses climate change concerns",
            "Tech company announces revolutionary new product"
        ]
        
        selected_headlines = random.sample(headlines, min(3, len(headlines)))
        news_str = "Here are the latest headlines: "
        for i, headline in enumerate(selected_headlines, 1):
            news_str += f"{i}. {headline}. "
        
        return news_str
    
    # Reminder-related commands (simulated)
    elif "remind" in command or "reminder" in command:
        return "Reminder set successfully. I'll remind you in 1 minute."
    
    # Help command
    elif "help" in command:
        return ("I can help you with the following tasks: "
                "Tell you the time and date, check the weather, read the news, "
                "and set reminders. Just say what you need!")
    
    # Exit command
    elif "exit" in command or "quit" in command or "goodbye" in command:
        return "Goodbye! Have a great day!"
    
    # Default response
    else:
        responses = [
            "I'm sorry, I didn't understand that. Can you please repeat?",
            "I'm not sure what you mean. Try asking for the time, weather, news, or to set a reminder.",
            "I didn't catch that. Say 'help' to hear what I can do."
        ]
        return random.choice(responses)

@app.route('/')
def index():
    """
    Serve the main page.
    """
    return render_template('index.html')

@app.route('/process_audio', methods=['POST'])
def process_audio():
    """
    Process audio data sent from the client.
    """
    try:
        # Get audio data from request
        audio_data = request.json.get('audio')
        
        if not audio_data:
            return jsonify({'error': 'No audio data received'}), 400
        
        # Decode base64 audio data
        # Note: In a real implementation, you would process the actual audio
        # For this demo, we'll simulate recognition
        
        # Simulate speech recognition
        recognized_text = "what time is it"  # This would be the actual recognized text
        
        # Process the command
        response_text = get_response(recognized_text)
        
        # In a real implementation, you would convert response_text to speech
        # and return the audio data
        
        return jsonify({
            'success': True,
            'recognized_text': recognized_text,
            'response_text': response_text,
            'audio_response': ''  # This would be base64 encoded audio data
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/process_text', methods=['POST'])
def process_text():
    """
    Process text command sent from the client.
    """
    try:
        # Get text command from request
        command = request.json.get('command')
        
        if not command:
            return jsonify({'error': 'No command received'}), 400
        
        # Process the command
        response_text = get_response(command)
        
        return jsonify({
            'success': True,
            'response_text': response_text
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)