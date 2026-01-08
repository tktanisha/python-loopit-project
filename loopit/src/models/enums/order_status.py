
from enum import Enum

class OrderStatus(str, Enum):
    InUse = "In Use"
    ReturnRequested = "Return Requested"
    Returned = "Returned"
