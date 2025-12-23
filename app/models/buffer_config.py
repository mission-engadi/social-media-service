"""BufferConfig database model.

Manages Buffer API configuration and credentials.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class BufferConfig(Base):
    """Buffer API configuration model.
    
    Stores Buffer API credentials and configuration for integration.
    Each organization or user can have their own Buffer configuration.
    
    Attributes:
        access_token: Buffer API access token (encrypted)
        refresh_token: Buffer API refresh token (encrypted)
        token_expires_at: Token expiration timestamp
        organization_id: Buffer organization ID
        is_active: Whether this configuration is active
        created_by: User who created this configuration
    """
    
    __tablename__ = "buffer_configs"
    
    access_token: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )  # TODO: Implement encryption
    refresh_token: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )  # TODO: Implement encryption
    token_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )
    organization_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
    )
    created_by: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    def __repr__(self) -> str:
        return (
            f"<BufferConfig(id={self.id}, "
            f"is_active={self.is_active}, "
            f"organization_id='{self.organization_id}')>"
        )
