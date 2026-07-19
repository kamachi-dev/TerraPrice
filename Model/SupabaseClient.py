import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.environ["SUPABASE_URL"]
key = os.environ["SUPABASE_ANON_KEY"]


def get_client():
    return create_client(url, key)
