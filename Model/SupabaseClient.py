import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.environ["SUPABASE_URL"]
key = os.environ["SUPABASE_ANON_KEY"]

# This project's GoTrue service doesn't support the 2024-01-01 API version header
import supabase_auth._sync.gotrue_base_api as gotrue_api
gotrue_api.API_VERSIONS_2024_01_01_NAME = ""


def get_client():
    return create_client(url, key)


def get_service_client():
    service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", key)
    return create_client(url, service_key)
