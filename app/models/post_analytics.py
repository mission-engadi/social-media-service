"""PostAnalytics database model.

Tracks social media post performance and engagement metrics.
"""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.scheduled_post import ScheduledPost
    from app.models.social_account import SocialAccount


class PostAnalytics(Base):
    """Post analytics model.
    
    Stores engagement metrics and analytics for published social media posts.
    Tracks likes, shares, comments, reach, and other platform-specific metrics.
    
    Attributes:
        scheduled_post_id: Link to the scheduled post
        social_account_id: Link to the social account
        platform: Platform name
        platform_post_id: Platform-specific post ID
        likes: Number of likes/reactions
        shares: Number of shares/retweets
        comments: Number of comments
        clicks: Number of link clicks
        reach: Number of unique users reached
        impressions: Total number of times post was displayed
        engagement_rate: Calculated engagement rate percentage
        collected_at: When these metrics were collected
        raw_data: Full raw analytics data from platform
    """
    
    __tablename__ = "post_analytics"
    
    scheduled_post_id: Mapped[UUID] = mapped_column(
        ForeignKey("scheduled_posts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    social_account_id: Mapped[UUID] = mapped_column(
        ForeignKey("social_accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    platform: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    platform_post_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    likes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    shares: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    comments: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    clicks: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    reach: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    impressions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    engagement_rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),  # 5 digits, 2 decimal places (e.g., 100.00)
        nullable=True,
    )
    collected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )
    raw_data: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
    )
    
    # Relationships
    scheduled_post: Mapped["ScheduledPost"] = relationship(
        "ScheduledPost",
        back_populates="analytics",
    )
    social_account: Mapped["SocialAccount"] = relationship(
        "SocialAccount",
        back_populates="post_analytics",
    )
    
    def __repr__(self) -> str:
        return (
            f"<PostAnalytics(id={self.id}, "
            f"platform='{self.platform}', "
            f"likes={self.likes}, "
            f"shares={self.shares})>"
        )
