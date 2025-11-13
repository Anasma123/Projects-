"""
Machine Learning Module for Intent Classification
"""
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.pipeline import Pipeline
import joblib
import logging
from typing import List, Dict, Tuple, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntentClassifier:
    """
    Machine Learning-based Intent Classifier for voice commands.
    """
    
    def __init__(self):
        """
        Initialize the Intent Classifier with multiple ML models.
        """
        self.models = {
            'naive_bayes': MultinomialNB(),
            'logistic_regression': LogisticRegression(random_state=42, max_iter=1000),
            'svm': SVC(probability=True, random_state=42),
            'random_forest': RandomForestClassifier(n_estimators=100, random_state=42)
        }
        
        self.pipelines = {}
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2),
            lowercase=True
        )
        
        self.is_trained = False
        self.best_model = None
        self.best_model_name = None
        
        # Default intent labels
        self.intent_labels = [
            'time_query',
            'weather_query', 
            'news_query',
            'reminder_query',
            'calculation_query',
            'search_query',
            'music_query',
            'navigation_query',
            'help_query',
            'exit_query',
            'unknown'
        ]
    
    def prepare_training_data(self) -> Tuple[List[str], List[str]]:
        """
        Prepare sample training data for intent classification.
        
        Returns:
            Tuple[List[str], List[str]]: Training texts and labels
        """
        # Sample training data - in a real application, this would come from a dataset
        training_data = [
            # Time queries
            ("what time is it", "time_query"),
            ("tell me the time", "time_query"),
            ("what's the current time", "time_query"),
            ("do you have the time", "time_query"),
            ("time please", "time_query"),
            ("what date is it", "time_query"),
            ("today's date", "time_query"),
            ("current date", "time_query"),
            
            # Weather queries
            ("what's the weather like", "weather_query"),
            ("how's the weather today", "weather_query"),
            ("weather forecast", "weather_query"),
            ("is it raining", "weather_query"),
            ("temperature outside", "weather_query"),
            ("weather in New York", "weather_query"),
            ("climate conditions", "weather_query"),
            ("sunny today", "weather_query"),
            
            # News queries
            ("what's in the news", "news_query"),
            ("latest headlines", "news_query"),
            ("current events", "news_query"),
            ("breaking news", "news_query"),
            ("news update", "news_query"),
            ("what's happening", "news_query"),
            ("today's news", "news_query"),
            ("news report", "news_query"),
            
            # Reminder queries
            ("remind me to call", "reminder_query"),
            ("set a reminder", "reminder_query"),
            ("alarm for tomorrow", "reminder_query"),
            ("schedule appointment", "reminder_query"),
            ("reminder for meeting", "reminder_query"),
            ("notify me later", "reminder_query"),
            ("set alarm", "reminder_query"),
            ("reminder notification", "reminder_query"),
            
            # Calculation queries
            ("calculate this", "calculation_query"),
            ("what is 2 plus 2", "calculation_query"),
            ("math problem", "calculation_query"),
            ("compute the result", "calculation_query"),
            ("solve equation", "calculation_query"),
            ("arithmetic operation", "calculation_query"),
            ("mathematical calculation", "calculation_query"),
            ("do the math", "calculation_query"),
            
            # Search queries
            ("search for information", "search_query"),
            ("find me details", "search_query"),
            ("look up", "search_query"),
            ("google search", "search_query"),
            ("browse the web", "search_query"),
            ("find on internet", "search_query"),
            ("web search", "search_query"),
            ("search online", "search_query"),
            
            # Music queries
            ("play some music", "music_query"),
            ("song request", "music_query"),
            ("music playback", "music_query"),
            ("stream music", "music_query"),
            ("play a song", "music_query"),
            ("music player", "music_query"),
            ("audio playback", "music_query"),
            ("listen to music", "music_query"),
            
            # Navigation queries
            ("navigate to", "navigation_query"),
            ("directions to", "navigation_query"),
            ("map route", "navigation_query"),
            ("find location", "navigation_query"),
            ("gps navigation", "navigation_query"),
            ("route planner", "navigation_query"),
            ("navigation system", "navigation_query"),
            ("get directions", "navigation_query"),
            
            # Help queries
            ("help me", "help_query"),
            ("what can you do", "help_query"),
            ("how does this work", "help_query"),
            ("instructions", "help_query"),
            ("user guide", "help_query"),
            ("support needed", "help_query"),
            ("assistance required", "help_query"),
            ("help documentation", "help_query"),
            
            # Exit queries
            ("goodbye", "exit_query"),
            ("exit application", "exit_query"),
            ("quit now", "exit_query"),
            ("stop assistant", "exit_query"),
            ("bye bye", "exit_query"),
            ("see you later", "exit_query"),
            ("farewell", "exit_query"),
            ("end session", "exit_query")
        ]
        
        texts, labels = zip(*training_data)
        return list(texts), list(labels)
    
    def train(self, texts: List[str] = None, labels: List[str] = None) -> Dict[str, float]:
        """
        Train all models and select the best one.
        
        Args:
            texts (List[str]): Training texts
            labels (List[str]): Training labels
            
        Returns:
            Dict[str, float]: Model accuracies
        """
        # Use sample data if none provided
        if texts is None or labels is None:
            texts, labels = self.prepare_training_data()
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            texts, labels, test_size=0.2, random_state=42, stratify=labels
        )
        
        # Vectorize texts
        X_train_vec = self.vectorizer.fit_transform(X_train)
        X_test_vec = self.vectorizer.transform(X_test)
        
        # Train and evaluate each model
        accuracies = {}
        
        for name, model in self.models.items():
            try:
                # Train model
                model.fit(X_train_vec, y_train)
                
                # Make predictions
                y_pred = model.predict(X_test_vec)
                
                # Calculate accuracy
                accuracy = accuracy_score(y_test, y_pred)
                accuracies[name] = accuracy
                
                # Create pipeline
                self.pipelines[name] = Pipeline([
                    ('vectorizer', self.vectorizer),
                    ('classifier', model)
                ])
                
                logger.info(f"{name} accuracy: {accuracy:.4f}")
                
            except Exception as e:
                logger.error(f"Error training {name}: {e}")
                accuracies[name] = 0.0
        
        # Select best model
        if accuracies:
            self.best_model_name = max(accuracies, key=accuracies.get)
            self.best_model = self.pipelines.get(self.best_model_name)
            logger.info(f"Best model: {self.best_model_name} with accuracy {accuracies[self.best_model_name]:.4f}")
        
        self.is_trained = True
        return accuracies
    
    def predict(self, text: str) -> Dict[str, float]:
        """
        Predict intent for a given text.
        
        Args:
            text (str): Input text
            
        Returns:
            Dict[str, float]: Predicted intents with probabilities
        """
        if not self.is_trained or self.best_model is None:
            logger.warning("Model not trained yet. Training with sample data...")
            self.train()
        
        if self.best_model is None:
            # Fallback to simple keyword matching
            return self._keyword_based_prediction(text)
        
        try:
            # Get prediction probabilities
            probabilities = self.best_model.predict_proba([text])[0]
            classes = self.best_model.named_steps['classifier'].classes_
            
            # Create intent-probability mapping
            intent_probs = dict(zip(classes, probabilities))
            
            # Sort by probability
            sorted_intents = {k: v for k, v in sorted(intent_probs.items(), key=lambda item: item[1], reverse=True)}
            
            return sorted_intents
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return self._keyword_based_prediction(text)
    
    def _keyword_based_prediction(self, text: str) -> Dict[str, float]:
        """
        Fallback method using keyword matching.
        
        Args:
            text (str): Input text
            
        Returns:
            Dict[str, float]: Predicted intents with confidence scores
        """
        text_lower = text.lower()
        
        # Keyword patterns for each intent
        intent_patterns = {
            'time_query': ['time', 'date', 'clock', 'hour', 'minute', 'second', 'day', 'today'],
            'weather_query': ['weather', 'temperature', 'climate', 'forecast', 'rain', 'sun', 'cloud'],
            'news_query': ['news', 'headline', 'update', 'current event', 'breaking'],
            'reminder_query': ['remind', 'reminder', 'alarm', 'schedule', 'appointment'],
            'calculation_query': ['calculate', 'compute', 'math', 'add', 'subtract', 'multiply', 'divide'],
            'search_query': ['search', 'find', 'look', 'google', 'browse'],
            'music_query': ['music', 'song', 'play', 'spotify', 'youtube'],
            'navigation_query': ['navigate', 'direction', 'map', 'route', 'location'],
            'help_query': ['help', 'assist', 'support', 'guide', 'instruction'],
            'exit_query': ['exit', 'quit', 'stop', 'bye', 'goodbye']
        }
        
        # Calculate scores based on keyword matches
        scores = {}
        total_matches = 0
        
        for intent, keywords in intent_patterns.items():
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            scores[intent] = matches
            total_matches += matches
        
        # Convert to probabilities
        if total_matches > 0:
            probabilities = {intent: score/total_matches for intent, score in scores.items()}
        else:
            # If no matches, assign equal probability to all intents
            probabilities = {intent: 1/len(intent_patterns) for intent in intent_patterns}
        
        # Sort by probability
        sorted_probs = {k: v for k, v in sorted(probabilities.items(), key=lambda item: item[1], reverse=True)}
        
        return sorted_probs
    
    def add_training_data(self, texts: List[str], labels: List[str]):
        """
        Add new training data to the classifier.
        
        Args:
            texts (List[str]): New training texts
            labels (List[str]): New training labels
        """
        # In a real implementation, you would retrain the model with new data
        # For now, we'll just log the addition
        logger.info(f"Added {len(texts)} new training samples")
    
    def save_model(self, filepath: str):
        """
        Save the trained model to disk.
        
        Args:
            filepath (str): Path to save the model
        """
        if self.best_model is None:
            logger.warning("No trained model to save")
            return
        
        try:
            joblib.dump({
                'model': self.best_model,
                'vectorizer': self.vectorizer,
                'is_trained': self.is_trained,
                'best_model_name': self.best_model_name
            }, filepath)
            logger.info(f"Model saved to {filepath}")
        except Exception as e:
            logger.error(f"Error saving model: {e}")
    
    def load_model(self, filepath: str):
        """
        Load a trained model from disk.
        
        Args:
            filepath (str): Path to load the model from
        """
        try:
            loaded_data = joblib.load(filepath)
            self.best_model = loaded_data['model']
            self.vectorizer = loaded_data['vectorizer']
            self.is_trained = loaded_data['is_trained']
            self.best_model_name = loaded_data['best_model_name']
            logger.info(f"Model loaded from {filepath}")
        except Exception as e:
            logger.error(f"Error loading model: {e}")


# Example usage
if __name__ == "__main__":
    # Create an instance of the intent classifier
    classifier = IntentClassifier()
    
    # Train the model
    print("Training intent classifier...")
    accuracies = classifier.train()
    print(f"Model accuracies: {accuracies}")
    
    # Test predictions
    test_commands = [
        "What time is it?",
        "How's the weather today?",
        "Tell me the latest news",
        "Remind me to call John",
        "Calculate 25 times 4",
        "Search for artificial intelligence",
        "Play some jazz music",
        "Navigate to the nearest gas station",
        "Help me with this assistant",
        "Goodbye"
    ]
    
    print("\nTesting predictions:")
    for command in test_commands:
        predictions = classifier.predict(command)
        top_intent = max(predictions, key=predictions.get)
        confidence = predictions[top_intent]
        print(f"Command: '{command}'")
        print(f"  Predicted intent: {top_intent} (confidence: {confidence:.4f})")
        print(f"  All predictions: {predictions}")
        print()