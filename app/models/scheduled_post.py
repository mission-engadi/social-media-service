"""ScheduledPost database model.

Manages scheduled social media posts.
"""

from datetime import datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.campaign import Campaign
    from app.models.post_analytics import PostAnalytics
    from app.models.social_account import SocialAccount


class PostType(str, PyEnum):
    """Post type enum."""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    LINK = "link"
    CAROUSEL = "carousel"


class PostStatus(str, PyEnum):
    """Post status enum."""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ScheduledPost(Base):
    """Scheduled social media post model.
    
    Stores posts scheduled for publishing to social media platforms.
    Integrates with Buffer for scheduling and tracks publishing status.
    
    Attributes:
        content_id: Optional link to Content Service content
        title: Post title (optional)
        text: Post text content
        media_urls: Array of image/video URLs
        platforms: Target platforms for this post
        post_type: Type of post (text, image, video, etc.)
        scheduled_time: When to publish the post
        published_time: When the post was actually published
        status: Current post status
        buffer_post_ids: Buffer post IDs per platform
        platform_post_ids: Platform-specific post IDs after publishing
        campaign_id: Optional campaign association
        error_message: Error details if publication failed
        created_by: User who created this post
    """
    
    __tablename__ = "scheduled_posts"
    
    content_id: Mapped[Optional[UUID]] = mapped_column(
        nullable=True,
        index=True,
    )  # FK to Content Service (external)
    title: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    media_urls: Mapped[Optional[list[str]]] = mapped_column(
        ARRAY(String),
        nullable=True,
    )
    platforms: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
    )
    post_type: Mapped[PostType] = mapped_column(
        Enum(PostType),
        nullable=False,
        default=PostType.TEXT,
    )
    scheduled_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )
    published_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )
    status: Mapped[PostStatus] = mapped_column(
        Enum(PostStatus),
        nullable=False,
        default=PostStatus.DRAFT,
        index=True,
    )
    buffer_post_ids: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
    )  # {"facebook": "buffer_id", "twitter": "buffer_id"}
    platform_post_ids: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
    )  # {"facebook": "fb_post_id", "twitter": "tweet_id"}
    campaign_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("campaigns.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    created_by: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Relationships
    campaign: Mapped[Optional["Campaign"]] = relationship(
        "Campaign",
        back_populates="scheduled_posts",
    )
    analytics: Mapped[list["PostAnalytics"]] = relationship(
        "PostAnalytics",
        back_populates="scheduled_post",
        cascade="all, delete-orphan",
    )
    social_accounts: Mapped[list["SocialAccount"]] = relationship(
        "SocialAccount",
        back_populates="scheduled_posts",
        secondary="scheduled_post_accounts",
    )
    
    def __repr__(self) -> str:
        return (
            f"<ScheduledPost(id={self.id}, "
            f"status='{self.status.value}', "
            f"scheduled='{self.scheduled_time}')>"
        )
