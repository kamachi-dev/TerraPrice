from psycopg2.extras import RealDictCursor
from .ConnectionInPostgre import MyConnection
import hashlib

def query_db(query, args=(), fetch=False, dictionary=False):
    conn = MyConnection(
        host="aws-0-ap-southeast-1.pooler.supabase.com",
        user="postgres.rgdisearlwcbmbvwrrli",
        password="TerraPrice@553431!",
        database="postgres",
        port=6543
    ).connect()

    cursor_factory = RealDictCursor if dictionary else None
    cursor = conn.cursor(cursor_factory=cursor_factory)

    cursor.execute(query, args)
    result = cursor.fetchall() if fetch else None

    conn.commit()
    cursor.close()
    conn.close()
    return result

def search_region(region):
    result = query_db("SELECT * FROM dataset WHERE admin1 = %s", (region,), fetch=True, dictionary=True)
    return [dict(row) for row in result]

def authenticate_user(username, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    result = query_db(
        'SELECT id, username, "isAdmin" FROM account WHERE username = %s AND password = %s',
        (username, hashed_password),
        fetch=True,
        dictionary=True
    )
    print("AUTH CALLED")
    print(result[0] if result else None)
    return result[0] if result else None

def create_user(username, password, is_admin=False):
    existing_user = query_db(
        "SELECT id FROM account WHERE username = %s",
        (username,),
        fetch=True,
        dictionary=True
    )
    
    if existing_user:
        return False, "Username already exists"
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    try:
        query_db(
            "INSERT INTO account (username, password) VALUES (%s, %s)",
            (username, hashed_password)
        )
        return True, "Account created successfully"
    except Exception as e:
        print(f"Error creating user: {e}")
        return False, "Failed to create account"

def get_categories():
    result = query_db("SELECT DISTINCT category FROM dataset ORDER BY category", fetch=True, dictionary=True)
    return [row['category'] for row in result]

def get_commodities_by_category(category):
    result = query_db(
        "SELECT DISTINCT commodity FROM dataset WHERE category = %s ORDER BY commodity",
        (category,),
        fetch=True,
        dictionary=True
    )
    return [row['commodity'] for row in result]

def get_all_datasets():
    result = query_db(
        "SELECT id, latitude, longitude, category, commodity, pricetype, price FROM dataset ORDER BY id DESC",
        fetch=True,
        dictionary=True
    )
    return [dict(row) for row in result]

def get_datasets_paginated(limit, offset):
    result = query_db(
        "SELECT id, latitude, longitude, category, commodity, pricetype, price FROM dataset ORDER BY id DESC LIMIT %s OFFSET %s",
        (limit, offset),
        fetch=True,
        dictionary=True
    )
    return [dict(row) for row in result]

def get_total_datasets_count():
    result = query_db(
        "SELECT COUNT(*) as count FROM dataset",
        fetch=True,
        dictionary=True
    )
    return result[0]['count'] if result else 0

def get_latest_datasets(limit=5):
    result = query_db(
        "SELECT id, latitude, longitude, category, commodity, pricetype, price FROM dataset ORDER BY id DESC LIMIT %s",
        (limit,),
        fetch=True,
        dictionary=True
    )
    return [dict(row) for row in result]

def add_dataset_entry(data):
    try:
        query_db(
            """INSERT INTO dataset (latitude, longitude, category, commodity, pricetype, price) 
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (data['latitude'], data['longitude'], data['category'], 
             data['commodity'], data['pricetype'], data['value'])
        )
        return True
    except Exception as e:
        print(f"Error adding dataset entry: {e}")
        return False
