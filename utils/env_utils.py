import os
from dotenv import load_dotenv

def load_env_variables():
    """Load environment variables from .env file."""
    load_dotenv()
    email = os.getenv("FB_EMAIL")
    password = os.getenv("FB_PASSWORD")
    if not email or not password:
        raise ValueError("Les variables d'environnement FB_EMAIL et FB_PASSWORD doivent être définies.")
    return email, password