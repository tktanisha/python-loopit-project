from enum import Enum

class BuyRequestStatus(str,Enum):
    Pending="Pending"
    Approved="Approved"
    Rejected="Rejected"