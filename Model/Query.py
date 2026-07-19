from .SupabaseClient import get_client


def authenticate_user(email, password):
    client = get_client()
    try:
        session = client.auth.sign_in_with_password({"email": email, "password": password})
        user = session.user
        profile = client.table("profiles").select("*").eq("id", user.id).execute()
        row = profile.data[0] if profile.data else {}
        p = row if isinstance(row, dict) else {}
        return {
            "id": user.id,
            "email": user.email,
            "username": p.get("username", user.email.split("@")[0]),
            "isAdmin": p.get("role") == "admin",
        }
    except Exception as e:
        return {"_error": str(e)}


def create_user(email, password, username):
    client = get_client()
    try:
        session = client.auth.sign_up({
            "email": email,
            "password": password,
            "options": {"data": {"username": username}},
        })
        if session.user:
            try:
                client.rpc("confirm_user", {"user_email": email}).execute()
            except Exception:
                pass
            return True, "Account created successfully"
        return True, "Account created. Check your email for confirmation."
    except Exception as e:
        m = str(e)
        if "already registered" in m.lower():
            return False, "Email already registered"
        if "rate limit" in m.lower():
            return False, "Too many attempts. Please wait."
        return False, f"Registration failed: {m}"


def get_profile(user_id):
    client = get_client()
    r = client.table("profiles").select("*").eq("id", user_id).execute()
    return r.data[0] if r.data else None


def get_categories():
    client = get_client()
    r = client.table("dataset").select("category").execute()
    cats = set()
    for row in r.data:
        if row.get("category"):
            cats.add(row["category"])
    return sorted(cats)


def get_commodities_by_category(category):
    client = get_client()
    r = client.table("dataset").select("commodity").eq("category", category).execute()
    coms = set()
    for row in r.data:
        if row.get("commodity"):
            coms.add(row["commodity"])
    return sorted(coms)


def get_all_datasets():
    client = get_client()
    r = client.table("dataset").select("id, latitude, longitude, category, commodity, pricetype, price").order("id", desc=True).execute()
    return r.data


def get_datasets_paginated(limit, offset):
    client = get_client()
    r = client.table("dataset").select("id, latitude, longitude, category, commodity, pricetype, price").order("id", desc=True).range(offset, offset + limit - 1).execute()
    return r.data


def get_total_datasets_count():
    client = get_client()
    r = client.table("dataset").select("id", count="exact").execute()
    return r.count if hasattr(r, 'count') and r.count else 0


def get_latest_datasets(limit=5):
    client = get_client()
    r = client.table("dataset").select("id, latitude, longitude, category, commodity, pricetype, price").order("id", desc=True).limit(limit).execute()
    return r.data


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
