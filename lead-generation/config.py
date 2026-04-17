import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    DEBUG = os.environ.get('FLASK_DEBUG', False)

    # Directories
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    RAW_DATA_DIR = os.path.join(BASE_DIR, 'data', 'raw')
    INTERIM_DATA_DIR = os.path.join(BASE_DIR, 'data', 'interim')
    PROCESSED_DATA_DIR = os.path.join(BASE_DIR, 'data', 'processed')

    # API Keys
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

    # Gmail Configuration
    GMAIL_CREDENTIALS_PATH = os.path.join(BASE_DIR, 'credentials.json')
    GMAIL_TOKEN_PATH = 'token.pickle'
    GMAIL_SCOPES = ['']

    # Search Configuration
    MAX_SEARCH_RESULTS = 50
    SEARCH_TIMEOUT = 10

    # Database Configuration (if needed)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Email Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', True)
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    # Other configurations from your src scripts
    WEBSITE_DATA_PATH = os.environ.get('WEBSITE_DATA_PATH', 'data/website_data.json')
    PARSED_DATA_PATH = os.environ.get('PARSED_DATA_PATH', 'data/parsed_data.json')
