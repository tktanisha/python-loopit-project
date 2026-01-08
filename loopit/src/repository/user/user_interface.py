from abc import ABC,abstractmethod
from models.user import User
from typing import List



class UserRepo(ABC):

    @abstractmethod
    def create(self,user:User) ->None:
        ...

    @abstractmethod
    def find_by_email(self, email: str) -> User:
        ...    

    @abstractmethod
    async def find_by_id(self, id:int)->User:
        ...     

    @abstractmethod
    async def delete_by_id(self, user_id: int) -> None:  
        ...

    @abstractmethod
    async def become_lender(self, user_id: int) -> None:
        ...

    @abstractmethod
    async def find_all(self, filters: dict) -> List[User]:
        ...
        
                  