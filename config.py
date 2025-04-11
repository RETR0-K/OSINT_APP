import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    
    # API keys
    RAPIDAPI_KEY = os.environ.get('RAPIDAPI_KEY')  # The RapidAPI key for all breach APIs
    
    # OpenAI API key for AI analysis features
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///osint_tracker.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Email configuration for password resets (optional feature)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    