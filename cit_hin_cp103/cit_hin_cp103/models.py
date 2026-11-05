"""Simple domain model classes used by CIT HUB."""
from dataclasses import dataclass

@dataclass
class Equipment:
    asset_code: str
    name: str
    category: str
    location: str
    condition: str = "Good"

@dataclass
class Borrower:
    borrower_code: str
    display_name: str
    department_or_program: str

@dataclass
class Loan:
    asset_id: int
    borrower_id: int
    borrowed_on: str
    due_on: str
