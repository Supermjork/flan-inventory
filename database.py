import sqlite3

# Database Initialisation

db = sqlite3.connect("inventory.db")

db.execute("""
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL COLLATE NOCASE UNIQUE,
        unit TEXT NOT NULL
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

def add_item(name, unit):
    try:
        db.execute(
            "INSERT INTO items (name, unit) VALUES (?, ?)",
            (name, unit)
        )
        db.commit()
        return True

    except IntegrityError:
        return False

def get_items():
    return db.execute("""
        SELECT id, name, unit
        FROM items
        ORDER BY id
    """).fetchall()

def update_item(item_id, name, unit):
    try:
        db.execute(
            "UPDATE items SET name = ?, unit = ? WHERE id = ?",
            (name, unit, item_id)
        )
        db.commit()
        return True

    except IntegrityError:
        return False

def count_inventory_for_item(item_id):
    row = db.execute(
        "SELECT COUNT(*) FROM inventory WHERE item_id = ?",
        (item_id,)
    ).fetchone()

    return row[0]

def delete_item(item_id):
    db.execute("DELETE FROM inventory WHERE item_id = ?", (item_id,))
    db.execute("DELETE FROM items WHERE id = ?", (item_id,))
    db.commit()

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
        SELECT inventory.id, inventory.date, items.name,
               inventory.amount, inventory.unit
        FROM inventory
        JOIN items ON inventory.item_id = items.id
        ORDER BY inventory.date, inventory.item_id
    """).fetchall()

def update_inventory_record(record_id, date, amount):
    try:
        db.execute(
            "UPDATE inventory SET date = ?, amount = ? WHERE id = ?",
            (date, amount, record_id)
        )
        db.commit()
        return True

    except IntegrityError:
        return False

def delete_inventory_record(record_id):
    db.execute("DELETE FROM inventory WHERE id = ?", (record_id,))
    db.commit()