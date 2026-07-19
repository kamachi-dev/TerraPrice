from .SupabaseClient import get_client, get_service_client


def search_region(region):
    client = get_client()
    result = client.table("dataset").select("*").eq("admin1", region).execute()
    return result.data


def authenticate_user(email, password):
    client = get_client()
    try:
        session = client.auth.sign_in_with_password({"email": email, "password": password})
        user = session.user
        profile_result = client.table("profiles").select("*").eq("id", user.id).execute()
        profile = profile_result.data[0] if profile_result.data else None
        return {
            "id": user.id,
            "email": user.email,
            "username": profile["username"] if profile else user.email.split("@")[0],
            "isAdmin": profile["role"] == "admin" if profile else False,
            "access_token": session.session.access_token,
            "refresh_token": session.session.refresh_token,
        }
    except Exception as e:
        print(f"Auth error: {e}")
        return None


def create_user(email, password, username):
    client = get_client()
    try:
        session = client.auth.sign_up({
            "email": email,
            "password": password,
            "options": {"data": {"username": username}},
        })
        if session.user:
            return True, "Account created successfully"
        return True, "Account created. Check your email for confirmation."
    except Exception as e:
        error_msg = str(e)
        if "already registered" in error_msg.lower() or "already exists" in error_msg.lower():
            return False, "Email already registered"
        if "rate limit" in error_msg.lower():
            return False, "Too many attempts. Please wait a moment and try again."
        if "invalid" in error_msg.lower() and "email" in error_msg.lower():
            return False, "Please enter a valid email address"
        print(f"Registration error: {e}")
        return False, f"Failed to create account: {error_msg}"


def get_profile(user_id):
    client = get_client()
    result = client.table("profiles").select("*").eq("id", user_id).execute()
    return result.data[0] if result.data else None


def get_categories():
    client = get_client()
    result = client.table("dataset").select("category").execute()
    categories = set()
    for row in result.data:
        if row.get("category"):
            categories.add(row["category"])
    return sorted(categories)


def get_commodities_by_category(category):
    client = get_client()
    result = client.table("dataset").select("commodity").eq("category", category).execute()
    commodities = set()
    for row in result.data:
        if row.get("commodity"):
            commodities.add(row["commodity"])
    return sorted(commodities)


def get_all_datasets():
    client = get_client()
    result = client.table("dataset").select("id, latitude, longitude, category, commodity, pricetype, price").order("id", desc=True).execute()
    return result.data


def get_datasets_paginated(limit, offset):
    client = get_client()
    result = client.table("dataset").select("id, latitude, longitude, category, commodity, pricetype, price").order("id", desc=True).range(offset, offset + limit - 1).execute()
    return result.data


def get_total_datasets_count():
    client = get_client()
    result = client.table("dataset").select("id", count="exact").execute()
    return result.count if hasattr(result, 'count') and result.count else 0


def get_latest_datasets(limit=5):
    client = get_client()
    result = client.table("dataset").select("id, latitude, longitude, category, commodity, pricetype, price").order("id", desc=True).limit(limit).execute()
    return result.data


def add_dataset_entry(data, user_id=None):
    client = get_client()
    try:
        payload = {
            "latitude": data["latitude"],
            "longitude": data["longitude"],
            "category": data["category"],
            "commodity": data["commodity"],
            "pricetype": data["pricetype"],
            "price": data["value"],
        }
        if user_id:
            payload["user_id"] = user_id
        client.table("dataset").insert(payload).execute()
        return True
    except Exception as e:
        print(f"Error adding dataset entry: {e}")
        return False
