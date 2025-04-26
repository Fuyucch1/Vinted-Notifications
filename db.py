import sqlite3
from traceback import print_exc


def create_sqlite_db():
    conn = None
    try:
        conn = sqlite3.connect("vinted_notifications.db")
        cursor = conn.cursor()
        # I'm not respecting normal forms yet, but I will, I promise
        cursor.execute("CREATE TABLE items (item NUMERIC, price NUMERIC, timestamp NUMERIC, query TEXT)")
        cursor.execute("CREATE TABLE queries (query TEXT, last_item NUMERIC)")
        cursor.execute("CREATE TABLE allowlist (country TEXT)")
        # Add a parameters table
        cursor.execute("CREATE TABLE parameters (key TEXT, value TEXT)")
        # Add desired keys to the parameters table
        cursor.execute("INSERT INTO parameters (key, value) VALUES (?, ?)", ("telegram_enabled", "False"))
        cursor.execute("INSERT INTO parameters (key, value) VALUES (?, ?)", ("telegram_token", ""))
        cursor.execute("INSERT INTO parameters (key, value) VALUES (?, ?)", ("telegram_chat_id", ""))
        cursor.execute("INSERT INTO parameters (key, value) VALUES (?, ?)", ("rss_enabled", "False"))
        cursor.execute("INSERT INTO parameters (key, value) VALUES (?, ?)", ("rss_port", "8080"))
        cursor.execute("INSERT INTO parameters (key, value) VALUES (?, ?)", ("rss_max_items", "100"))
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


def get_last_timestamp(query):
    conn = None
    try:
        conn = sqlite3.connect("vinted_notifications.db")
        cursor = conn.cursor()
        cursor.execute("SELECT last_item FROM queries WHERE query=?", (query,))
        return cursor.fetchone()[0]
    except Exception:
        print_exc()
    finally:
        if conn:
            conn.close()


def update_last_timestamp(query, timestamp):
    conn = None
    try:
        conn = sqlite3.connect("vinted_notifications.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE queries SET last_item=? WHERE query=?", (timestamp, query))
        conn.commit()
    except Exception:
        print_exc()
    finally:
        if conn:
            conn.close()


def add_item_to_db(id, query, price, timestamp):
    conn = None
    try:
        conn = sqlite3.connect("vinted_notifications.db")
        cursor = conn.cursor()
        # Insert into db the id and the query related to the item
        cursor.execute("INSERT INTO items VALUES (?, ?, ?, ?)", (id, price, timestamp, query))
        # Update the last item for the query
        cursor.execute("UPDATE queries SET last_item=? WHERE query=?", (timestamp, query))
        conn.commit()
    except Exception:
        print_exc()
    finally:
        if conn:
            conn.close()

def clean_db():
    conn = None
    # We clean the db by doing two processes :
    # First, we remove all the items that are too old (we keep the last 100 per query)
    # Then, we remove all lines in the items table that do not match any query in the queries table
    # This should lead to no deletion, but let's keep it safe

    # Get all the queries
    queries = get_queries()
    # For each query we keep the last 100 items
    for query in queries:
        conn = sqlite3.connect("vinted_notifications.db")
        cursor = conn.cursor()
        cursor.execute("SELECT item FROM items WHERE query=? ORDER BY ROWID DESC LIMIT -1 OFFSET 100", (query[0],))
        items = cursor.fetchall()
        for item in items:
            cursor.execute("DELETE FROM items WHERE item=?", (item[0],))
            conn.commit()
        conn.close()

    # Remove all items that do not match any query
    conn = sqlite3.connect("vinted_notifications.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM items WHERE query NOT IN (SELECT query FROM queries)")
    conn.commit()
    conn.close()

def get_queries():
    conn = None
    try:
        conn = sqlite3.connect("vinted_notifications.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM queries")
        return cursor.fetchall()
    except Exception:
        print_exc()
    finally:
        if conn:
            conn.close()

def is_query_in_db(searched_text):
    conn = None
    try:
        conn = sqlite3.connect("vinted_notifications.db")
        cursor = conn.cursor()
        # replace spaces in searched_text by % to match any query containing the searched text
        searched_text = searched_text.replace(' ', '+')

        cursor.execute("SELECT COUNT() FROM queries WHERE query LIKE ?", ('%'+searched_text+'%',))
        if cursor.fetchone()[0]:
            return True
    except Exception:
        print_exc()
    finally:
        if conn:
            conn.close()

def add_query_to_db(query):
    conn = None
    try:
        conn = sqlite3.connect("vinted_notifications.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO queries (query) VALUES (?)", (query,))
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
        query_string = f"SELECT query, rowid FROM (SELECT query, rowid, ROW_NUMBER() OVER (ORDER BY ROWID) rn FROM queries) t WHERE rn={query_number}"
        cursor.execute(query_string)
        query = cursor.fetchone()
        cursor.execute("DELETE FROM queries WHERE ROWID=?", (query[1],))
        cursor.execute("DELETE FROM items WHERE query=?", (query[0],))
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
        cursor.execute("DELETE FROM queries")
        cursor.execute("DELETE FROM items")
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
