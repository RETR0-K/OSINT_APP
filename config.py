import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    
    # API keys
    HAVEIBEENPWNED_API_KEY = os.environ.get('HAVEIBEENPWNED_API_KEY')
    DEHASHED_API_KEY = os.environ.get('DEHASHED_API_KEY')
    BREACHDIRECTORY_API_KEY = os.environ.get('BREACHDIRECTORY_API_KEY')
    
    # OpenAI API key for AI analysis features
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # Database configuration (if needed later)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///osint.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False