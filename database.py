import sqlite3

# Database Initialisation

db = sqlite3.connect("inventory.db")

db.execute("""
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL COLLATE NOCASE UNIQUE
    )
""")

db.commit()

# Error exposure

IntegrityError = sqlite3.IntegrityError

# Function suite

def add_item(name):
    try:
        db.execute(
            "INSERT INTO items (name) VALUES (?)",
            (name,)
        )
        db.commit()
        return True

    except IntegrityError:
        return False

def get_items():
    return db.execute("""
        SELECT id, name
        FROM items
        ORDER BY id
    """).fetchall()

