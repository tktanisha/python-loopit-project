from service.auth.auth_interface import AuthService
from repository.user.user_interface import UserRepo
from models.user import User
from helpers.auth_helper import AuthHelper
import logging
from exception.user import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
    AuthServiceError,
    UserNotFoundError
)

logger = logging.getLogger(__name__)

class AuthServiceImple(AuthService):

    def __init__(self, user_repo: UserRepo):
        self.user_repo = user_repo

    async def register(self, user: User) -> None:
        print("user in service=",user)
        try:
            user_db = self.user_repo.find_by_email(user.email)

            if user_db:
                raise UserAlreadyExistsError("user already exists")

        except UserNotFoundError:
            pass

        except UserAlreadyExistsError:
            raise

        except Exception as e:
            raise AuthServiceError("failed to verify existing user") from e

        user.password_hash = AuthHelper.hash_password(user.password_hash)

        try:
            self.user_repo.create(user)
        except Exception as e:
            raise AuthServiceError("failed to register user") from e
        

    async def login(self, email: str, password: str):
        print(email,password)
        try:
            user = self.user_repo.find_by_email(email)
        except UserNotFoundError:
            raise InvalidCredentialsError("invalid credentials")

        except Exception as e:
            logger.exception("real error during login")
            raise 

        if not AuthHelper.verify_password(password, user.password_hash):
            logger.info("password invalid")
            raise InvalidCredentialsError("invalid credentials")

        try:
            token = AuthHelper.create_token(user.id, user.role.value)
        except Exception as e:
            logger.exception("jwt in service=",e)
            raise AuthServiceError("failed to generate token") from e

        return token, user
