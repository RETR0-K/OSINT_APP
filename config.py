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
    