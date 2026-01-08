from abc import ABC,abstractmethod
from models.user import User
from typing import Tuple

class AuthService(ABC):

    @abstractmethod
    def login(self, email: str, password: str)-> None:
        ...

    @abstractmethod
    def register(self, user: User)->  Tuple[str, User]:
        ...
