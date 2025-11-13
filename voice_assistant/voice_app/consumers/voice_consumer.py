import json
import base64
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from ai_modules.ai_assistant import AdvancedVoiceAssistant
from voice_app.models import VoiceCommand, SystemLog
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)

class VoiceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handle WebSocket connection."""
        # Accept the connection
        await self.accept()
        
        # Initialize the AI assistant
        self.assistant = AdvancedVoiceAssistant()
        
        # Log the connection
        await self.send_system_message("Connected to the voice assistant WebSocket server")
        logger.info("WebSocket connection established")

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        logger.info(f"WebSocket connection closed with code: {close_code}")

    async def receive(self, text_data=None, bytes_data=None):
        """Handle incoming WebSocket messages."""
        try:
            if text_data:
                # Parse the JSON data
                data = json.loads(text_data)
                message_type = data.get('type')
                
                if message_type == 'voice_data':
                    await self.handle_voice_data(data)
                elif message_type == 'text_command':
                    await self.handle_text_command(data)
                elif message_type == 'start_listening':
                    await self.start_listening()
                elif message_type == 'stop_listening':
                    await self.stop_listening()
                else:
                    await self.send_error("Unknown message type")
            else:
                await self.send_error("Invalid message format")
        except json.JSONDecodeError:
            await self.send_error("Invalid JSON format")
        except Exception as e:
            logger.error(f"Error processing WebSocket message: {str(e)}")
            await self.send_error(f"Error processing message: {str(e)}")

    async def handle_voice_data(self, data):
        """Handle incoming voice data."""
        try:
            # Extract audio data
            audio_data = data.get('audio_data')
            if not audio_data:
                await self.send_error("No audio data provided")
                return
            
            # Send processing status
            await self.send_status("Processing voice data...")
            
            # In a real implementation, you would:
            # 1. Decode the base64 audio data
            # 2. Process the audio with speech recognition
            # 3. Generate a response using the AI assistant
            # 4. Convert response to speech if needed
            # 5. Send the response back to the client
            
            # For this example, we'll simulate the process
            recognized_text = "what time is it"  # This would come from speech recognition
            response_text = self.assistant.generate_response(recognized_text)
            
            # Send the response
            await self.send_voice_response({
                'recognized_text': recognized_text,
                'response_text': response_text,
                'audio_response': ''  # This would be base64 encoded audio data
            })
            
            # Log the interaction
            await self.log_interaction(recognized_text, response_text)
            
        except Exception as e:
            logger.error(f"Error handling voice data: {str(e)}")
            await self.send_error(f"Error processing voice data: {str(e)}")

    async def handle_text_command(self, data):
        """Handle text command."""
        try:
            # Extract command
            command = data.get('command')
            if not command:
                await self.send_error("No command provided")
                return
            
            # Send processing status
            await self.send_status("Processing text command...")
            
            # Process the command with the AI assistant
            response_text = self.assistant.generate_response(command)
            
            # Send the response
            await self.send_text_response({
                'command': command,
                'response_text': response_text
            })
            
            # Log the interaction
            await self.log_interaction(command, response_text)
            
        except Exception as e:
            logger.error(f"Error handling text command: {str(e)}")
            await self.send_error(f"Error processing text command: {str(e)}")

    async def start_listening(self):
        """Start voice listening mode."""
        await self.send_status("Listening for voice input...")
        # In a real implementation, you would start the microphone or audio stream

    async def stop_listening(self):
        """Stop voice listening mode."""
        await self.send_status("Stopped listening")
        # In a real implementation, you would stop the microphone or audio stream

    async def send_system_message(self, message):
        """Send a system message to the client."""
        await self.send(text_data=json.dumps({
            'type': 'system_message',
            'message': message
        }))

    async def send_status(self, status):
        """Send a status update to the client."""
        await self.send(text_data=json.dumps({
            'type': 'status_update',
            'status': status
        }))

    async def send_error(self, error):
        """Send an error message to the client."""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'error': error
        }))

    async def send_voice_response(self, response_data):
        """Send voice response to the client."""
        response_data['type'] = 'voice_response'
        await self.send(text_data=json.dumps(response_data))

    async def send_text_response(self, response_data):
        """Send text response to the client."""
        response_data['type'] = 'text_response'
        await self.send(text_data=json.dumps(response_data))

    @sync_to_async
    def log_interaction(self, command, response):
        """Log the voice interaction to the database."""
        try:
            # In a real implementation, you would associate with the authenticated user
            # For now, we'll create without user association
            VoiceCommand.objects.create(
                command_text=command,
                response_text=response,
                intent="unknown",  # In a real implementation, you would extract the intent
                processing_time=0.0,  # In a real implementation, you would measure this
                success=True
            )
        except Exception as e:
            logger.error(f"Error logging interaction: {str(e)}")