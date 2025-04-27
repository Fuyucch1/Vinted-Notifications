import sqlite3
from traceback import print_exc


def get_db_connection():
    conn = sqlite3.connect("vinted_notifications.db")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def create_sqlite_db():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Using proper foreign key relationship between items and queries
        cursor.execute("CREATE TABLE queries (id INTEGER PRIMARY KEY AUTOINCREMENT, query TEXT, last_item NUMERIC)")
        cursor.execute(
            "CREATE TABLE items (item NUMERIC, title TEXT, price NUMERIC, currency TEXT, timestamp NUMERIC, photo_url TEXT, query_id INTEGER, FOREIGN KEY(query_id) REFERENCES queries(id))")
        cursor.execute("CREATE TABLE allowlist (country TEXT)")
        # Add a parameters table
        cursor.execute("CREATE TABLE parameters (key TEXT, value TEXT)")
        # Telegram parameters
        cursor.execute("INSERT INTO parameters (key, value) VALUES (?, ?)", ("telegram_enabled", "False"))
        cursor.execute("INSERT INTO parameters (key, value) VALUES (?, ?)", ("telegram_token", ""))
        cursor.execute("INSERT INTO parameters (key, value) VALUES (?, ?)", ("telegram_chat_id", ""))
        cursor.execute("INSERT INTO parameters (key, value) VALUES (?, ?)", ("telegram_process_running", "False"))

        # RSS parameters
        cursor.execute("INSERT INTO parameters (key, value) VALUES (?, ?)", ("rss_enabled", "False"))
        cursor.execute("INSERT INTO parameters (key, value) VALUES (?, ?)", ("rss_port", "8080"))
        cursor.execute("INSERT INTO parameters (key, value) VALUES (?, ?)", ("rss_max_items", "100"))
        cursor.execute("INSERT INTO parameters (key, value) VALUES (?, ?)", ("rss_process_running", "False"))

        # Version of the bot
        cursor.execute("INSERT INTO parameters (key, value) VALUES (?, ?)", ("version", "1.0.0"))
        # GitHub URL
        cursor.execute("INSERT INTO parameters (key, value) VALUES (?, ?)",
                       ("github_url", "https://github.com/Fuyucch1/Vinted-Notifications"))

        # System parameters
        cursor.execute("INSERT INTO parameters (key, value) VALUES (?, ?)", ("items_per_query", "20"))
        cursor.execute("INSERT INTO parameters (key, value) VALUES (?, ?)", ("query_refresh_delay", "60"))

        # Proxy parameters
        cursor.execute("INSERT INTO parameters (key, value) VALUES (?, ?)", ("proxy_list", ""))
        cursor.execute("INSERT INTO parameters (key, value) VALUES (?, ?)", ("proxy_list_link", ""))
        cursor.execute("INSERT INTO parameters (key, value) VALUES (?, ?)", ("check_proxies", "False"))
        cursor.execute("INSERT INTO parameters (key, value) VALUES (?, ?)", ("last_proxy_check_time", "0"))

        conn.commit()
    except Exception:
        print_exc()
    finally:
        if conn:
            conn.close()


def is_item_in_db_by_id(id):
    conn = None
    try:
        conn = sqlite3.connect("vinted_notifications.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT() FROM items WHERE item=?", (id,))
        return cursor.fetchone()[0]
    except Exception:
        print_exc()
    finally:
        if conn:
            conn.close()


def get_last_timestamp(query_id):
    conn = None
    try:
        conn = sqlite3.connect("vinted_notifications.db")
        cursor = conn.cursor()
        cursor.execute("SELECT last_item FROM queries WHERE id=?", (query_id,))
        result = cursor.fetchone()
        if result:
            return result[0]
        return None
    except Exception:
        print_exc()
        return None
    finally:
        if conn:
            conn.close()


def update_last_timestamp(query_id, timestamp):
    conn = None
    try:
        conn = sqlite3.connect("vinted_notifications.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE queries SET last_item=? WHERE id=?", (timestamp, query_id))
        conn.commit()
    except Exception:
        print_exc()
    finally:
        if conn:
            conn.close()


def add_item_to_db(id, title, query_id, price, timestamp, photo_url, currency="EUR"):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Insert into db the id and the query_id related to the item
        cursor.execute(
            "INSERT INTO items (item, title, price, currency, timestamp, photo_url, query_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (id, title, price, currency, timestamp, photo_url, query_id))
        # Update the last item for the query
        cursor.execute("UPDATE queries SET last_item=? WHERE id=?", (timestamp, query_id))
        conn.commit()
    except Exception:
        print_exc()
    finally:
        if conn:
            conn.close()

def get_queries():
    conn = None
    try:
        conn = sqlite3.connect("vinted_notifications.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, query, last_item FROM queries")
        return cursor.fetchall()
    except Exception:
        print_exc()
    finally:
        if conn:
            conn.close()


def is_query_in_db(processed_query):
    conn = None
    try:
        conn = sqlite3.connect("vinted_notifications.db")
        cursor = conn.cursor()
        # replace spaces in searched_text by % to match any query containing the searched text

        cursor.execute("SELECT COUNT() FROM queries WHERE query = ?", (processed_query,))
        if cursor.fetchone()[0]:
            return True
        return False
    except Exception:
        print_exc()
        return False
    finally:
        if conn:
            conn.close()

def add_query_to_db(query):
    conn = None
    try:
        conn = sqlite3.connect("vinted_notifications.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO queries (query, last_item) VALUES (?, NULL)", (query,))
        conn.commit()
    except Exception:
        print_exc()
    finally:
        if conn:
            conn.close()

def remove_query_from_db(query_number):
    conn = None
    try:
        conn = sqlite3.connect("vinted_notifications.db")
        cursor = conn.cursor()
        # Get the query and its ID based on the row number
        query_string = f"SELECT id, query, rowid FROM (SELECT id, query, rowid, ROW_NUMBER() OVER (ORDER BY ROWID) rn FROM queries) t WHERE rn={query_number}"
        cursor.execute(query_string)
        query_result = cursor.fetchone()
        if query_result:
            query_id, query_text, rowid = query_result
            # Delete items associated with this query using query_id
            cursor.execute("DELETE FROM items WHERE query_id=?", (query_id,))
            # Delete the query
            cursor.execute("DELETE FROM queries WHERE ROWID=?", (rowid,))
            conn.commit()
    except Exception:
        print_exc()
    finally:
        if conn:
            conn.close()


def remove_all_queries_from_db():
    conn = None
    try:
        conn = sqlite3.connect("vinted_notifications.db")
        cursor = conn.cursor()
        # Delete all items first to maintain foreign key integrity
        cursor.execute("DELETE FROM items")
        # Then delete all queries
        cursor.execute("DELETE FROM queries")
        conn.commit()
    except Exception:
        print_exc()
    finally:
        if conn:
            conn.close()


def add_to_allowlist(country):
    conn = None
    try:
        conn = sqlite3.connect("vinted_notifications.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO allowlist VALUES (?)", (country,))
        conn.commit()
    except Exception:
        print_exc()
    finally:
        if conn:
            conn.close()

def remove_from_allowlist(country):
    conn = None
    try:
        conn = sqlite3.connect("vinted_notifications.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM allowlist WHERE country=?", (country,))
        conn.commit()
    except Exception:
        print_exc()
    finally:
        if conn:
            conn.close()

def get_allowlist():
    conn = None
    try:
        conn = sqlite3.connect("vinted_notifications.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM allowlist")
        # Get list of countries
        countries = [country[0] for country in cursor.fetchall()]
        # Return 0 if there are no countries in the allowlist
        if not countries:
            return 0
        return countries
    finally:
        if conn:
            conn.close()


def clear_allowlist():
    conn = None
    try:
        conn = sqlite3.connect("vinted_notifications.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM allowlist")
        conn.commit()
    except Exception:
        print_exc()
    finally:
        if conn:
            conn.close()


def get_parameter(key):
    conn = None
    try:
        conn = sqlite3.connect("vinted_notifications.db")
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM parameters WHERE key=?", (key,))
        result = cursor.fetchone()
        return result[0] if result else None
    except Exception:
        print_exc()
    finally:
        if conn:
            conn.close()


def set_parameter(key, value):
    conn = None
    try:
        conn = sqlite3.connect("vinted_notifications.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE parameters SET value=? WHERE key=?", (value, key))
        conn.commit()
    except Exception:
        print_exc()
    finally:
        if conn:
            conn.close()


def get_all_parameters():
    conn = None
    try:
        conn = sqlite3.connect("vinted_notifications.db")
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM parameters")
        return {row[0]: row[1] for row in cursor.fetchall()}
    except Exception:
        print_exc()
        return {}
    finally:
        if conn:
            conn.close()


def get_items(limit=50, query=None):
    conn = None
    try:
        conn = sqlite3.connect("vinted_notifications.db")
        cursor = conn.cursor()
        if query:
            # Get the query_id for the given query
            cursor.execute("SELECT id FROM queries WHERE query=?", (query,))
            result = cursor.fetchone()
            if result:
                query_id = result[0]
                # Get items with the matching query_id
                cursor.execute(
                    "SELECT i.item, i.title, i.price, i.currency, i.timestamp, q.query, i.photo_url FROM items i JOIN queries q ON i.query_id = q.id WHERE i.query_id=? ORDER BY i.timestamp DESC LIMIT ?",
                    (query_id, limit))
            else:
                return []
        else:
            # Join with queries table to get the query text
            cursor.execute(
                "SELECT i.item, i.title, i.price, i.currency, i.timestamp, q.query, i.photo_url FROM items i JOIN queries q ON i.query_id = q.id ORDER BY i.timestamp DESC LIMIT ?",
                (limit,))
        return cursor.fetchall()
    except Exception:
        print_exc()
        return []
    finally:
        if conn:
            conn.close()


def get_total_items_count():
    conn = None
    try:
        conn = sqlite3.connect("vinted_notifications.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM items")
        return cursor.fetchone()[0]
    except Exception:
        print_exc()
        return 0
    finally:
        if conn:
            conn.close()


def get_total_queries_count():
    conn = None
    try:
        conn = sqlite3.connect("vinted_notifications.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM queries")
        return cursor.fetchone()[0]
    except Exception:
        print_exc()
        return 0
    finally:
        if conn:
            conn.close()


def get_last_found_item():
    conn = None
    try:
        conn = sqlite3.connect("vinted_notifications.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT i.item, i.title, i.price, i.currency, i.timestamp, q.query, i.photo_url FROM items i JOIN queries q ON i.query_id = q.id ORDER BY i.timestamp DESC LIMIT 1")
        return cursor.fetchone()
    except Exception:
        print_exc()
        return None
    finally:
        if conn:
            conn.close()


def get_items_per_day():
    conn = None
    try:
        conn = sqlite3.connect("vinted_notifications.db")
        cursor = conn.cursor()

        # Get total items
        cursor.execute("SELECT COUNT(*) FROM items")
        total_items = cursor.fetchone()[0]

        if total_items == 0:
            return 0

        # Get earliest and latest timestamps
        cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM items")
        min_timestamp, max_timestamp = cursor.fetchone()

        # Calculate number of days (add 1 to include both start and end days)
        import datetime
        min_date = datetime.datetime.fromtimestamp(min_timestamp).date()
        max_date = datetime.datetime.fromtimestamp(max_timestamp).date()
        days_diff = (max_date - min_date).days + 1

        # Ensure at least 1 day to avoid division by zero
        days_diff = max(1, days_diff)

        # Calculate items per day
        return round(total_items / days_diff, 1)
    except Exception:
        print_exc()
        return 0
    finally:
        if conn:
            conn.close()
