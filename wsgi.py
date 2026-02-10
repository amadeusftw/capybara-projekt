"""WSGI entry point for gunicorn."""
import os
from dotenv import load_dotenv

load_dotenv()

from app.app import app

if __name__ == "__main__":
    app.run()
