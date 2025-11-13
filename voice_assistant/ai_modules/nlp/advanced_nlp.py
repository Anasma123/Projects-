"""
Advanced NLP Module for the AI Voice Assistant
"""
import spacy
import re
import logging
from typing import List, Dict, Tuple, Optional
from collections import Counter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedNLPProcessor:
    """
    Advanced NLP Processor with comprehensive linguistic analysis capabilities.
    """
    
    def __init__(self):
        """
        Initialize the Advanced NLP Processor.
        """
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.error("spaCy English model not found. Please install with: python -m spacy download en_core_web_sm")
            self.nlp = None
    
    def process_text(self, text: str) -> Dict:
        """
        Process text with comprehensive NLP analysis.
        
        Args:
            text (str): Input text
            
        Returns:
            Dict: Comprehensive analysis results
        """
        if not self.nlp:
            return {"error": "NLP model not loaded"}
        
        doc = self.nlp(text)
        
        # Extract various linguistic features
        analysis = {
            "text": text,
            "tokens": self._extract_tokens(doc),
            "lemmas": self._extract_lemmas(doc),
            "pos_tags": self._extract_pos_tags(doc),
            "named_entities": self._extract_named_entities(doc),
            "noun_chunks": self._extract_noun_chunks(doc),
            "sentences": self._extract_sentences(doc),
            "dependencies": self._extract_dependencies(doc),
            "similarity_scores": self._calculate_similarity_scores(doc),
            "readability_metrics": self._calculate_readability_metrics(doc),
            "key_phrases": self._extract_key_phrases(doc),
            "sentiment_cues": self._extract_sentiment_cues(doc)
        }
        
        return analysis
    
    def _extract_tokens(self, doc) -> List[str]:
        """Extract tokens from document."""
        return [token.text for token in doc if not token.is_space]
    
    def _extract_lemmas(self, doc) -> List[str]:
        """Extract lemmas from document."""
        return [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
    
    def _extract_pos_tags(self, doc) -> List[Tuple[str, str]]:
        """Extract part-of-speech tags."""
        return [(token.text, token.pos_) for token in doc]
    
    def _extract_named_entities(self, doc) -> List[Dict]:
        """Extract named entities."""
        entities = []
        for ent in doc.ents:
            entities.append({
                "text": ent.text,
                "label": ent.label_,
                "description": "",  # spacy.explain(ent.label_) if available
                "start": ent.start_char,
                "end": ent.end_char
            })
        return entities
    
    def _extract_noun_chunks(self, doc) -> List[str]:
        """Extract noun chunks."""
        return [chunk.text for chunk in doc.noun_chunks]
    
    def _extract_sentences(self, doc) -> List[str]:
        """Extract sentences."""
        return [sent.text.strip() for sent in doc.sents]
    
    def _extract_dependencies(self, doc) -> List[Dict]:
        """Extract syntactic dependencies."""
        dependencies = []
        for token in doc:
            dependencies.append({
                "text": token.text,
                "dep": token.dep_,
                "head": token.head.text,
                "children": [child.text for child in token.children]
            })
        return dependencies
    
    def _calculate_similarity_scores(self, doc) -> Dict:
        """Calculate similarity scores between sentences."""
        sentences = list(doc.sents)
        if len(sentences) < 2:
            return {}
        
        # Calculate similarity between first two sentences as an example
        sim_score = sentences[0].similarity(sentences[1]) if hasattr(sentences[0], 'similarity') else 0.0
        
        return {
            "sentence_similarity": sim_score,
            "total_sentences": len(sentences)
        }
    
    def _calculate_readability_metrics(self, doc) -> Dict:
        """Calculate readability metrics."""
        sentences = list(doc.sents)
        words = [token.text for token in doc if not token.is_punct and not token.is_space]
        
        if not sentences or not words:
            return {}
        
        # Simple readability metrics
        avg_sentence_length = len(words) / len(sentences)
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        return {
            "avg_sentence_length": avg_sentence_length,
            "avg_word_length": avg_word_length,
            "total_words": len(words),
            "total_sentences": len(sentences)
        }
    
    def _extract_key_phrases(self, doc) -> List[str]:
        """Extract key phrases using noun chunks and named entities."""
        key_phrases = []
        
        # Add noun chunks
        key_phrases.extend([chunk.text for chunk in doc.noun_chunks])
        
        # Add named entities
        key_phrases.extend([ent.text for ent in doc.ents])
        
        # Remove duplicates and return top phrases
        unique_phrases = list(set(key_phrases))
        return unique_phrases[:10]  # Return top 10
    
    def _extract_sentiment_cues(self, doc) -> List[Dict]:
        """Extract sentiment-related words and phrases."""
        sentiment_cues = []
        
        # Define sentiment-related POS patterns
        positive_patterns = ["good", "great", "excellent", "amazing", "wonderful", "fantastic"]
        negative_patterns = ["bad", "terrible", "awful", "horrible", "disgusting", "worst"]
        
        for token in doc:
            if token.text.lower() in positive_patterns:
                sentiment_cues.append({
                    "text": token.text,
                    "sentiment": "positive",
                    "position": token.i
                })
            elif token.text.lower() in negative_patterns:
                sentiment_cues.append({
                    "text": token.text,
                    "sentiment": "negative",
                    "position": token.i
                })
        
        return sentiment_cues
    
    def extract_intent_keywords(self, text: str) -> Dict[str, List[str]]:
        """
        Extract keywords that indicate user intent.
        
        Args:
            text (str): Input text
            
        Returns:
            Dict[str, List[str]]: Intent categories and their keywords
        """
        doc = self.nlp(text) if self.nlp else None
        if not doc:
            return {}
        
        intent_keywords = {
            "question_words": [],
            "action_verbs": [],
            "temporal_words": [],
            "modal_verbs": []
        }
        
        for token in doc:
            # Question words (wh-words)
            if token.tag_ in ["WDT", "WP", "WP$", "WRB"]:
                intent_keywords["question_words"].append(token.text)
            
            # Action verbs
            if token.pos_ == "VERB" and token.tag_ in ["VB", "VBD", "VBG", "VBN", "VBP", "VBZ"]:
                intent_keywords["action_verbs"].append(token.lemma_)
            
            # Temporal words
            if token.ent_type_ == "DATE" or token.ent_type_ == "TIME":
                intent_keywords["temporal_words"].append(token.text)
            
            # Modal verbs
            if token.tag_ == "MD":
                intent_keywords["modal_verbs"].append(token.text)
        
        return intent_keywords
    
    def analyze_text_structure(self, text: str) -> Dict:
        """
        Analyze the overall structure of the text.
        
        Args:
            text (str): Input text
            
        Returns:
            Dict: Text structure analysis
        """
        doc = self.nlp(text) if self.nlp else None
        if not doc:
            return {"error": "NLP model not loaded"}
        
        structure = {
            "paragraphs": len(text.split("\n\n")),
            "sentences": len(list(doc.sents)),
            "words": len([token for token in doc if not token.is_punct and not token.is_space]),
            "characters": len(text),
            "avg_sent_length": 0.0,
            "avg_word_length": 0.0
        }
        
        # Calculate averages
        if structure["sentences"] > 0:
            structure["avg_sent_length"] = float(structure["words"] / structure["sentences"])
        
        words = [token.text for token in doc if not token.is_punct and not token.is_space]
        if words:
            structure["avg_word_length"] = float(sum(len(word) for word in words) / len(words))
        
        return structure


# Example usage
if __name__ == "__main__":
    # Create an instance of the advanced NLP processor
    nlp_processor = AdvancedNLPProcessor()
    
    # Example text
    sample_text = "The quick brown fox jumps over the lazy dog. This is a sample sentence for NLP processing."
    
    # Process the text
    analysis = nlp_processor.process_text(sample_text)
    
    # Print results
    print("NLP Analysis Results:")
    print(f"Tokens: {analysis.get('tokens', [])}")
    print(f"Named Entities: {analysis.get('named_entities', [])}")
    print(f"Key Phrases: {analysis.get('key_phrases', [])}")