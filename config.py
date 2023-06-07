import os
from dotenv import load_dotenv

load_dotenv()

class Config():
    
    SQLALCHEMY_DATABASE_URI = os.getenv("DEV_SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False