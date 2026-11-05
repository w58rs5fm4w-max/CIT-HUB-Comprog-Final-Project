# CIT HUB
**School Resource Borrowing & Inventory Management System**

A local Python desktop application for managing school equipment, borrowers, checkouts, returns, and overdue loans.

## Requirements
- Python 3.10 or newer (the project uses `match-case`)
- Tkinter (normally included with standard Python installations)
- SQLite (included through Python's `sqlite3` module)

No third-party Python packages are required.

## Run the application
1. Extract the `CIT_HUB` folder.
2. Open a terminal or command prompt inside the folder.
3. Run:

   ```bash
   python main.py
   ```

4. The database is created automatically at `data/cit_hub.db`.

## Main features
- Equipment: add, list, search, update, and deactivate (records are retained).
- Borrowers: register and search using unique borrower codes.
- Checkout: only available equipment and active borrowers can be checked out.
- Return: records a return date and restores equipment availability.
- Monitoring: dashboard counts, active loans, overdue loans, and returned history.
- CSV: export the inventory list.

## Date format
Enter dates as `YYYY-MM-DD`, for example `2026-11-05`.

## Suggested demonstration sequence
1. Add an asset with a unique asset code.
2. Try adding the same code again; the database should reject the duplicate.
3. Add a fictional test borrower.
4. Check out the available asset.
5. Try checking it out again; the system should block the second checkout.
6. Record a return and confirm the asset becomes available.
7. Close and reopen the program to verify persistence.
8. Select the overdue view and demonstrate an overdue test loan (use a due date in the past).

## Database
The SQLite database contains:
- `equipment`: one row per physical asset.
- `borrowers`: one row per borrower.
- `loans`: one row per checkout transaction.

Foreign keys and unique constraints are enabled. SQL values are passed using parameterized queries.

## Backup and reset
- **Backup:** close the application and copy `data/cit_hub.db` to a safe location.
- **Reset:** close the application and remove `data/cit_hub.db`. The app will create a fresh database next time it starts. This permanently removes local records.

## Notes
- Use fictional or instructor-approved borrower test data.
- This is a local classroom project, not a production multi-user system.
- Keep the project folder together so the database path remains correct.
