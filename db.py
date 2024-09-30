import sqlite3
from traceback import print_exc


def create_sqlite_db():
    conn = None
    try:
        conn = sqlite3.connect("vinted.db")
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE items (item NUMERIC)")
        cursor.execute("CREATE TABLE keywords (keyword TEXT, already_processed NUMERIC DEFAULT 0)")
        conn.commit()
    except Exception:
        print_exc()
    finally:
        if conn:
            conn.close()


def is_item_in_db(id):
    conn = None
    try:
        conn = sqlite3.connect("vinted.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT() FROM items WHERE item=?", (id,))
        return cursor.fetchone()[0]
    except Exception:
        print_exc()
    finally:
        if conn:
            conn.close()


def add_item_to_db(id):
    conn = None
    try:
        conn = sqlite3.connect("vinted.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO items VALUES (?)", (id,))
        conn.commit()
    except Exception:
        print_exc()
    finally:
        if conn:
            conn.close()


# TODO : Function to prune the db (update db to id + keyword and keep the last 20 per keyword)

def get_keywords():
    conn = None
    try:
        conn = sqlite3.connect("vinted.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM keywords")
        return cursor.fetchall()
    except Exception:
        print_exc()
    finally:
        if conn:
            conn.close()


def is_keyword_in_db(keyword):
    conn = None
    try:
        conn = sqlite3.connect("vinted.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT() FROM keywords WHERE keyword=?", (keyword,))
        return cursor.fetchone()[0]
    except Exception:
        print_exc()
    finally:
        if conn:
            conn.close()


def add_keyword_to_db(keyword):
    conn = None
    try:
        conn = sqlite3.connect("vinted.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO keywords VALUES (?, 0)", (keyword,))
        conn.commit()
    except Exception:
        print_exc()
    finally:
        if conn:
            conn.close()


def remove_keyword_from_db(keyword):
    conn = None
    try:
        conn = sqlite3.connect("vinted.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM keywords WHERE keyword=?", (keyword,))
        conn.commit()
    except Exception:
        print_exc()
    finally:
        if conn:
            conn.close()


def remove_all_keywords_from_db():
    conn = None
    try:
        conn = sqlite3.connect("vinted.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM keywords")
        conn.commit()
    except Exception:
        print_exc()
    finally:
        if conn:
            conn.close()


def update_keyword_processed(keyword):
    conn = None
    try:
        conn = sqlite3.connect("vinted.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE keywords SET already_processed = 1 WHERE keyword=?", (keyword,))
        conn.commit()
    except Exception:
        print_exc()
    finally:
        if conn:
            conn.close()
