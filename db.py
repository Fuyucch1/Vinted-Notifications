import sqlite3
from traceback import print_exc


def create_sqlite_db():
    conn = None
    try:
        conn = sqlite3.connect("vinted.db")
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE items (item NUMERIC, keyword TEXT)")
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


def add_item_to_db(id, keyword):
    conn = None
    try:
        conn = sqlite3.connect("vinted.db")
        cursor = conn.cursor()
        # Insert into db the id and the keyword related to the item
        cursor.execute("INSERT INTO items VALUES (?, ?)", (id, keyword))
        conn.commit()
    except Exception:
        print_exc()
    finally:
        if conn:
            conn.close()


def clean_db():
    conn = None
    # We clean the db by doing two processes :
    # First, we remove all the items that are too old (we keep the last 50 per keyword)
    # Then, we remove all lines in the items table that do not match any keyword in the keywords table
    # This should lead to no deletion, but let's keep it safe

    # Get all the keywords
    keywords = get_keywords()
    # For each keyword we keep the last 50 items
    for keyword in keywords:
        conn = sqlite3.connect("vinted.db")
        cursor = conn.cursor()
        cursor.execute("SELECT item FROM items WHERE keyword=? ORDER BY ROWID DESC LIMIT -1 OFFSET 50", (keyword[0],))
        items = cursor.fetchall()
        for item in items:
            cursor.execute("DELETE FROM items WHERE item=?", (item[0],))
            conn.commit()
        conn.close()

    # Remove all items that do not match any keyword
    conn = sqlite3.connect("vinted.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM items WHERE keyword NOT IN (SELECT keyword FROM keywords)")
    conn.commit()
    conn.close()


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
        cursor.execute("DELETE FROM items WHERE keyword=?", (keyword,))
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
        cursor.execute("DELETE FROM items")
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
