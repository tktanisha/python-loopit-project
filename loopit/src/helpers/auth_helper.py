from datetime import datetime, timedelta, timezone
import bcrypt
from fastapi import HTTPException, status,Request
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt
from loopit.src.helpers.app_settings import AppSettings

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/api/v1/login")

class AuthHelper:

    @staticmethod
    def hash_password(password: str) -> str:
        password_bytes = password.encode("utf-8")
        hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        ) 

    @staticmethod
    def create_token(user_id: str, role: str) -> str:
        now = datetime.now(timezone.utc)
        print(f"{AppSettings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES}")
        payload = {
            "user_id": str(user_id),
            "role": str(role),
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=int(AppSettings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES))).timestamp()),
        }
        return jwt.encode(payload, AppSettings.JWT_SECRET_KEY, algorithm=AppSettings.JWT_ALGORITHM)

    @staticmethod
    def verify_jwt(request: Request):
        header = request.headers.get("Authorization")
        if not header or not header.startswith("Bearer "):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header is missing or invalid")

        token = header.split(" ")[1]
        try:
            claims = jwt.decode(token, AppSettings.JWT_SECRET_KEY, algorithms=[AppSettings.JWT_ALGORITHM])
        except ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid or token expired")
        except JWTError as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

        request.state.user = claims
