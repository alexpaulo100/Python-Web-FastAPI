from fastapi import FastAPI
from dundie.routes.user import router as user_router


from dundie.db import ActiveSession
from sqlmodel import Session, select

from dundie.models import User
from dundie.models.user import UserResponse


app = FastAPI(
    title="dundie",
    version="0.1.0",
    description="dundie is a rewards API",
)

app.include_router(user_router, prefix="/user", tags=["user"])
