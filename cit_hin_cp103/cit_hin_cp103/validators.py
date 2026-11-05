"""Input validation helpers."""
from datetime import date
import re


def required(values):
    return [name for name, value in values.items() if not str(value).strip()]


def valid_iso_date(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value.strip()):
        return False
    try:
        date.fromisoformat(value.strip())
        return True
    except ValueError:
        return False


def validate_loan_dates(borrowed_on, due_on):
    if not valid_iso_date(borrowed_on) or not valid_iso_date(due_on):
        return False, "Use valid dates in YYYY-MM-DD format."
    if date.fromisoformat(due_on.strip()) < date.fromisoformat(borrowed_on.strip()):
        return False, "Due date cannot be earlier than the borrowing date."
    return True, ""
