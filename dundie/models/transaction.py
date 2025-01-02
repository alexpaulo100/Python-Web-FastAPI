from datetime import datetime, UTC
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from dundie.models.user import User


class Transaction(SQLModel, table=True):
    """Represents the transaction Model"""

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False)
    from_id: int = Field(foreign_key="user.id", nullable=False)
    value: int = Field(nullable=False)
    date: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)

    # Populates a '.incomes' on 'User'
    user: Optional["User"] = Relationship(
        back_populates="incomes",
        sa_relationship_kwargs={"primaryjoin": "Transaction.user_id == User.id"},
    )
    # Populates a '.expenses' on 'User'
    from_user: Optional["User"] = Relationship(
        back_populates="expenses",
        sa_relationship_kwargs={"primaryjoin": "Transaction.from_id == User.id"},
    )


class Balance(SQLModel, table=True):
    """Store the balance of a user accont"""

    user_id: int = Field(
        foreign_key="user.id",
        nullable=False,
        primary_key=True,
        unique=True,
    )

    value: int = Field(nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.now(UTC),
        nullable=False,
        sa_column_kwargs={"onupdate": datetime.now(UTC)},
    )
    # Populates a '._balance' on 'User'
    user: Optional["User"] = Relationship(back_populates="_balance")
