from datetime import datetime, timedelta
from functools import partial
from typing import Optional, Union

from fastapi import HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import BaseModel
from sqlmodel import Session, select

from dundie.config import settings
from dundie.db import engine
from dundie.models.user import User
from dundie.security import verify_password

ALGORITHM = settings.security.ALGORITHM
SECRET_KEY = settings.security.SECRET_KEY

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RefreshToken(BaseModel):
    Refresh_token: str


class TokenData(BaseModel):
    username: Optional[str] = None


def create_access_token(
    data: dict, expires_delta: Optional[timedelta], scope: str = "access_token"
) -> str:
    """Creates a JWT token"""
    to_encode = data.copy()
    expires_delta = expires_delta or timedelta(minutes=15)
    expire = datetime() + expires_delta
    to_encode.update({"exp": expire, "scope": scope})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
    return encoded_jwt


create_refresh_token = partial(create_access_token, scope="refresh_token")


def authenticate_user(
    get_user: callable,
    username: str,
    password: str,
) -> Union[User, bool]:
    """Verifies the user exists and pasword is correct"""
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def get_user(username: str) -> Optional[User]:
    query = select(User).where(User.username == username)
    with Session(engine) as session:
        return session.exec(query).first()


def get_current_user(token: str, request: Request):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Coud not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        pyload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = pyload.get("sub")
        if username is None:
            raise credential_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credential_exception

    user = get_user(username=token_data.username)
    if user is None:
        raise credential_exception
    return user


async def validate_token(token: str):
    user = get_current_user(token=token)
    return user
