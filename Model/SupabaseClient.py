import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.environ["SUPABASE_URL"]
key = os.environ["SUPABASE_ANON_KEY"]


def get_client():
    return create_client(url, key)


def get_service_client():
    service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", key)
    return create_client(url, service_key)
