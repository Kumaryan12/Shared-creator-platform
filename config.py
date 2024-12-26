# config.py

import os

class Config:
    SECRET_KEY = os.environ.get('eaf5e2d8e91f3e45c921e3a3f1d7250c') or 'your_secret_key'
    
    SQLALCHEMY_DATABASE_URI = 'sqlite:///platform.db'  # SQLite database
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable overhead tracking
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable tracking modifications
    WTF_CSRF_ENABLED = False