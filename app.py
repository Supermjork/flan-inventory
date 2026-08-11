import flet as ft
import sqlite3


def main(page: ft.Page):
    page.title = "Kitchen Inventory"

    db = sqlite3.connect("inventory.db")

    db.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        )
    """)
    db.commit()

    item_name = ft.TextField(label="Item name")

    items_list = ft.Column()

    def load_items():
        items_list.controls.clear()

        rows = db.execute("""
            SELECT id, name
            FROM items
            ORDER BY id
        """).fetchall()

        for item_id, name in rows:
            items_list.controls.append(
                ft.Text(f"{item_id} — {name}")
            )

        page.update()

    def add_item(e):
        name = item_name.value.strip()

        if not name:
            return

        try:
            db.execute(
                "INSERT INTO items (name) VALUES (?)",
                (name,)
            )
            db.commit()

        except sqlite3.IntegrityError:
            print("Item already exists.")
            return

        item_name.value = ""
        load_items()

    add_button = ft.Button(
        content="Add",
        on_click=add_item
    )

    page.add(
        ft.Text("Kitchen Inventory", size=24),
        ft.Row([
            item_name,
            add_button
        ]),
        ft.Divider(),
        items_list
    )

    load_items()


ft.run(main)