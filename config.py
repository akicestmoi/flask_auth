import os
from dotenv import load_dotenv

load_dotenv()

class Config():
    
    SQLALCHEMY_DATABASE_URI: str | None = os.getenv("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SESSION_TYPE: str = os.getenv("SESSION_TYPE")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    LOGIN_DISABLED = False #This should be turned to True during Unit Testing