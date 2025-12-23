"""User database model.

Basic user model for authentication and ownership tracking.
This is a minimal model - extend based on your auth service needs.
"""

from typing import Optional

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class User(Base):
    """User model for authentication and ownership.
    
    This is a basic user model. In production, you may want to:
    - Sync with an external Auth Service
    - Add more fields (email, name, etc.)
    - Implement proper password hashing
    
    Attributes:
        email: User email address
        username: User username
        is_active: Whether the user account is active
        is_superuser: Whether the user has admin privileges
    """
    
    __tablename__ = "users"
    
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )
    username: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    
    def __repr__(self) -> str:
        return (
            f"<User(id={self.id}, "
            f"username='{self.username}', "
            f"email='{self.email}')>"
        )
