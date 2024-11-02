"""User related data models"""
from typing import Optional
from sqlmodel import Field, SQLModel # type: ignore

class User(SQLModel, table=True):
    """Represents the User Model"""

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, nullable=False)
    username: str = Field(unique=True, nullable=False)
    avatar: Optional[str] = None
    bio: Optional[str] = None
    password: str = Field(nullable=False)
    name: str = Field(nullable=False)
    dept: str = Field(nullable=False)
    currency: str = Field(nullable=False)

    @property
    def superuser(self):
        """"Users belonging to management dept are admins."""
        return self.dept == "management"
    

     
    def generate_username(name: str) -> str:
        """Generate a slug from user.name.
        "Manoel Santos" -> "manoel-santos"
        "Maria José" -> "maria-jose"
        "Antônio Silva" -> "antonio-silva"
        "Márcio Oliveira" -> "marcio-oliveira"
        """
        return name.lower().replace(" ", "-")
    

