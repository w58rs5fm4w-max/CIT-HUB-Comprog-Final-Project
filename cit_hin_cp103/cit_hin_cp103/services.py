"""Application rules and database operations for CIT HUB."""
import sqlite3
from database import get_connection
from models import Equipment, Borrower
from validators import required, validate_loan_dates

class CampusHubService:
    def add_equipment(self, item: Equipment):
        missing = required({"Asset code": item.asset_code, "Name": item.name,
                            "Category": item.category, "Location": item.location})
        if missing:
            raise ValueError("Required: " + ", ".join(missing))
        with get_connection() as conn:
            conn.execute("""INSERT INTO equipment
                (asset_code,name,category,location,condition,status)
                VALUES (?,?,?,?,?,'Available')""",
                (item.asset_code.strip(), item.name.strip(), item.category.strip(),
                 item.location.strip(), item.condition.strip()))

    def update_equipment(self, asset_id, item: Equipment):
        missing = required({"Asset code": item.asset_code, "Name": item.name,
                            "Category": item.category, "Location": item.location})
        if missing:
            raise ValueError("Required: " + ", ".join(missing))
        with get_connection() as conn:
            conn.execute("""UPDATE equipment SET asset_code=?,name=?,category=?,
                location=?,condition=? WHERE asset_id=? AND status!='Inactive'""",
                (item.asset_code.strip(), item.name.strip(), item.category.strip(),
                 item.location.strip(), item.condition.strip(), asset_id))

    def deactivate_equipment(self, asset_id):
        with get_connection() as conn:
            row = conn.execute("SELECT status FROM equipment WHERE asset_id=?", (asset_id,)).fetchone()
            if not row:
                raise ValueError("Equipment record was not found.")
            if row["status"] == "Borrowed":
                raise ValueError("Return the borrowed equipment before deactivating it.")
            conn.execute("UPDATE equipment SET status='Inactive' WHERE asset_id=?", (asset_id,))

    def add_borrower(self, borrower: Borrower):
        missing = required({"Borrower code": borrower.borrower_code,
                            "Name": borrower.display_name,
                            "Department/Program": borrower.department_or_program})
        if missing:
            raise ValueError("Required: " + ", ".join(missing))
        with get_connection() as conn:
            conn.execute("""INSERT INTO borrowers
                (borrower_code,display_name,department_or_program)
                VALUES (?,?,?)""",
                (borrower.borrower_code.strip(), borrower.display_name.strip(),
                 borrower.department_or_program.strip()))

    def checkout(self, asset_code, borrower_code, borrowed_on, due_on):
        ok, message = validate_loan_dates(borrowed_on, due_on)
        if not ok:
            raise ValueError(message)
        with get_connection() as conn:
            asset = conn.execute("SELECT * FROM equipment WHERE asset_code=? COLLATE NOCASE",
                                 (asset_code.strip(),)).fetchone()
            borrower = conn.execute("SELECT * FROM borrowers WHERE borrower_code=? COLLATE NOCASE",
                                    (borrower_code.strip(),)).fetchone()
            if not asset:
                raise ValueError("Asset code was not found.")
            if not borrower or not borrower["active"]:
                raise ValueError("Borrower was not found or is inactive.")
            if asset["status"] != "Available":
                raise ValueError("This equipment is not available for checkout.")
            conn.execute("""INSERT INTO loans(asset_id,borrower_id,borrowed_on,due_on,status)
                            VALUES(?,?,?,?, 'Active')""",
                         (asset["asset_id"], borrower["borrower_id"], borrowed_on, due_on))
            conn.execute("UPDATE equipment SET status='Borrowed' WHERE asset_id=?",
                         (asset["asset_id"],))

    def return_loan(self, loan_id, returned_on):
        from validators import valid_iso_date
        if not valid_iso_date(returned_on):
            raise ValueError("Enter the return date as YYYY-MM-DD.")
        with get_connection() as conn:
            loan = conn.execute("SELECT * FROM loans WHERE loan_id=?", (loan_id,)).fetchone()
            if not loan or loan["status"] != "Active":
                raise ValueError("Active loan was not found.")
            if returned_on < loan["borrowed_on"]:
                raise ValueError("Return date cannot be before the borrowing date.")
            conn.execute("UPDATE loans SET returned_on=?,status='Returned' WHERE loan_id=?",
                         (returned_on, loan_id))
            conn.execute("UPDATE equipment SET status='Available' WHERE asset_id=?",
                         (loan["asset_id"],))

    def equipment(self, search=""):
        with get_connection() as conn:
            return conn.execute("""SELECT * FROM equipment
                WHERE asset_code LIKE ? OR name LIKE ? ORDER BY asset_code""",
                (f"%{search}%", f"%{search}%")).fetchall()

    def borrowers(self, search=""):
        with get_connection() as conn:
            return conn.execute("""SELECT * FROM borrowers
                WHERE borrower_code LIKE ? OR display_name LIKE ? ORDER BY display_name""",
                (f"%{search}%", f"%{search}%")).fetchall()

    def loans(self, search="", mode="all"):
                                                                        
        match mode:
            case "active":
                condition = "l.status='Active'"
            case "overdue":
                condition = "l.status='Active' AND l.due_on < date('now','localtime')"
            case "returned":
                condition = "l.status='Returned'"
            case _:
                condition = "1=1"
        with get_connection() as conn:
            return conn.execute(f"""SELECT l.loan_id,e.asset_code,e.name AS asset_name,
                b.borrower_code,b.display_name,l.borrowed_on,l.due_on,l.returned_on,l.status,
                CASE WHEN l.status='Active' AND l.due_on < date('now','localtime')
                     THEN 'Overdue' ELSE l.status END AS display_status
                FROM loans l JOIN equipment e ON e.asset_id=l.asset_id
                JOIN borrowers b ON b.borrower_id=l.borrower_id
                WHERE ({condition}) AND
                (e.asset_code LIKE ? OR e.name LIKE ? OR b.display_name LIKE ?)
                ORDER BY l.loan_id DESC""",
                (f"%{search}%", f"%{search}%", f"%{search}%")).fetchall()

    def dashboard_counts(self):
        with get_connection() as conn:
            total = conn.execute("SELECT COUNT(*) FROM equipment WHERE status!='Inactive'").fetchone()[0]
            available = conn.execute("SELECT COUNT(*) FROM equipment WHERE status='Available'").fetchone()[0]
            active = conn.execute("SELECT COUNT(*) FROM loans WHERE status='Active'").fetchone()[0]
            overdue = conn.execute("""SELECT COUNT(*) FROM loans
                WHERE status='Active' AND due_on < date('now','localtime')""").fetchone()[0]
            return {"Total equipment": total, "Available": available,
                    "Active loans": active, "Overdue": overdue}
