"""Campaign database model.

Manages social media campaigns and coordinated posts.
"""

from datetime import date
from enum import Enum as PyEnum
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Date, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.scheduled_post import ScheduledPost


class CampaignType(str, PyEnum):
    """Campaign type enum."""
    AWARENESS = "awareness"
    FUNDRAISING = "fundraising"
    EVENT = "event"
    GENERAL = "general"


class CampaignStatus(str, PyEnum):
    """Campaign status enum."""
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Campaign(Base):
    """Social media campaign model.
    
    Organizes multiple scheduled posts into coordinated campaigns.
    Tracks campaign goals, target platforms, and performance.
    
    Attributes:
        name: Campaign name
        description: Campaign description
        campaign_type: Type of campaign (awareness, fundraising, etc.)
        status: Current campaign status
        start_date: Campaign start date
        end_date: Campaign end date (optional)
        target_platforms: Platforms targeted by this campaign
        goals: Campaign goals and KPIs
        tags: Campaign tags for organization
        created_by: User who created this campaign
    """
    
    __tablename__ = "campaigns"
    
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    campaign_type: Mapped[CampaignType] = mapped_column(
        Enum(CampaignType),
        nullable=False,
        default=CampaignType.GENERAL,
        index=True,
    )
    status: Mapped[CampaignStatus] = mapped_column(
        Enum(CampaignStatus),
        nullable=False,
        default=CampaignStatus.DRAFT,
        index=True,
    )
    start_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )
    end_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        index=True,
    )
    target_platforms: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
    )
    goals: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
    )  # {"reach": 10000, "engagement_rate": 5.0, "conversions": 100}
    tags: Mapped[Optional[list[str]]] = mapped_column(
        ARRAY(String),
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
        back_populates="campaign",
    )
    
    def __repr__(self) -> str:
        return (
            f"<Campaign(id={self.id}, "
            f"name='{self.name}', "
            f"status='{self.status.value}')>"
        )
