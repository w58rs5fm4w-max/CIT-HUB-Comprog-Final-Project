"""CSV export and report helpers."""
import csv
from tkinter import filedialog, messagebox
from database import get_connection

def export_equipment(parent):
    path = filedialog.asksaveasfilename(parent=parent, defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")], initialfile="cit_hub_inventory.csv")
    if not path:
        return
    with get_connection() as conn:
        rows = conn.execute("""SELECT asset_code,name,category,location,condition,status
                               FROM equipment ORDER BY asset_code""").fetchall()
    def safe_cell(value):
        text = "" if value is None else str(value)
        if text.startswith(("=", "+", "-", "@", "\\t", "\\r")):
            return "'" + text
        return text

    with open(path, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(["Asset Code","Name","Category","Location","Condition","Status"])
        writer.writerows([[safe_cell(value) for value in row] for row in rows])
    messagebox.showinfo("Export complete", f"Inventory report saved to:\n{path}", parent=parent)
