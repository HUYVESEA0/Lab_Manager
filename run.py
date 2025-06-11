import os
from dotenv import load_dotenv

# Load environment variables first, before importing anything else
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
elif os.path.exists('.env'):
    load_dotenv()

from app import create_app

# Create the Flask app and SocketIO instance
app, socketio = create_app()

if __name__ == "__main__":
    socketio.run(app, debug=True, host='127.0.0.1', port=5000)
