"""
Simple Web Server for Voice Assistant Interface
"""

import http.server
import socketserver
import webbrowser
import os
import threading
import time

# Set the port for the web server
PORT = 8000

def start_web_server():
    """Start a simple web server to serve the voice assistant interface."""
    # Change to the voice_assistant directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Create a simple HTTP request handler
    Handler = http.server.SimpleHTTPRequestHandler
    
    try:
        # Create the server
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"Web server started at http://localhost:{PORT}")
            print("Available interfaces:")
            print(f"  - Basic interface: http://localhost:{PORT}/web_interface.html")
            print(f"  - Advanced interface: http://localhost:{PORT}/advanced_web_interface.html")
            print("Serving voice assistant interfaces...")
            print("Press Ctrl+C to stop the server")
            
            # Open the advanced browser interface automatically
            webbrowser.open(f"http://localhost:{PORT}/advanced_web_interface.html")
            
            # Start the server
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except Exception as e:
        print(f"Error starting server: {e}")

if __name__ == "__main__":
    start_web_server()