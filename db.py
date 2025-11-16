import sqlite3
from traceback import print_exc
import hashlib
import secrets
import time

DB_PATH = "./data/vinted_notifications.db"

### DB BASE FUNC ###

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def create_or_update_sqlite_db(db_path):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Using the sql script
        with open(db_path, "r", encoding="utf-8") as sql_file:
            sql_script = sql_file.read()
            cursor.executescript(sql_script)

        conn.commit()
    except Exception:
        print_exc()
    finally:
        if conn:
            conn.close()

### ITEMS FUNC ###

def is_item_in_db_by_id(id):
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT() FROM items WHERE item=?", (id,))
        if cursor.fetchone()[0]:
            return True
        return False
    except Exception:
        print_exc()
    finally:
        if conn:
            conn.close()

def get_last_timestamp(query_id):
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
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
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE queries SET last_item=? WHERE id=?", (timestamp, query_id)
        )
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
            (id, title, price, currency, timestamp, photo_url, query_id),
        )
        # Update the last item for the query
        cursor.execute(
            "UPDATE queries SET last_item=? WHERE id=?", (timestamp, query_id)
        )
        conn.commit()
    except Exception:
        print_exc()
    finally:
        if conn:
            conn.close()

def get_items_for_owner(owner_id, limit=50):
    """
    Return recent items whose query belongs to the given owner_id.

    Rows: (item, title, price, currency, timestamp, query, photo_url)
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT i.item,
                   i.title,
                   i.price,
                   i.currency,
                   i.timestamp,
                   q.query,
                   i.photo_url
            FROM items i
            JOIN queries q ON i.query_id = q.id
            WHERE q.owner_id = ?
            ORDER BY i.timestamp DESC
            LIMIT ?
            """,
            (owner_id, limit),
        )
        return cursor.fetchall()
    except Exception:
        print_exc()
        return []
    finally:
        if conn:
            conn.close()


### QUERIES FUNC ###

def get_queries():
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, query, last_item, query_name FROM queries")
        return cursor.fetchall()
    except Exception:
        print_exc()
    finally:
        if conn:
            conn.close()

def get_due_queries(now_ts=None):
    """
    Return enabled queries whose (last_run + delay) <= now_ts, or last_run IS NULL.
    Each row: (id, query, last_run, delay)
    """
    conn = None
    try:
        if now_ts is None:
            now_ts = int(time.time())
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, query, last_run, delay
            FROM queries
            WHERE enabled = 1
              AND (last_run IS NULL OR last_run + delay <= ?)
            """,
            (now_ts,),
        )
        return cursor.fetchall()
    except Exception:
        print_exc()
        return []
    finally:
        if conn:
            conn.close()

def update_last_run(query_id, timestamp=None):
    """
    Update the last_run timestamp for a query.
    """
    conn = None
    try:
        if timestamp is None:
            timestamp = int(time.time())
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE queries SET last_run = ? WHERE id = ?",
            (timestamp, query_id),
        )
        conn.commit()
    except Exception:
        print_exc()
    finally:
        if conn:
            conn.close()

def get_queries_for_user(user_id):
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, query, last_item, query_name, enabled, delay, owner_id "
            "FROM queries WHERE owner_id = ?",
            (user_id,),
        )
        return cursor.fetchall()
    except Exception:
        print_exc()
        return []
    finally:
        if conn:
            conn.close()

def get_queries_with_owner():
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT q.id,
                   q.query,
                   q.last_item,
                   q.query_name,
                   u.username AS owner_username,
                   q.delay,
                   q.owner_id
            FROM queries q
            LEFT JOIN users u ON q.owner_id = u.id
            """
        )
        return cursor.fetchall()
    except Exception:
        print_exc()
        return []
    finally:
        if conn:
            conn.close()

def get_enabled_queries():
    """
    Return only enabled queries as (id, query) or with minimal fields used by the scraper.
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, query FROM queries WHERE enabled = 1")
        return cursor.fetchall()
    except Exception:
        print_exc()
        return []
    finally:
        if conn:
            conn.close()

def get_all_queries_enabled_map():
    """Return a dict {query_id: enabled} for all queries."""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, enabled FROM queries")
        rows = cursor.fetchall()
        return {row[0]: (row[1] == 1) for row in rows}
    except Exception:
        print_exc()
        return {}
    finally:
        if conn:
            conn.close()

def is_query_enabled(query_id):
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT enabled FROM queries WHERE id = ?", (query_id,))
        row = cursor.fetchone()
        return bool(row[0]) if row is not None else False
    except Exception:
        print_exc()
        return False
    finally:
        if conn:
            conn.close()

def set_query_enabled(query_id, enabled):
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE queries SET enabled = ? WHERE id = ?", (1 if enabled else 0, query_id))
        conn.commit()
        return cursor.rowcount == 1
    except Exception:
        print_exc()
        return False
    finally:
        if conn:
            conn.close()

def toggle_query_enabled(query_id):
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE queries SET enabled = CASE enabled WHEN 1 THEN 0 ELSE 1 END WHERE id = ?", (query_id,))
        conn.commit()
        return cursor.rowcount == 1
    except Exception:
        print_exc()
        return False
    finally:
        if conn:
            conn.close()

def is_query_owned_by_user(query_id, user_id):
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(1) FROM queries WHERE id = ? AND owner_id = ?",
            (query_id, user_id),
        )
        return cursor.fetchone()[0] == 1
    except Exception:
        print_exc()
        return False
    finally:
        if conn:
            conn.close()

def get_query_owner_id(query_id):
    """Return owner_id for a query or None."""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT owner_id FROM queries WHERE id = ?", (query_id,))
        row = cursor.fetchone()
        return row[0] if row else None
    except Exception:
        print_exc()
        return None
    finally:
        if conn:
            conn.close()

def is_query_in_db(processed_query, owner_id=None):
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # If owner_id is provided, check within that owner's scope to allow same query for different users
        if owner_id is not None:
            cursor.execute(
                "SELECT COUNT() FROM queries WHERE query = ? AND owner_id = ?",
                (processed_query, owner_id),
            )
        else:
            cursor.execute(
                "SELECT COUNT() FROM queries WHERE query = ?",
                (processed_query,),
            )
        if cursor.fetchone()[0]:
            return True
        return False
    except Exception:
        print_exc()
        return False
    finally:
        if conn:
            conn.close()

def add_query_to_db(query, name=None, owner_id=None):
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        try:
            delay_param = get_parameter("query_refresh_delay")
            delay = int(delay_param) if delay_param is not None else None
        except Exception:
            delay = None

        if owner_id is not None and name:
            cursor.execute(
                "INSERT INTO queries (query, last_item, query_name, owner_id, delay) "
                "VALUES (?, NULL, ?, ?, ?)",
                (query, name, owner_id, delay),
            )
        elif owner_id is not None:
            cursor.execute(
                "INSERT INTO queries (query, last_item, owner_id, delay) "
                "VALUES (?, NULL, ?, ?)",
                (query, owner_id, delay),
            )
        elif name:
            cursor.execute(
                "INSERT INTO queries (query, last_item, query_name, delay) "
                "VALUES (?, NULL, ?, ?)",
                (query, name, delay),
            )
        else:
            cursor.execute(
                "INSERT INTO queries (query, last_item, delay) "
                "VALUES (?, NULL, ?)",
                (query, delay),
            )
        conn.commit()
    except Exception:
        print_exc()
    finally:
        if conn:
            conn.close()

def get_query_id_by_rowid(rowid):
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        query = f"SELECT id FROM (SELECT id, ROW_NUMBER() OVER (ORDER BY ROWID) rn FROM queries) t WHERE rn={rowid}"
        cursor.execute(query)
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

def remove_query_from_db(query_number):
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Delete items associated with this query using query_id
        cursor.execute("DELETE FROM items WHERE query_id=?", (query_number,))
        # Delete the query
        cursor.execute("DELETE FROM queries WHERE id=?", (query_number,))
        conn.commit()
    except Exception:
        print_exc()
    finally:
        if conn:
            conn.close()

def remove_all_queries_from_db():
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
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

def remove_all_queries_for_user(owner_id):
    """
    Remove all queries (and their items) for a specific user.
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Delete items for this user's queries
        cursor.execute(
            """
            DELETE FROM items
            WHERE query_id IN (
                SELECT id FROM queries WHERE owner_id = ?
            )
            """,
            (owner_id,),
        )
        # Delete the user's queries
        cursor.execute("DELETE FROM queries WHERE owner_id = ?", (owner_id,))
        conn.commit()
        return True
    except Exception:
        print_exc()
        return False
    finally:
        if conn:
            conn.close()


def update_query_in_db(query_id, query=None, name=None, owner_id=None, delay=None):
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        set_clauses = []
        params = []

        if query is not None:
            set_clauses.append("query = ?")
            params.append(query)
        if name is not None:
            set_clauses.append("query_name = ?")
            params.append(name)
        if owner_id is not None:
            set_clauses.append("owner_id = ?")
            params.append(owner_id)
        if delay is not None:
            set_clauses.append("delay = ?")
            params.append(delay)

        # Nothing to update
        if not set_clauses:
            return False

        sql = f"UPDATE queries SET {', '.join(set_clauses)} WHERE id = ?"
        params.append(query_id)

        cursor.execute(sql, params)
        conn.commit()
        return cursor.rowcount == 1
    except Exception:
        print_exc()
        return False
    finally:
        if conn:
            conn.close()

### ALLOWLIST FUNC ###

def add_to_allowlist(country):
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
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
        conn = sqlite3.connect(DB_PATH)
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
        conn = sqlite3.connect(DB_PATH)
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
        conn = sqlite3.connect(DB_PATH)
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
        conn = sqlite3.connect(DB_PATH)
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
        conn = sqlite3.connect(DB_PATH)
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
        conn = sqlite3.connect(DB_PATH)
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
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        if query:
            # Get the query_id for the given query
            cursor.execute("SELECT id FROM queries WHERE query=?", (query,))
            result = cursor.fetchone()
            if result:
                query_id = result[0]
                # Get items with the matching query_id
                cursor.execute(
                    "SELECT i.item, i.title, i.price, i.currency, i.timestamp, q.query, i.photo_url, q.query_name FROM items i JOIN queries q ON i.query_id = q.id WHERE i.query_id=? ORDER BY i.timestamp DESC LIMIT ?",
                    (query_id, limit),
                )
            else:
                return []
        else:
            # Join with queries table to get the query text
            cursor.execute(
                "SELECT i.item, i.title, i.price, i.currency, i.timestamp, q.query, i.photo_url, q.query_name FROM items i JOIN queries q ON i.query_id = q.id ORDER BY i.timestamp DESC LIMIT ?",
                (limit,),
            )
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
        conn = sqlite3.connect(DB_PATH)
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
        conn = sqlite3.connect(DB_PATH)
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
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT i.item, i.title, i.price, i.currency, i.timestamp, q.query, i.photo_url FROM items i JOIN queries q ON i.query_id = q.id ORDER BY i.timestamp DESC LIMIT 1"
        )
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
        conn = sqlite3.connect(DB_PATH)
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


# User management functions


def hash_password(password):
    """
    Hash a password using SHA-256

    Args:
        password (str): The password to hash

    Returns:
        str: The hashed password
    """
    return hashlib.sha256(password.encode()).hexdigest()


def create_user(username, password, is_admin=False):
    """
    Create a new user in the database

    Args:
        username (str): The username
        password (str): The password (will be hashed)
        is_admin (bool): Whether the user is an admin (default: False)

    Returns:
        bool: True if the user was created successfully, False otherwise
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Hash the password
        password_hash = hash_password(password)

        # Insert the user
        cursor.execute(
            "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)",
            (username, password_hash, 1 if is_admin else 0),
        )
        conn.commit()
        return True
    except Exception:
        print_exc()
        return False
    finally:
        if conn:
            conn.close()


def authenticate_user(username, password):
    """
    Authenticate a user

    Args:
        username (str): The username
        password (str): The password

    Returns:
        int or None: The user ID if authentication was successful, None otherwise
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Hash the password
        password_hash = hash_password(password)

        # Check if the user exists and the password is correct
        cursor.execute(
            "SELECT id FROM users WHERE username = ? AND password_hash = ?",
            (username, password_hash),
        )
        result = cursor.fetchone()

        return result[0] if result else None
    except Exception:
        print_exc()
        return None
    finally:
        if conn:
            conn.close()


def get_user_count():
    """
    Get the number of users in the database

    Returns:
        int: The number of users
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        return cursor.fetchone()[0]
    except Exception:
        print_exc()
        return 0
    finally:
        if conn:
            conn.close()


def is_user_admin(user_id):
    """
    Check if a user is an admin

    Args:
        user_id (int): The user ID

    Returns:
        bool: True if the user is an admin, False otherwise
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT is_admin FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        return bool(result[0]) if result else False
    except Exception:
        print_exc()
        return False
    finally:
        if conn:
            conn.close()


def create_reset_token(username):
    """
    Create a password reset token for a user

    Args:
        username (str): The username

    Returns:
        str or None: The reset token if successful, None otherwise
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Check if the user exists
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()

        if not result:
            return None

        # Generate a token
        token = secrets.token_urlsafe(32)
        # Set expiration to 24 hours from now
        expiration = int(time.time()) + 86400

        # Update the user with the token
        cursor.execute(
            "UPDATE users SET reset_token = ?, reset_token_exp = ? WHERE username = ?",
            (token, expiration, username),
        )
        conn.commit()

        return token
    except Exception:
        print_exc()
        return None
    finally:
        if conn:
            conn.close()


def verify_reset_token(token):
    """
    Verify a password reset token

    Args:
        token (str): The token to verify

    Returns:
        str or None: The username if the token is valid, None otherwise
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Get the current time
        current_time = int(time.time())

        # Check if the token exists and is not expired
        cursor.execute(
            "SELECT username FROM users WHERE reset_token = ? AND reset_token_exp > ?",
            (token, current_time),
        )
        result = cursor.fetchone()

        return result[0] if result else None
    except Exception:
        print_exc()
        return None
    finally:
        if conn:
            conn.close()


def reset_password(token, new_password):
    """
    Reset a user's password using a token

    Args:
        token (str): The reset token
        new_password (str): The new password

    Returns:
        bool: True if the password was reset successfully, False otherwise
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Get the username for the token
        username = verify_reset_token(token)

        if not username:
            return False

        # Hash the new password
        password_hash = hash_password(new_password)

        # Update the user's password and clear the token
        cursor.execute(
            "UPDATE users SET password_hash = ?, reset_token = NULL, reset_token_exp = NULL WHERE username = ?",
            (password_hash, username),
        )
        conn.commit()

        return True
    except Exception:
        print_exc()
        return False
    finally:
        if conn:
            conn.close()


def get_all_users():
    """
    Get all users from the database

    Returns:
        list: A list of tuples containing user information (id, username, is_admin, created_at)
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, is_admin, created_at FROM users ORDER BY username"
        )
        return cursor.fetchall()
    except Exception:
        print_exc()
        return []
    finally:
        if conn:
            conn.close()


def delete_user(user_id):
    """
    Delete a user from the database

    Args:
        user_id (int): The user ID to delete

    Returns:
        bool: True if the user was deleted successfully, False otherwise
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Check if this is the last admin user
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = 1")
        admin_count = cursor.fetchone()[0]

        cursor.execute("SELECT is_admin FROM users WHERE id = ?", (user_id,))
        user_result = cursor.fetchone()

        if not user_result:
            return False

        is_admin = bool(user_result[0])

        # Don't allow deleting the last admin user
        if is_admin and admin_count <= 1:
            return False

        remove_all_queries_for_user(user_id)

        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception:
        print_exc()
        return False
    finally:
        if conn:
            conn.close()
