import flet as ft
from datetime import datetime
from database import (
    add_item as add_item_to_database,
    get_items,
    add_inventory,
    get_inventory
)


# -------------------------
# Functions
# -------------------------

def load_items(page: ft.Page, items_list: ft.Column):
    items_list.controls.clear()

    rows = get_items()

    for item_id, name in rows:
        items_list.controls.append(
            ft.Text(f"{item_id} — {name}")
        )

    page.update()


def load_inventory_items(page: ft.Page, inventory_item: ft.Dropdown):
    inventory_item.options.clear()

    for item_id, name in get_items():
        inventory_item.options.append(
            ft.DropdownOption(
                key=str(item_id),
                text=name
            )
        )

    page.update()


def add_item(
    page: ft.Page,
    item_name: ft.TextField,
    items_list: ft.Column,
    message: ft.Text,
    inventory_item: ft.Dropdown
):
    name = item_name.value.strip()

    if not name:
        return

    if not add_item_to_database(name):
        message.value = "Item already exists."
        page.update()
        return

    message.value = ""
    item_name.value = ""

    load_items(page, items_list)
    load_inventory_items(page, inventory_item)

    page.pop_dialog()


def load_inventory(page: ft.Page, inventory_list: ft.Column):
    inventory_list.controls.clear()

    rows = get_inventory()

    for date, item_name, amount, unit in rows:
        inventory_list.controls.append(
            ft.Text(
                f"{date} — {item_name}: "
                f"{amount} {unit}"
            )
        )

    page.update()


def add_inventory_record(
    page: ft.Page,
    inventory_date: ft.TextField,
    inventory_item: ft.Dropdown,
    inventory_amount: ft.TextField,
    inventory_unit: ft.TextField,
    inventory_message: ft.Text,
    inventory_list: ft.Column
):
    date = inventory_date.value.strip()
    item_id = inventory_item.value
    amount = inventory_amount.value.strip()
    unit = inventory_unit.value.strip()

    if not date or not item_id or not amount or not unit:
        inventory_message.value = "Please fill in all fields."
        page.update()
        return

    try:
        date = datetime.strptime(
            date,
            "%Y-%m-%d"
        ).strftime("%Y-%m-%d")
    except ValueError:
        inventory_message.value = "Date must be YYYY-MM-DD."
        page.update()
        return

    try:
        amount = float(amount)
    except ValueError:
        inventory_message.value = "Amount must be a number."
        page.update()
        return

    if amount < 0:
        inventory_message.value = "Amount cannot be negative."
        page.update()
        return

    if not add_inventory(
        date,
        int(item_id),
        amount,
        unit
    ):
        inventory_message.value = (
            "An inventory record already exists "
            "for this item and date."
        )
        page.update()
        return

    inventory_message.value = ""
    inventory_amount.value = ""
    inventory_unit.value = ""

    load_inventory(page, inventory_list)

    page.pop_dialog()


def main(page: ft.Page):
    page.title = "Kitchen Inventory"

    page.window.min_width = 800
    page.window.min_height = 800

    page.window.width = 1000
    page.window.height = 850

    items_list = ft.Column()
    inventory_list = ft.Column()

    message = ft.Text()
    inventory_message = ft.Text()

    # -------------------------
    # Add Item controls
    # -------------------------

    item_name = ft.TextField(
        label="Item name",
        on_submit=lambda: add_item(
            page,
            item_name,
            items_list,
            message,
            inventory_item
        ),
        expand=True
    )

    add_button = ft.Button(
        content="Add",
        on_click=lambda: add_item(
            page,
            item_name,
            items_list,
            message,
            inventory_item
        ),
        expand=True
    )

    close_add_item_button = ft.Button(
        content="Cancel",
        on_click=lambda: page.pop_dialog()
    )

    add_item_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Add Item"),
        content=ft.Column(
            controls=[
                item_name,
                message
            ],
            tight=True
        ),
        actions=[
            close_add_item_button,
            add_button
        ]
    )

    open_add_item_button = ft.Button(
        content="Add Item",
        on_click=lambda: page.show_dialog(add_item_dialog)
    )

    # -------------------------
    # Inventory controls
    # -------------------------

    inventory_item = ft.Dropdown(
        label="Item",
        expand=True
    )

    inventory_date = ft.TextField(
        label="Date",
        value="2026-08-12",
        on_submit=lambda e: add_inventory_record(
            page,
            inventory_date,
            inventory_item,
            inventory_amount,
            inventory_unit,
            inventory_message,
            inventory_list
        ),
        expand=True
    )

    inventory_amount = ft.TextField(
        label="Amount",
        on_submit=lambda e: add_inventory_record(
            page,
            inventory_date,
            inventory_item,
            inventory_amount,
            inventory_unit,
            inventory_message,
            inventory_list
        ),
        expand=True
    )

    inventory_unit = ft.TextField(
        label="Unit",
        on_submit=lambda e: add_inventory_record(
            page,
            inventory_date,
            inventory_item,
            inventory_amount,
            inventory_unit,
            inventory_message,
            inventory_list
        ),
        expand=True
    )

    inventory_add_button = ft.Button(
        content="Add Inventory",
        on_click=lambda e: add_inventory_record(
            page,
            inventory_date,
            inventory_item,
            inventory_amount,
            inventory_unit,
            inventory_message,
            inventory_list
        ),
        expand=True
    )

    close_inventory_button = ft.Button(
        content="Cancel",
        on_click=lambda: page.pop_dialog()
    )

    inventory_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Inventory an Item"),
        content=ft.Column(
            controls=[
                inventory_date,
                inventory_item,
                inventory_amount,
                inventory_unit,
                inventory_message
            ],
            tight=True
        ),
        actions=[
            close_inventory_button,
            inventory_add_button
        ]
    )

    open_inventory_button = ft.Button(
        content="Inventory an Item",
        on_click=lambda: page.show_dialog(inventory_dialog)
    )

    # -------------------------
    # Main page
    # -------------------------

    page.add(
        ft.Text(
            "Kitchen Inventory",
            size=24
        ),

        ft.Row(
            controls=[
                open_add_item_button,
                open_inventory_button
            ]
        ),

        ft.Divider(),

        ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text(
                            "Items",
                            size=20
                        ),
                        items_list
                    ],
                    expand=True
                ),

                ft.VerticalDivider(),

                ft.Column(
                    controls=[
                        ft.Text(
                            "Inventory History",
                            size=20
                        ),
                        inventory_list
                    ],
                    expand=True
                )
            ],
            expand=True
        )
    )

    load_items(page, items_list)
    load_inventory_items(page, inventory_item)
    load_inventory(page, inventory_list)


ft.run(main)