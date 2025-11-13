"""
Advanced AI Voice Assistant with NLP, Machine Learning, and Conversational Intelligence
"""
import re
import json
import datetime
import random
import logging
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

# AI and ML libraries
import spacy
import torch
import numpy as np
import pandas as pd
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from langdetect import detect
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Django models (for database interactions)
from voice_app.models import VoiceCommand, UserProfile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedVoiceAssistant:
    """
    Advanced AI Voice Assistant with comprehensive NLP capabilities,
    machine learning models, and conversational intelligence.
    """
    
    def __init__(self, user=None):
        """
        Initialize the Advanced Voice Assistant with AI models and capabilities.
        
        Args:
            user: Django User object (optional)
        """
        self.user = user
        self.user_profile = None
        if user:
            try:
                self.user_profile = UserProfile.objects.get(user=user)
            except UserProfile.DoesNotExist:
                logger.warning(f"User profile not found for user {user.username}")
        
        # Load spaCy model for advanced NLP
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.error("spaCy English model not found. Please install with: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Initialize sentiment analyzer
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        
        # Initialize transformers pipeline for intent classification
        try:
            self.intent_classifier = pipeline(
                "text-classification",
                model="microsoft/DialoGPT-medium",
                tokenizer="microsoft/DialoGPT-medium"
            )
        except Exception as e:
            logger.warning(f"Could not load DialoGPT model: {e}")
            self.intent_classifier = None
        
        # Initialize translation model
        try:
            self.translator = pipeline("translation_en_to_fr", 
                                     model="Helsinki-NLP/opus-mt-en-fr")
        except Exception as e:
            logger.warning(f"Could not load translation model: {e}")
            self.translator = None
        
        # Command history for context awareness
        self.command_history = []
        self.conversation_context = {}
        
        # Intent mapping for command classification
        self.intent_mapping = {
            "time_query": ["time", "date", "clock", "hour", "minute", "second", "day", "today"],
            "weather_query": ["weather", "temperature", "climate", "forecast", "rain", "sun", "cloud"],
            "news_query": ["news", "headline", "update", "current event", "breaking"],
            "reminder_query": ["remind", "reminder", "alarm", "schedule", "appointment"],
            "calculation_query": ["calculate", "compute", "math", "add", "subtract", "multiply", "divide"],
            "search_query": ["search", "find", "look", "google", "browse"],
            "music_query": ["music", "song", "play", "spotify", "youtube"],
            "navigation_query": ["navigate", "direction", "map", "route", "location"],
            "help_query": ["help", "assist", "support", "guide", "instruction"],
            "exit_query": ["exit", "quit", "stop", "bye", "goodbye"]
        }
        
        # Response templates for different intents
        self.response_templates = {
            "time_query": [
                "The current time is {time}.",
                "It's {time} right now.",
                "The time is {time}."
            ],
            "weather_query": [
                "The current weather in {location} is {weather}.",
                "It's {weather} in {location} at the moment.",
                "The weather forecast for {location} shows {weather}."
            ],
            "news_query": [
                "Here are the latest headlines: {headlines}",
                "Current news updates: {headlines}",
                "Top stories right now: {headlines}"
            ],
            "reminder_query": [
                "I've set a reminder for {time}.",
                "Reminder scheduled for {time}.",
                "Your reminder has been set for {time}."
            ],
            "calculation_query": [
                "The result is {result}.",
                "That equals {result}.",
                "The calculation gives {result}."
            ],
            "search_query": [
                "I found information about {topic}.",
                "Here's what I know about {topic}.",
                "Searching for {topic} yielded these results."
            ],
            "music_query": [
                "Playing {song} for you.",
                "Now playing {song}.",
                "I'll play {song} for you."
            ],
            "navigation_query": [
                "The route to {destination} is displayed.",
                "Directions to {destination} are ready.",
                "Navigating to {destination}."
            ],
            "help_query": [
                "I can help with time, weather, news, reminders, calculations, searches, music, and navigation.",
                "Try asking about time, weather, news, or setting reminders.",
                "I can assist with various tasks. Say 'help' for more information."
            ],
            "exit_query": [
                "Goodbye! Have a great day!",
                "See you later!",
                "Farewell! Take care!"
            ],
            "unknown": [
                "I'm sorry, I didn't understand that. Can you please rephrase?",
                "I'm not sure what you mean. Could you try asking differently?",
                "I didn't catch that. Please try again."
            ]
        }
        
        # Initialize TF-IDF vectorizer for similarity matching
        self.tfidf_vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        self.command_vectors = []
        self.command_texts = []
        
        # Download NLTK data if not already present
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
            
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocess text for NLP analysis.
        
        Args:
            text (str): Input text
            
        Returns:
            str: Preprocessed text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Tokenize and remove stopwords
        if self.nlp:
            doc = self.nlp(text)
            tokens = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
            text = ' '.join(tokens)
        
        return text.strip()
    
    def detect_language(self, text: str) -> str:
        """
        Detect the language of the input text.
        
        Args:
            text (str): Input text
            
        Returns:
            str: Detected language code
        """
        try:
            return detect(text)
        except:
            return "en"  # Default to English
    
    def translate_text(self, text: str, target_lang: str = "en") -> str:
        """
        Translate text to target language.
        
        Args:
            text (str): Text to translate
            target_lang (str): Target language code
            
        Returns:
            str: Translated text
        """
        if not self.translator or target_lang != "fr":
            return text  # Return original if translation not available
        
        try:
            result = self.translator(text)
            return result[0]['translation_text']
        except Exception as e:
            logger.warning(f"Translation failed: {e}")
            return text
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment of the input text.
        
        Args:
            text (str): Input text
            
        Returns:
            Dict[str, float]: Sentiment scores
        """
        # Use VADER sentiment analyzer
        scores = self.sentiment_analyzer.polarity_scores(text)
        
        # Also use TextBlob for comparison
        blob = TextBlob(text)
        textblob_sentiment = blob.sentiment.polarity
        
        # Combine scores
        combined_scores = {
            'vader_compound': scores['compound'],
            'vader_positive': scores['pos'],
            'vader_negative': scores['neg'],
            'vader_neutral': scores['neu'],
            'textblob_polarity': textblob_sentiment,
            'overall_sentiment': 'positive' if scores['compound'] > 0.05 else 
                               'negative' if scores['compound'] < -0.05 else 'neutral'
        }
        
        return combined_scores
    
    def extract_entities(self, text: str) -> List[Dict]:
        """
        Extract named entities from text using spaCy.
        
        Args:
            text (str): Input text
            
        Returns:
            List[Dict]: List of extracted entities
        """
        if not self.nlp:
            return []
        
        doc = self.nlp(text)
        entities = []
        
        for ent in doc.ents:
            entities.append({
                'text': ent.text,
                'label': ent.label_,
                'description': spacy.explain(ent.label_),
                'start': ent.start_char,
                'end': ent.end_char
            })
        
        return entities
    
    def classify_intent(self, text: str) -> str:
        """
        Classify the intent of the input text.
        
        Args:
            text (str): Input text
            
        Returns:
            str: Classified intent
        """
        # Preprocess text
        processed_text = self.preprocess_text(text)
        
        # Check for keyword matches first
        for intent, keywords in self.intent_mapping.items():
            for keyword in keywords:
                if keyword in processed_text:
                    return intent
        
        # Use transformer model if available
        if self.intent_classifier:
            try:
                result = self.intent_classifier(text)
                # Map transformer output to our intents
                # This is a simplified mapping - in practice, you'd train a custom classifier
                label = result[0]['label'].lower()
                if 'question' in label or 'query' in label:
                    return 'help_query'
                elif 'statement' in label:
                    return 'unknown'
            except Exception as e:
                logger.warning(f"Intent classification failed: {e}")
        
        return "unknown"
    
    def get_current_time(self) -> str:
        """
        Get current time and date.
        
        Returns:
            str: Formatted current time and date
        """
        now = datetime.datetime.now()
        return now.strftime("%A, %B %d, %Y at %I:%M %p")
    
    def get_weather(self, city: str = "London") -> str:
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
            "Sydney": "25°C, Sunny",
            "Berlin": "12°C, Rainy",
            "Moscow": "-5°C, Snowy",
            "Dubai": "35°C, Sunny"
        }
        
        # Simulate API response delay
        import time
        time.sleep(0.5)
        
        weather = temperatures.get(city, f"{random.randint(10, 25)}°C, Partly Cloudy")
        return weather
    
    def get_news(self) -> str:
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
            "Tech company announces revolutionary new product",
            "Major sports event concludes with record-breaking performances",
            "Healthcare advances show promising results in clinical trials",
            "Space mission successfully lands on distant planet",
            "Cultural festival celebrates diversity and unity",
            "Educational initiative improves literacy rates worldwide"
        ]
        
        # Simulate API response delay
        import time
        time.sleep(0.5)
        
        selected_headlines = random.sample(headlines, min(3, len(headlines)))
        news_str = " ".join([f"{i+1}. {headline}." for i, headline in enumerate(selected_headlines)])
        
        return news_str
    
    def set_reminder(self, reminder_text: str, time_delay_minutes: int = 1) -> str:
        """
        Set a reminder.
        
        Args:
            reminder_text (str): Text of the reminder
            time_delay_minutes (int): Delay in minutes before reminder
            
        Returns:
            str: Confirmation message
        """
        reminder_time = datetime.datetime.now() + datetime.timedelta(minutes=time_delay_minutes)
        
        # In a real implementation, you would store this in a database
        # and set up a scheduled task
        
        return f"Reminder set for {time_delay_minutes} minute(s) from now: {reminder_text}"
    
    def perform_calculation(self, expression: str) -> str:
        """
        Perform a mathematical calculation.
        
        Args:
            expression (str): Mathematical expression
            
        Returns:
            str: Calculation result
        """
        try:
            # Simple calculator - in practice, use a proper expression parser
            # This is a basic example and should be expanded for production use
            result = eval(expression)
            return str(result)
        except Exception as e:
            return f"Error performing calculation: {str(e)}"
    
    def search_information(self, query: str) -> str:
        """
        Search for information (simulated).
        
        Args:
            query (str): Search query
            
        Returns:
            str: Search results
        """
        # In a real implementation, you would use a search API
        # This is a simulation for demonstration purposes
        
        # Simulate API response delay
        import time
        time.sleep(1)
        
        responses = [
            f"I found information about {query}. It's an interesting topic with many aspects to explore.",
            f"Regarding {query}, there are several key points to consider.",
            f"Research on {query} shows various perspectives and findings."
        ]
        
        return random.choice(responses)
    
    def play_music(self, song: str) -> str:
        """
        Play music (simulated).
        
        Args:
            song (str): Song name
            
        Returns:
            str: Confirmation message
        """
        # In a real implementation, you would interface with a music service
        # This is a simulation for demonstration purposes
        
        responses = [
            f"Playing {song} for you now.",
            f"Now streaming {song}.",
            f"Enjoy {song}!",
            f"Starting {song} playback."
        ]
        
        return random.choice(responses)
    
    def navigate(self, destination: str) -> str:
        """
        Provide navigation (simulated).
        
        Args:
            destination (str): Destination name
            
        Returns:
            str: Navigation information
        """
        # In a real implementation, you would interface with a maps service
        # This is a simulation for demonstration purposes
        
        responses = [
            f"Calculating route to {destination}. Turn-by-turn directions are ready.",
            f"Navigating to {destination}. Estimated arrival time: 15 minutes.",
            f"Route to {destination} displayed. Next turn in 200 meters.",
            f"Directions to {destination} loaded. Starting navigation now."
        ]
        
        return random.choice(responses)
    
    def update_context(self, command: str, response: str):
        """
        Update conversation context with the latest interaction.
        
        Args:
            command (str): User command
            response (str): Assistant response
        """
        self.command_history.append({
            'timestamp': datetime.datetime.now(),
            'command': command,
            'response': response,
            'intent': self.classify_intent(command)
        })
        
        # Keep only the last 10 interactions for context
        if len(self.command_history) > 10:
            self.command_history = self.command_history[-10:]
        
        # Update TF-IDF vectors for similarity matching
        self.command_texts.append(command)
        if len(self.command_texts) > 1:
            try:
                self.command_vectors = self.tfidf_vectorizer.fit_transform(self.command_texts)
            except Exception as e:
                logger.warning(f"TF-IDF vectorization failed: {e}")
    
    def find_similar_command(self, new_command: str) -> Optional[str]:
        """
        Find the most similar previous command using cosine similarity.
        
        Args:
            new_command (str): New command to compare
            
        Returns:
            Optional[str]: Most similar previous command, or None if not found
        """
        if len(self.command_texts) < 1:
            return None
        
        try:
            # Vectorize the new command
            new_vector = self.tfidf_vectorizer.transform([new_command])
            
            # Calculate cosine similarities
            similarities = cosine_similarity(new_vector, self.command_vectors)
            
            # Find the most similar command
            max_similarity_idx = similarities.argmax()
            max_similarity = similarities[0][max_similarity_idx]
            
            # Return the most similar command if similarity is above threshold
            if max_similarity > 0.7:  # Adjust threshold as needed
                return self.command_texts[max_similarity_idx]
        except Exception as e:
            logger.warning(f"Similarity matching failed: {e}")
        
        return None
    
    def generate_response(self, command: str) -> str:
        """
        Generate an appropriate response based on the command.
        
        Args:
            command (str): User command
            
        Returns:
            str: Generated response
        """
        # Preprocess the command
        processed_command = self.preprocess_text(command)
        
        # Classify intent
        intent = self.classify_intent(command)
        
        # Extract entities
        entities = self.extract_entities(command)
        
        # Analyze sentiment
        sentiment = self.analyze_sentiment(command)
        
        # Detect language
        language = self.detect_language(command)
        
        # Translate if needed (for demonstration, we'll translate to French if not in English)
        if language != "en":
            translated_command = self.translate_text(command, "en")
            logger.info(f"Translated command: {translated_command}")
        
        # Generate response based on intent
        response = ""
        
        if intent == "time_query":
            current_time = self.get_current_time()
            template = random.choice(self.response_templates["time_query"])
            response = template.format(time=current_time)
        
        elif intent == "weather_query":
            # Extract city from entities or default to London
            city = "London"
            for entity in entities:
                if entity['label'] in ['GPE', 'LOC']:  # Geopolitical entity or location
                    city = entity['text']
                    break
            weather_info = self.get_weather(city)
            template = random.choice(self.response_templates["weather_query"])
            response = template.format(location=city, weather=weather_info)
        
        elif intent == "news_query":
            news = self.get_news()
            template = random.choice(self.response_templates["news_query"])
            response = template.format(headlines=news)
        
        elif intent == "reminder_query":
            # Extract reminder text (simplified)
            reminder_text = command
            if "remind me to" in command.lower():
                reminder_text = command.lower().split("remind me to")[1].strip()
            elif "set a reminder for" in command.lower():
                reminder_text = command.lower().split("set a reminder for")[1].strip()
            
            reminder_response = self.set_reminder(reminder_text)
            template = random.choice(self.response_templates["reminder_query"])
            # For simplicity, we'll just use the response as is
            response = reminder_response
        
        elif intent == "calculation_query":
            # Extract mathematical expression (simplified)
            result = self.perform_calculation(processed_command)
            template = random.choice(self.response_templates["calculation_query"])
            response = template.format(result=result)
        
        elif intent == "search_query":
            # Extract search query (simplified)
            query = command
            if "search for" in command.lower():
                query = command.lower().split("search for")[1].strip()
            elif "find" in command.lower():
                query = command.lower().split("find")[1].strip()
            
            search_result = self.search_information(query)
            template = random.choice(self.response_templates["search_query"])
            response = template.format(topic=query)
        
        elif intent == "music_query":
            # Extract song name (simplified)
            song = "your requested song"
            if "play" in command.lower():
                parts = command.lower().split("play")
                if len(parts) > 1:
                    song = parts[1].strip()
            
            music_response = self.play_music(song)
            response = music_response
        
        elif intent == "navigation_query":
            # Extract destination (simplified)
            destination = "your destination"
            if "navigate to" in command.lower():
                destination = command.lower().split("navigate to")[1].strip()
            elif "directions to" in command.lower():
                destination = command.lower().split("directions to")[1].strip()
            
            navigation_response = self.navigate(destination)
            response = navigation_response
        
        elif intent == "help_query":
            template = random.choice(self.response_templates["help_query"])
            response = template
        
        elif intent == "exit_query":
            template = random.choice(self.response_templates["exit_query"])
            response = template
        
        else:
            # Check for similar previous commands
            similar_command = self.find_similar_command(command)
            if similar_command:
                # Find the response to the similar command
                for hist in self.command_history:
                    if hist['command'] == similar_command:
                        response = f"Similar to before: {hist['response']}"
                        break
            
            # If no similar command found, use unknown response
            if not response:
                template = random.choice(self.response_templates["unknown"])
                response = template
        
        # Update context with this interaction
        self.update_context(command, response)
        
        # Log the interaction to database if user is authenticated
        if self.user:
            try:
                VoiceCommand.objects.create(
                    user=self.user,
                    command_text=command,
                    response_text=response,
                    intent=intent,
                    entities=entities,
                    processing_time=0.0,  # In a real implementation, you'd measure this
                    success=True
                )
            except Exception as e:
                logger.error(f"Failed to log voice command: {e}")
        
        return response
    
    def get_conversation_summary(self) -> str:
        """
        Generate a summary of the current conversation.
        
        Returns:
            str: Conversation summary
        """
        if not self.command_history:
            return "No conversation history available."
        
        # Count intents
        intent_counts = defaultdict(int)
        for item in self.command_history:
            intent_counts[item['intent']] += 1
        
        # Generate summary
        total_commands = len(self.command_history)
        summary = f"Conversation Summary:\n"
        summary += f"- Total commands: {total_commands}\n"
        summary += f"- Session started: {self.command_history[0]['timestamp'].strftime('%Y-%m-%d %H:%M')}\n"
        summary += f"- Most common intent: {max(intent_counts, key=intent_counts.get) if intent_counts else 'None'}\n"
        
        return summary
    
    def reset_conversation(self):
        """
        Reset the conversation context.
        """
        self.command_history = []
        self.conversation_context = {}
        self.command_vectors = []
        self.command_texts = []
        logger.info("Conversation context reset")


# Example usage
if __name__ == "__main__":
    # Create an instance of the advanced voice assistant
    assistant = AdvancedVoiceAssistant()
    
    # Example commands
    test_commands = [
        "What time is it?",
        "What's the weather like in Paris?",
        "Tell me the latest news",
        "Remind me to call John in 30 minutes",
        "Calculate 25 times 4",
        "Search for artificial intelligence",
        "Play some jazz music",
        "Navigate to the nearest gas station",
        "Help me with this assistant",
        "Goodbye"
    ]
    
    # Process each command
    for command in test_commands:
        print(f"\nUser: {command}")
        response = assistant.generate_response(command)
        print(f"Assistant: {response}")
    
    # Print conversation summary
    print(f"\n{assistant.get_conversation_summary()}")