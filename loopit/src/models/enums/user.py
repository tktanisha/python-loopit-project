from enum import Enum


class Role(str, Enum):
    user="user"
    lender="lender"
    admin="admin"