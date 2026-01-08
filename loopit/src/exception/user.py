
class UserNotFoundError(Exception):
    pass


class UserAlreadyExistsError(Exception):
    pass


class UserRepositoryError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class AuthServiceError(Exception):
    pass