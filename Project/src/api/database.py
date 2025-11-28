import os
from dotenv import load_dotenv
from supabase import create_client, Client

from flask import request

def get_supabase() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SECRET_KEY")
    return create_client(url, key)
