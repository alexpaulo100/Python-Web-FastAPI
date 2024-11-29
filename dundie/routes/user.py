from typing import List

from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select

from dundie.auth import AuthenticatedUser, SuperUser, CanChangeUserPassword
from dundie.db import ActiveSession
from dundie.models.user import (
    User,
    UserRequest,
    UserResponse,
    UserProfilePatchRequest,
    UserPasswordPatchRequest,
)

router = APIRouter()


@router.get("/", reponse_model=List[UserResponse], dependecies=[AuthenticatedUser])
async def list_users(*, session: Session = ActiveSession) -> List[UserResponse]:
    """List all users from database"""
    users = session.exec(select(User)).all()
    return users


@router.get("/{username}/", response_model=UserResponse)
async def get_user_by_username(
    *,
    session: Session = ActiveSession,
    username: str,
):
    """Get single user by username"""
    query = select(User).where(User.username == username)
    user = session.exec(query).first()
    return user


@router.post(
    "/", response_model=UserResponse, status_code=201, dependencies=[SuperUser]
)
async def create_user(*, session: Session = ActiveSession, user: UserRequest):
    """ "Creates a new user."""
    if session.exec(select(User).where(User.email == user.email)).first():
        raise HTTPException(status_code=409, detail="User email already exists.")
    db_user = User.from_orm(user)
    session.add(db_user)
    try:
        session.commit()
    except ItegrityError:  # noqa: F821
        raise HTTPException(status_code=500, detail="Databse IntegrityError")
    session.refresh(db_user)
    return db_user


@router.patch("/{username}/", response_model=UserResponse)
async def update_user(
    *,
    session: Session = ActiveSession,
    patch_data: UserProfilePatchRequest,
    current_user: User = AuthenticatedUser,
    username: str,
):
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id != current_user.id and not current_user.superuser:
        raise HTTPException(
            status_code=403, detail="You can only update your own profile"
        )

    if patch_data.avatar is not None:
        user.avatar = patch_data.avatar
    if patch_data.bio is not None:
        user.bio = patch_data.bio

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.post("/{username}/password/", response_model=UserResponse)
async def change_password(
    *,
    session: Session = ActiveSession,
    patch_data: UserPasswordPatchRequest,
    user: User = CanChangeUserPassword,
):
    user.password = patch_data.hashed_password
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
