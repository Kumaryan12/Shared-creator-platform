from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate


migrate = Migrate()


# Extensions
csrf = CSRFProtect()
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
socketio = SocketIO()

def create_app():
    # Create Flask app instance
    app = Flask(__name__)

    # Load configuration
    app.config.from_object('config.Config')

    # Initialize extensions
    csrf.init_app(app)  # Initialize CSRF protection
    db.init_app(app)    # Initialize SQLAlchemy
    bcrypt.init_app(app)  # Initialize bcrypt
    login_manager.init_app(app)  # Initialize Flask-Login
    socketio.init_app(app, cors_allowed_origins="*")  # Initialize Flask-SocketIO
    migrate.init_app(app, db)  # Add this after initializing the database (db)

    # User loader for Flask-Login
    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    from app.blueprints.auth.routes import auth as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    return app
