"""
Advanced Voice Processing Module for the AI Assistant
"""
import speech_recognition as sr
import pyttsx3
import pyaudio
import wave
import numpy as np
import logging
from typing import Optional, Tuple
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceProcessor:
    """
    Advanced Voice Processor with speech recognition and text-to-speech capabilities.
    """
    
    def __init__(self):
        """
        Initialize the Voice Processor with recognition and synthesis engines.
        """
        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Initialize text-to-speech engine
        self.tts_engine = pyttsx3.init()
        
        # Configure TTS engine
        self._configure_tts()
        
        # Audio recording parameters
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.record_seconds = 5
        
        # Recording state
        self.is_recording = False
        self.audio_data = None
        
        # Adjust for ambient noise
        self._adjust_for_ambient_noise()
    
    def _configure_tts(self):
        """
        Configure the text-to-speech engine properties.
        """
        try:
            # Set voice properties
            voices = self.tts_engine.getProperty('voices')
            if voices:
                # Use the first available voice
                self.tts_engine.setProperty('voice', voices[0].id)
            
            # Set speech rate (words per minute)
            self.tts_engine.setProperty('rate', 150)
            
            # Set volume level (0.0 to 1.0)
            self.tts_engine.setProperty('volume', 0.9)
            
            logger.info("TTS engine configured successfully")
        except Exception as e:
            logger.error(f"Error configuring TTS engine: {e}")
    
    def _adjust_for_ambient_noise(self):
        """
        Adjust the recognizer for ambient noise.
        """
        try:
            logger.info("Adjusting for ambient noise...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            logger.info("Ambient noise adjustment completed")
        except Exception as e:
            logger.error(f"Error adjusting for ambient noise: {e}")
    
    def listen(self, timeout: Optional[float] = None, phrase_time_limit: Optional[float] = None) -> Optional[str]:
        """
        Listen for voice input and convert to text.
        
        Args:
            timeout (Optional[float]): Maximum time to wait for phrase start
            phrase_time_limit (Optional[float]): Maximum time for phrase duration
            
        Returns:
            Optional[str]: Recognized text or None if recognition failed
        """
        try:
            logger.info("Listening for voice input...")
            with self.microphone as source:
                # Listen for audio with timeout
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            
            logger.info("Processing audio...")
            # Use Google Speech Recognition
            text = self.recognizer.recognize_google(audio)
            logger.info(f"Recognized: {text}")
            return text.lower()
            
        except sr.WaitTimeoutError:
            logger.warning("Listening timed out")
            return None
        except sr.UnknownValueError:
            logger.warning("Could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Could not request results from speech recognition service: {e}")
            return None
        except Exception as e:
            logger.error(f"Error in listening: {e}")
            return None
    
    def speak(self, text: str, wait: bool = True) -> bool:
        """
        Convert text to speech.
        
        Args:
            text (str): Text to be spoken
            wait (bool): Whether to wait for speech to complete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"Speaking: {text}")
            print(f"Assistant: {text}")
            
            if wait:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            else:
                self.tts_engine.say(text)
                self.tts_engine.startLoop(False)
                # Run in separate thread to avoid blocking
                threading.Thread(target=self._run_tts_loop).start()
            
            return True
        except Exception as e:
            logger.error(f"Error in text-to-speech: {e}")
            return False
    
    def _run_tts_loop(self):
        """
        Run TTS engine loop in separate thread.
        """
        try:
            time.sleep(0.1)  # Small delay
            self.tts_engine.endLoop()
        except Exception as e:
            logger.error(f"Error in TTS loop: {e}")
    
    def record_audio(self, filename: str, duration: int = 5) -> bool:
        """
        Record audio to a file.
        
        Args:
            filename (str): Output filename
            duration (int): Recording duration in seconds
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"Recording audio for {duration} seconds...")
            
            # Initialize PyAudio
            audio = pyaudio.PyAudio()
            
            # Open stream
            stream = audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )
            
            frames = []
            
            # Record audio
            for i in range(0, int(self.rate / self.chunk * duration)):
                data = stream.read(self.chunk)
                frames.append(data)
            
            # Stop and close stream
            stream.stop_stream()
            stream.close()
            audio.terminate()
            
            # Save audio to file
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(audio.get_sample_size(self.format))
                wf.setframerate(self.rate)
                wf.writeframes(b''.join(frames))
            
            logger.info(f"Audio recorded and saved to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error recording audio: {e}")
            return False
    
    def analyze_audio_quality(self, audio_data) -> Dict[str, float]:
        """
        Analyze the quality of audio data.
        
        Args:
            audio_data: Audio data from speech recognition
            
        Returns:
            Dict[str, float]: Audio quality metrics
        """
        try:
            # Convert audio data to numpy array for analysis
            if hasattr(audio_data, 'get_raw_data'):
                raw_data = audio_data.get_raw_data()
                audio_array = np.frombuffer(raw_data, dtype=np.int16)
            else:
                # Assume it's already a numpy array
                audio_array = np.array(audio_data)
            
            # Calculate metrics
            metrics = {
                'amplitude_mean': float(np.mean(np.abs(audio_array))),
                'amplitude_max': float(np.max(np.abs(audio_array))),
                'amplitude_std': float(np.std(audio_array)),
                'duration_seconds': len(audio_array) / 44100.0,  # Assuming 44.1kHz sample rate
                'zero_crossing_rate': float(np.mean(np.abs(np.diff(np.sign(audio_array))))),
            }
            
            # Assess quality based on metrics
            if metrics['amplitude_max'] < 100:
                metrics['quality'] = 'poor'
            elif metrics['amplitude_max'] < 1000:
                metrics['quality'] = 'fair'
            else:
                metrics['quality'] = 'good'
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error analyzing audio quality: {e}")
            return {'error': str(e)}
    
    def set_voice_properties(self, rate: Optional[int] = None, volume: Optional[float] = None, voice_id: Optional[int] = None):
        """
        Set voice properties for text-to-speech.
        
        Args:
            rate (Optional[int]): Speech rate in words per minute
            volume (Optional[float]): Volume level (0.0 to 1.0)
            voice_id (Optional[int]): Voice ID to use
        """
        try:
            if rate is not None:
                self.tts_engine.setProperty('rate', rate)
            
            if volume is not None:
                self.tts_engine.setProperty('volume', volume)
            
            if voice_id is not None:
                voices = self.tts_engine.getProperty('voices')
                if 0 <= voice_id < len(voices):
                    self.tts_engine.setProperty('voice', voices[voice_id].id)
            
            logger.info("Voice properties updated")
        except Exception as e:
            logger.error(f"Error setting voice properties: {e}")
    
    def get_available_voices(self) -> List[Dict[str, str]]:
        """
        Get list of available voices.
        
        Returns:
            List[Dict[str, str]]: List of available voices with their properties
        """
        try:
            voices = self.tts_engine.getProperty('voices')
            voice_list = []
            
            for i, voice in enumerate(voices):
                voice_info = {
                    'id': i,
                    'name': voice.name,
                    'languages': voice.languages,
                    'gender': getattr(voice, 'gender', 'unknown')
                }
                voice_list.append(voice_info)
            
            return voice_list
        except Exception as e:
            logger.error(f"Error getting available voices: {e}")
            return []
    
    def is_speech_detected(self, threshold: int = 1000) -> bool:
        """
        Detect if speech is present in the current audio environment.
        
        Args:
            threshold (int): Amplitude threshold for speech detection
            
        Returns:
            bool: True if speech detected, False otherwise
        """
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=1)
                # Convert to numpy array
                raw_data = audio.get_raw_data()
                audio_array = np.frombuffer(raw_data, dtype=np.int16)
                # Check if amplitude exceeds threshold
                return np.max(np.abs(audio_array)) > threshold
        except Exception as e:
            logger.error(f"Error detecting speech: {e}")
            return False


# Example usage
if __name__ == "__main__":
    # Create an instance of the voice processor
    voice_processor = VoiceProcessor()
    
    # Get available voices
    voices = voice_processor.get_available_voices()
    print(f"Available voices: {len(voices)}")
    for voice in voices:
        print(f"  - {voice['name']} ({voice['languages']})")
    
    # Example: Speak some text
    voice_processor.speak("Hello, I am your advanced AI voice assistant.")
    
    # Example: Listen for voice input (uncomment to test)
    # print("Please say something...")
    # recognized_text = voice_processor.listen(timeout=5, phrase_time_limit=10)
    # if recognized_text:
    #     print(f"You said: {recognized_text}")
    #     voice_processor.speak(f"You said: {recognized_text}")
    
    # Example: Record audio (uncomment to test)
    # voice_processor.record_audio("test_recording.wav", duration=5)