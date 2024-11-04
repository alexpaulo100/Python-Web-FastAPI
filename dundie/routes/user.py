from typing import List

from fastapi import APIRouter
from sqlmodel import Session, select

from dundie.db import ActiveSession
from dundie.models.user import User, UserResponse

router = APIRouter()


@router.get("/")
async def list_users(*, session: Session = ActiveSession) -> List[UserResponse]:
    """List all users from database"""
    users = session.exec(select(User)).all()
    return users
