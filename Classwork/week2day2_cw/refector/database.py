import psycopg
import os
from dotenv import load_dotenv
from psycopg.rows import dict_row

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the environment variables.")

def get_connection():
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)
        