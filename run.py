from app import create_app

# Create the Flask app and SocketIO instance
app, socketio = create_app()

if __name__ == "__main__":
    socketio.run(app, debug=True, host='127.0.0.1', port=5000)
