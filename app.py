import flet as ft
import flet_datatable2 as fdt
import csv
from pathlib import Path
from datetime import datetime, timedelta
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors as pdf_colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
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

    for item_id, name, unit in rows:
        items_list.controls.append(
            ft.Text(f"{item_id} — {name}")
        )

    page.update()


def load_inventory_items(page: ft.Page, inventory_item: ft.Dropdown):
    inventory_item.options.clear()

    for item_id, name, unit in get_items():
        inventory_item.options.append(
            ft.DropdownOption(
                key=str(item_id),
                text=name,
                data=unit
            )
        )

    page.update()

def select_inventory_item(
    e,
    inventory_item: ft.Dropdown,
    inventory_unit: ft.TextField
):
    if not e.control.value:
        inventory_unit.value = ""
        return

    selected_option = next(
        (
            option
            for option in inventory_item.options
            if option.key == e.control.value
        ),
        None
    )

    if selected_option:
        inventory_unit.value = selected_option.data

    inventory_unit.update()


def add_item(
    page: ft.Page,
    item_name: ft.TextField,
    item_unit: ft.TextField,
    items_list: ft.Column,
    message: ft.Text,
    inventory_item: ft.Dropdown
):
    name = item_name.value.strip()
    unit = item_unit.value.strip()

    if not name or not unit:
        return

    if not add_item_to_database(name, unit):
        message.value = "Item already exists."
        page.update()
        return

    message.value = ""
    item_name.value = ""
    item_unit.value = ""

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

def get_inventory_table_data():
    items = get_items()
    inventory = get_inventory()

    if not inventory:
        return [], []

    # Create a lookup:
    # (date, item_id) -> amount
    inventory_lookup = {}

    for date, item_name, amount, unit in inventory:
        for item_id, name, item_unit in items:
            if name == item_name:
                inventory_lookup[(date, item_id)] = amount
                break

    # Get all dates in the inventory records
    dates = sorted(
        set(date for date, _, _, _ in inventory)
    )

    # Create a continuous date range
    start_date = datetime.strptime(
        dates[0],
        "%Y-%m-%d"
    )
    end_date = datetime.strptime(
        dates[-1],
        "%Y-%m-%d"
    )

    current_date = start_date
    all_dates = []

    while current_date <= end_date:
        all_dates.append(
            current_date.strftime("%Y-%m-%d")
        )

        current_date += timedelta(days=1)

    # Build the table rows
    rows = []

    for date in all_dates:
        row = [date]

        for item_id, name, unit in items:
            amount = inventory_lookup.get(
                (date, item_id)
            )

            if amount is None:
                row.append("No inventory data for this date")
            else:
                row.append(str(amount))

        rows.append(row)

    return items, rows

def build_inventory_table():
    items, rows = get_inventory_table_data()

    columns = [
        fdt.DataColumn2(
            label=ft.Text("Date"),
            fixed_width=120
        )
    ]

    for item_id, name, unit in items:
        columns.append(
            fdt.DataColumn2(
                label=ft.Text(f"{name} ({unit})"),
                fixed_width=180
            )
        )

    table_rows = []

    for row in rows:
        cells = []

        for value in row:
            cells.append(
                ft.DataCell(
                    ft.Text(value)
                )
            )

        table_rows.append(
            ft.DataRow(
                cells=cells
            )
        )

    return fdt.DataTable2(
        columns=columns,
        rows=table_rows,
        fixed_top_rows=1,
        fixed_left_columns=1,
        min_width=1200,
        visible_horizontal_scroll_bar=True,
        visible_vertical_scroll_bar=True
    )

def show_inventory_table(page: ft.Page, inventory_table_dialog: ft.AlertDialog):
    inventory_table_dialog.content = ft.Container(
        content=build_inventory_table(),
        height=500,
        width=900
    )

    page.show_dialog(inventory_table_dialog)

def get_inventory_table_headers(items):
    headers = ["Date"]

    for item_id, name, unit in items:
        headers.append(f"{name} ({unit})")

    return headers

def export_inventory_csv(filename):
    items, rows = get_inventory_table_data()
    headers = get_inventory_table_headers(items)

    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:
        writer = csv.writer(file)

        writer.writerow(headers)

        for row in rows:
            writer.writerow(row)

def export_inventory_xlsx(filename):
    items, rows = get_inventory_table_data()
    headers = get_inventory_table_headers(items)

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Inventory"

    sheet.append(headers)

    for cell in sheet[1]:
        cell.font = Font(bold=True)
        cell.fill = PatternFill(
            start_color="DDDDDD",
            end_color="DDDDDD",
            fill_type="solid"
        )

    for row in rows:
        sheet.append(row)

    for column_cells in sheet.columns:
        max_length = max(
            len(str(cell.value)) for cell in column_cells
        )
        sheet.column_dimensions[
            column_cells[0].column_letter
        ].width = min(max(max_length + 2, 10), 40)

    workbook.save(filename)

def export_inventory_pdf(filename):
    items, rows = get_inventory_table_data()
    headers = get_inventory_table_headers(items)

    styles = getSampleStyleSheet()
    title = Paragraph("Kitchen Inventory", styles["Title"])

    table = Table([headers] + rows, repeatRows=1)
    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), pdf_colors.HexColor("#DDDDDD")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, pdf_colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ])
    )

    doc = SimpleDocTemplate(filename, pagesize=landscape(letter))
    doc.build([title, table])

EXPORTERS = {
    "csv": export_inventory_csv,
    "xlsx": export_inventory_xlsx,
    "pdf": export_inventory_pdf,
}

def save_inventory(page: ft.Page, save_message: ft.Text, file_format: str):
    items, rows = get_inventory_table_data()

    if not rows:
        save_message.value = "No inventory data to export."
        save_message.color = "red"
        page.update()
        return

    try:
        downloads_dir = Path.home() / "Downloads"
        downloads_dir.mkdir(parents=True, exist_ok=True)

        filename = downloads_dir / (
            f"inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            f".{file_format}"
        )

        EXPORTERS[file_format](str(filename))

        save_message.value = f"Saved to {filename}"
        save_message.color = "green"

    except Exception as error:
        save_message.value = f"Save failed: {error}"
        save_message.color = "red"

    page.update()

def main(page: ft.Page):
    page.title = "Kitchen Inventory"

    page.window.min_width = 800
    page.window.min_height = 800

    page.window.width = 1000
    page.window.height = 850
    page.update()

    items_list = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )
    inventory_list = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )

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
            item_unit,
            items_list,
            message,
            inventory_item
        ),
        expand=True
    )

    item_unit = ft.TextField(
        label="Unit",
        on_submit=lambda e: add_item(
            page,
            item_name,
            item_unit,
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
            item_unit,
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
                item_unit,
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
        on_select=lambda e: select_inventory_item(
            e,
            inventory_item,
            inventory_unit
        ),
        expand=True
    )

    inventory_date = ft.TextField(
        label="Date",
        value=datetime.now().strftime("%Y-%m-%d"),
        read_only=True,
        suffix_icon=ft.Icons.CALENDAR_MONTH,
        on_click=lambda e: page.show_dialog(inventory_date_picker),
        expand=True
    )

    def on_inventory_date_change(e):
        inventory_date.value = e.control.value.strftime("%Y-%m-%d")
        inventory_date.update()

    inventory_date_picker = ft.DatePicker(
        value=datetime.now(),
        first_date=datetime(2020, 1, 1),
        last_date=datetime(2100, 12, 31),
        on_change=on_inventory_date_change
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

    inventory_table = build_inventory_table()

    save_message = ft.Text()

    export_csv_button = ft.Button(
        content="Export CSV",
        on_click=lambda e: save_inventory(
            page,
            save_message,
            "csv"
        )
    )

    export_xlsx_button = ft.Button(
        content="Export XLSX",
        on_click=lambda e: save_inventory(
            page,
            save_message,
            "xlsx"
        )
    )

    export_pdf_button = ft.Button(
        content="Export PDF",
        on_click=lambda e: save_inventory(
            page,
            save_message,
            "pdf"
        )
    )

    close_inventory_table_button = ft.Button(
        content="Close",
        on_click=lambda e: page.pop_dialog()
    )

    inventory_table_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Current Inventory"),
        content=ft.Container(
            content=ft.Column(
                controls=[
                    inventory_table
                ],
                scroll=ft.ScrollMode.AUTO,
                expand=True
            ),
            height=500,
            width=900
        ),
        actions=[
            ft.Row(
                controls=[
                    save_message,
                    export_csv_button,
                    export_xlsx_button,
                    export_pdf_button,
                    close_inventory_table_button
                ],
                alignment=ft.MainAxisAlignment.END,
                spacing=10,
                run_spacing=10,
                wrap=True,
                width=860
            )
        ]
    )

    open_inventory_table_button = ft.Button(
        content="Current Inventory",
        on_click=lambda e: show_inventory_table(
            page,
            inventory_table_dialog
        )
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
                open_inventory_button,
                open_inventory_table_button
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