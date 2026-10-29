import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    FLASK_DEBUG = os.environ.get("FLASK_DEBUG", "False") == "True"
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash")

    @staticmethod
    def validate():
        missing = []

        if not Config.SECRET_KEY:
            missing.append("SECRET_KEY")

        if not Config.SQLALCHEMY_DATABASE_URI:
            missing.append("DATABASE_URL")

        if missing:
            raise RuntimeError(
                f"Missing required environment variable(s): {', '.join(missing)}.\n"
                "Did you create a .env file from .env.example?"
            )