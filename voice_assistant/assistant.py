import speech_recognition as sr
import pyttsx3
import datetime
import requests
import json
import re
import random

class VoiceAssistant:
    def __init__(self):
        """
        Initialize the Voice Assistant with speech recognition and text-to-speech engines.
        """
        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Initialize text-to-speech engine
        self.tts_engine = pyttsx3.init()
        
        # Set voice properties
        voices = self.tts_engine.getProperty('voices')
        if voices:
            self.tts_engine.setProperty('voice', voices[0].id)  # Use first available voice
        self.tts_engine.setProperty('rate', 150)  # Speed of speech
        self.tts_engine.setProperty('volume', 0.9)  # Volume level
        
        # Reminders storage
        self.reminders = []
        
        # Configure recognizer for better accuracy
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        
        # Adjust for ambient noise
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
    
    def speak(self, text):
        """
        Convert text to speech.
        
        Args:
            text (str): Text to be spoken
        """
        print(f"Assistant: {text}")
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
    
    def listen(self):
        """
        Listen for voice input and convert to text.
        
        Returns:
            str: Recognized text or None if recognition failed
        """
        try:
            print("Listening...")
            with self.microphone as source:
                # Listen for audio with timeout
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            print("Recognizing...")
            # Use Google Speech Recognition
            text = self.recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text.lower()
        except sr.WaitTimeoutError:
            print("Listening timed out")
            return None
        except sr.UnknownValueError:
            print("Sorry, I didn't catch that. Could you please repeat?")
            return None
        except sr.RequestError as e:
            print(f"Could not request results from speech recognition service; {e}")
            return None
        except Exception as e:
            print(f"Error in listening: {e}")
            return None
    
    def get_current_time(self):
        """
        Get current time and date.
        
        Returns:
            str: Formatted current time and date
        """
        now = datetime.datetime.now()
        return now.strftime("%A, %B %d, %Y at %I:%M %p")
    
    def get_weather(self, city="London"):
        """
        Get weather information (simulated).
        
        Args:
            city (str): City name for weather information
            
        Returns:
            str: Weather information
        """
        # In a real implementation, you would use a weather API
        # This is a simulation for demonstration purposes
        temperatures = {
            "London": "15°C, Partly Cloudy",
            "New York": "18°C, Sunny",
            "Tokyo": "22°C, Clear",
            "Paris": "16°C, Overcast",
            "Sydney": "25°C, Sunny"
        }
        
        # Simulate API response delay
        import time
        time.sleep(1)
        
        weather = temperatures.get(city, f"{random.randint(10, 25)}°C, Partly Cloudy")
        return f"The current weather in {city} is {weather}"
    
    def get_news(self):
        """
        Get latest news headlines (simulated).
        
        Returns:
            str: News headlines
        """
        # In a real implementation, you would use a news API
        # This is a simulation for demonstration purposes
        headlines = [
            "Scientists discover new species in deep ocean",
            "Stock markets reach all-time high",
            "New breakthrough in renewable energy technology",
            "International summit addresses climate change concerns",
            "Tech company announces revolutionary new product"
        ]
        
        # Simulate API response delay
        import time
        time.sleep(1)
        
        selected_headlines = random.sample(headlines, min(3, len(headlines)))
        news_str = "Here are the latest headlines: "
        for i, headline in enumerate(selected_headlines, 1):
            news_str += f"{i}. {headline}. "
        
        return news_str
    
    def set_reminder(self, reminder_text, time_delay_minutes=1):
        """
        Set a reminder.
        
        Args:
            reminder_text (str): Text of the reminder
            time_delay_minutes (int): Delay in minutes before reminder
        """
        reminder_time = datetime.datetime.now() + datetime.timedelta(minutes=time_delay_minutes)
        self.reminders.append({
            'text': reminder_text,
            'time': reminder_time
        })
        return f"Reminder set for {time_delay_minutes} minute(s) from now."
    
    def check_reminders(self):
        """
        Check and announce any due reminders.
        """
        current_time = datetime.datetime.now()
        due_reminders = [r for r in self.reminders if r['time'] <= current_time]
        
        for reminder in due_reminders:
            self.speak(f"Reminder: {reminder['text']}")
            self.reminders.remove(reminder)
    
    def process_command(self, command):
        """
        Process voice commands and execute appropriate actions.
        
        Args:
            command (str): Recognized voice command
        """
        if not command:
            return
        
        # Time-related commands
        if "time" in command or "date" in command:
            current_time = self.get_current_time()
            self.speak(f"The current time is {current_time}")
        
        # Weather-related commands
        elif "weather" in command:
            # Extract city name if mentioned
            city_match = re.search(r'weather in (\w+)', command)
            city = city_match.group(1) if city_match else "London"
            weather_info = self.get_weather(city)
            self.speak(weather_info)
        
        # News-related commands
        elif "news" in command or "headlines" in command:
            news = self.get_news()
            self.speak(news)
        
        # Reminder-related commands
        elif "remind me" in command or "set reminder" in command:
            # Simple reminder extraction (in a real app, you'd want more sophisticated parsing)
            if "to " in command:
                reminder_text = command.split("to ", 1)[1]
            else:
                reminder_text = "something"
            
            response = self.set_reminder(reminder_text, 1)  # 1 minute reminder for demo
            self.speak(response)
        
        # Help command
        elif "help" in command:
            self.speak("I can help you with the following tasks: "
                      "Tell you the time and date, check the weather, read the news, "
                      "and set reminders. Just say what you need!")
        
        # Exit command
        elif "exit" in command or "quit" in command or "goodbye" in command:
            self.speak("Goodbye! Have a great day!")
            return False
        
        # Default response
        else:
            responses = [
                "I'm sorry, I didn't understand that. Can you please repeat?",
                "I'm not sure what you mean. Try asking for the time, weather, news, or to set a reminder.",
                "I didn't catch that. Say 'help' to hear what I can do."
            ]
            self.speak(random.choice(responses))
        
        return True
    
    def run(self):
        """
        Main loop to run the voice assistant.
        """
        self.speak("Hello! I'm your voice-activated personal assistant. How can I help you today?")
        self.speak("Say 'help' to hear what I can do, or 'exit' to quit.")
        
        running = True
        while running:
            # Check for due reminders
            self.check_reminders()
            
            # Listen for command
            command = self.listen()
            
            if command:
                # Process the command
                running = self.process_command(command)
            
            # Small delay to prevent excessive CPU usage
            import time
            time.sleep(0.1)

def main():
    """
    Main function to run the voice assistant.
    """
    print("=" * 60)
    print("VOICE-ACTIVATED PERSONAL ASSISTANT")
    print("=" * 60)
    print("Initializing...")
    
    try:
        assistant = VoiceAssistant()
        assistant.run()
    except KeyboardInterrupt:
        print("\nAssistant stopped by user.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()