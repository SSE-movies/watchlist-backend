import os
from dotenv import load_dotenv

load_dotenv()



class Config:
    PORT = int(os.getenv("PORT", 80))
    DATABASE_URL = os.getenv("DATABASE_URL")
    DEBUG = os.getenv("DEBUG", "False") == "True"
