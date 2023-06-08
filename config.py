import os
from dotenv import load_dotenv

load_dotenv()

class Config():
    
    SQLALCHEMY_DATABASE_URI: str | None = os.getenv("DEV_SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False