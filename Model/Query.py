from psycopg2.extras import RealDictCursor
from .ConnectionInPostgre import MyConnection

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
    return result
