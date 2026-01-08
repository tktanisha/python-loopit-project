
# enums/return_status.py
from enum import Enum

class ReturnStatus(str, Enum):
    Pending = "Pending"
    Approved = "Approved"
    Rejected = "Rejected"
