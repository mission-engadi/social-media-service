"""SocialAccount database model.

Manages social media accounts and their credentials.
"""

from datetime import datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.scheduled_post import ScheduledPost
    from app.models.post_analytics import PostAnalytics


class SocialPlatform(str, PyEnum):
    """Social media platforms enum."""
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"


class AccountStatus(str, PyEnum):
    """Social account status enum."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISCONNECTED = "disconnected"
    ERROR = "error"


class SocialAccount(Base):
    """Social media account model.
    
    Stores social media account information and credentials.
    Supports multiple platforms with OAuth tokens and Buffer integration.
    
    Attributes:
        platform: Social media platform (facebook, twitter, etc.)
        account_name: Display name of the account
        account_handle: Username/handle (e.g., @username)
        account_id: Platform-specific account ID
        status: Current account status
        access_token: OAuth access token (encrypted)
        refresh_token: OAuth refresh token (encrypted)
        token_expires_at: Token expiration timestamp
        buffer_profile_id: Buffer profile ID for this account
        is_primary: Whether this is the primary account for the platform
        platform_metadata: Additional platform-specific data
        created_by: User who added this account
    """
    
    __tablename__ = "social_accounts"
    
    platform: Mapped[SocialPlatform] = mapped_column(
        Enum(SocialPlatform),
        nullable=False,
        index=True,
    )
    account_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    account_handle: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    account_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )
    status: Mapped[AccountStatus] = mapped_column(
        Enum(AccountStatus),
        nullable=False,
        default=AccountStatus.ACTIVE,
        index=True,
    )
    access_token: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )  # TODO: Implement encryption
    refresh_token: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )  # TODO: Implement encryption
    token_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    buffer_profile_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )
    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    platform_metadata: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
    )
    created_by: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Relationships
    scheduled_posts: Mapped[list["ScheduledPost"]] = relationship(
        "ScheduledPost",
        back_populates="social_accounts",
        secondary="scheduled_post_accounts",
    )
    post_analytics: Mapped[list["PostAnalytics"]] = relationship(
        "PostAnalytics",
        back_populates="social_account",
    )
    
    def __repr__(self) -> str:
        return (
            f"<SocialAccount(id={self.id}, "
            f"platform='{self.platform.value}', "
            f"handle='{self.account_handle}', "
            f"status='{self.status.value}')>"
        )
