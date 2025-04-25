import os
import random
import string
from dotenv import load_dotenv
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DB_URL = f"postgres://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
DB_CONNECTIONS = {
    "default": DB_URL,
}

SECRET_KEY = os.getenv("SECRET_KEY", default="".join(random.choices(string.ascii_letters + string.digits, k=32)))
CLIENT_ID = os.getenv("CLIENT_ID", default="".join(random.choices(string.ascii_letters + string.digits, k=32)))

MODE = os.getenv("MODE", default="development")

ROOT_PATH = os.getenv("ROOT_PATH", default="/account")