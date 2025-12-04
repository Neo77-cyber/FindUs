import os
import subprocess
import time
import threading

def run_django():
    """Run Django development server"""
    print("🚀 Starting Django server...")
    os.system("python manage.py runserver")

def run_ngrok():
    """Run ngrok to expose the server"""
    time.sleep(3)  # Wait for Django to start
    print("🌐 Starting ngrok tunnel...")
    os.system("ngrok http 8000")

if __name__ == "__main__":
    print("🎯 Starting temporary public deployment...")
    
    # Start Django in a thread
    django_thread = threading.Thread(target=run_django)
    django_thread.daemon = True
    django_thread.start()
    
    # Start ngrok
    run_ngrok()