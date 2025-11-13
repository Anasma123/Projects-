"""
Voice-Activated Personal Assistant Application
Run this file to start the voice assistant.
"""

def main():
    """
    Main function to run the voice assistant application.
    """
    print("=" * 60)
    print("VOICE-ACTIVATED PERSONAL ASSISTANT")
    print("=" * 60)
    print("Welcome to your personal voice assistant!")
    print("\nFeatures:")
    print("- Tell you the current time and date")
    print("- Check weather conditions")
    print("- Read the latest news headlines")
    print("- Set reminders for important tasks")
    print("\nInstructions:")
    print("1. Speak clearly when giving commands")
    print("2. Say 'help' to hear available commands")
    print("3. Say 'exit' or 'quit' to close the application")
    print("\nStarting assistant...")
    
    # Import here to avoid import issues
    from assistant import VoiceAssistant
    
    # Initialize and run the voice assistant
    assistant = VoiceAssistant()
    assistant.run()

if __name__ == "__main__":
    main()