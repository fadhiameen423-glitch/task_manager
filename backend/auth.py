import uuid
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext

import database


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

sessions = {}


def hash_password(password: str):
    password = password[:72]
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    plain_password = plain_password[:72]
    return pwd_context.verify(plain_password, hashed_password)


def create_token(email: str):
    token = str(uuid.uuid4())
    sessions[token] = email
    return token


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    if token not in sessions:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    email = sessions[token]
    user = database.get_user_by_email(email)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return user