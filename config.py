import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev'
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/quiz'
    DEBUG = True
