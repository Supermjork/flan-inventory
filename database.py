import sqlite3

# Database Initialisation

db = sqlite3.connect("inventory.db")

db.execute("""
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL COLLATE NOCASE UNIQUE
    )
""")

db.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY,
        date TEXT NOT NULL,
        item_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        unit TEXT NOT NULL,
        UNIQUE(date, item_id),
        FOREIGN KEY (item_id) REFERENCES items(id)
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

def add_inventory(date, item_id, amount, unit):
    try:
        db.execute(
            """
            INSERT INTO inventory (date, item_id, amount, unit)
            VALUES (?, ?, ?, ?)
            """,
            (date, item_id, amount, unit)
        )
        db.commit()
        return True

    except IntegrityError:
        return False

def get_inventory():
    return db.execute("""
        SELECT inventory.date, items.name, inventory.amount, inventory.unit
        FROM inventory
        JOIN items ON inventory.item_id = items.id
        ORDER BY inventory.date, inventory.item_id
    """).fetchall()
