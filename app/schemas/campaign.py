"""Pydantic schemas for Campaign model.

Schemas define the structure of API requests and responses.
"""

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.campaign import CampaignStatus, CampaignType


class CampaignBase(BaseModel):
    """Base schema with common fields."""
    
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Campaign name",
    )
    description: Optional[str] = Field(
        None,
        description="Campaign description",
    )
    campaign_type: CampaignType = Field(
        CampaignType.GENERAL,
        description="Type of campaign",
    )
    start_date: date = Field(
        ...,
        description="Campaign start date",
    )
    end_date: Optional[date] = Field(
        None,
        description="Campaign end date (optional)",
    )
    target_platforms: list[str] = Field(
        ...,
        min_items=1,
        description="Platforms targeted by this campaign",
    )
    goals: Optional[dict] = Field(
        None,
        description="Campaign goals and KPIs",
    )
    tags: Optional[list[str]] = Field(
        None,
        description="Campaign tags for organization",
    )


class CampaignCreate(CampaignBase):
    """Schema for creating a campaign.
    
    Used for POST requests.
    """
    pass


class CampaignUpdate(BaseModel):
    """Schema for updating a campaign.
    
    Used for PUT/PATCH requests.
    All fields are optional for partial updates.
    """
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    campaign_type: Optional[CampaignType] = None
    status: Optional[CampaignStatus] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    target_platforms: Optional[list[str]] = Field(None, min_items=1)
    goals: Optional[dict] = None
    tags: Optional[list[str]] = None


class CampaignResponse(CampaignBase):
    """Schema for campaign responses.
    
    Used for GET requests.
    Includes database fields like id and timestamps.
    """
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    status: CampaignStatus
    created_by: UUID
    created_at: datetime
    updated_at: datetime


class CampaignWithStats(CampaignResponse):
    """Campaign with statistics.
    
    Includes post counts and performance metrics.
    """
    
    total_posts: int = Field(0, description="Total posts in campaign")
    published_posts: int = Field(0, description="Published posts")
    scheduled_posts: int = Field(0, description="Scheduled posts")
    draft_posts: int = Field(0, description="Draft posts")
    total_reach: int = Field(0, description="Total reach across all posts")
    total_engagement: int = Field(
        0,
        description="Total engagement (likes + shares + comments)",
    )
