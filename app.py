import flet as ft
from database import db, IntegrityError


def main(page: ft.Page):
    page.title = "Kitchen Inventory"

    db.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL COLLATE NOCASE UNIQUE
        )
    """)
    db.commit()

    items_list = ft.Column()

    message = ft.Text()

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

        except IntegrityError:
            message.value = "Item already exists."
            page.update()
            return

        message.value = ""
        item_name.value = ""
        load_items()

    item_name = ft.TextField(
        label="Item name",
        on_submit=add_item
    )
    
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
        message,
        ft.Divider(),
        items_list
    )

    load_items()


ft.run(main)