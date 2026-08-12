import sqlite3

db = sqlite3.connect("inventory.db")

IntegrityError = sqlite3.IntegrityError
