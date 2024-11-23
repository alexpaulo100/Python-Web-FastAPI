from datetime import datetime, timedelta
from functools import partial
from typing import Optional, Union

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
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
    if expires_delta:
        expires_delta = datetime() + expires_delta
    else:
        expire = datetime() + timedelta(minutes=15)
    to_encode.update({"exp": expire, "scope": scope})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


create_refresh_token = partial(create_access_token, scope="refresh_token")


def authenticate_user(
    get_user: callable,
    username: str,
    password: str,
) -> Union[User, bool]:
    """Authenticate the user"""
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


def get_current_user(
    token: str = Depends(oauth2_scheme), request: Request = None, fresh=False
) -> User:
    """Get current user authenticated"""
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Coud not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if request:
        if authorization := request.headers.get("authorization"):
            try:
                token = authorization.split(" ")[1]
            except IndexError:
                raise credential_exception
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
    if fresh and (not pyload["fresh"] and not user.superuser):
        raise credential_exception
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Wraps the sinc get_active_user for sync calls"""
    return current_user


AuthenticatedUser = Depends(get_current_active_user)


async def get_current_super_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Wraps the sinc get_active_user for sync calls"""
    if not current_user.superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not a super user"
        )
    return current_user


SuperUser = Depends(get_current_super_user)


async def validate_token(token: str = Depends(oauth2_scheme)) -> User:
    """Validates user token"""
    user = get_current_user(token=token)
    return user
