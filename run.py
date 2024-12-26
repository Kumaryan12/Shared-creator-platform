from app import create_app, db, socketio  # Import socketio for real-time chat

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create the database
    socketio.run(app, debug=True)  # Use socketio.run to enable real-time functionality
print(app.url_map)

from app import create_app

app = create_app()

if __name__ == "__main__":
    print(app.url_map)  # Prints all registered routes
    app.run(debug=True)
