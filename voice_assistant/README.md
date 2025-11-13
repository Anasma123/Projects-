# Voice-Activated Personal Assistant

A personal assistant application that performs tasks like setting reminders, checking the weather, and reading the news. Integrated with speech recognition and text-to-speech libraries to create an interactive, voice-activated experience.

## Features

- **Time and Date**: Ask for the current time and date
- **Weather Information**: Check weather conditions for cities
- **News Headlines**: Get the latest news updates
- **Reminders**: Set reminders for important tasks
- **Voice Control**: Fully voice-activated interface

## Installation

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. On some systems, you might need to install PyAudio separately:
   ```
   pip install pyaudio
   ```

## Usage

Run the application:
```
python app.py
```

### Voice Commands

- **"What time is it?"** - Get current time and date
- **"What's the weather in [city]?"** - Check weather conditions
- **"Tell me the news"** - Get latest headlines
- **"Remind me to [task]"** - Set a reminder
- **"Help"** - List available commands
- **"Exit"** or **"Quit"** - Close the application

## How It Works

The assistant uses:
- **SpeechRecognition** library for voice input
- **pyttsx3** for text-to-speech output
- **Google Speech Recognition** API for speech-to-text conversion

## Requirements

- Python 3.6+
- Internet connection (for speech recognition)
- Microphone (for voice input)
- Speakers (for voice output)

## Note

This is a demonstration application. In a production environment, you would want to:
- Add error handling for network issues
- Use proper APIs for weather and news data
- Implement more sophisticated natural language processing
- Add user authentication and data persistence