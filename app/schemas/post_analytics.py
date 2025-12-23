"""Pydantic schemas for PostAnalytics model.

Schemas define the structure of API requests and responses.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PostAnalyticsBase(BaseModel):
    """Base schema with common fields."""
    
    scheduled_post_id: UUID = Field(
        ...,
        description="Link to the scheduled post",
    )
    social_account_id: UUID = Field(
        ...,
        description="Link to the social account",
    )
    platform: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Platform name",
    )
    platform_post_id: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Platform-specific post ID",
    )
    likes: int = Field(
        0,
        ge=0,
        description="Number of likes/reactions",
    )
    shares: int = Field(
        0,
        ge=0,
        description="Number of shares/retweets",
    )
    comments: int = Field(
        0,
        ge=0,
        description="Number of comments",
    )
    clicks: int = Field(
        0,
        ge=0,
        description="Number of link clicks",
    )
    reach: int = Field(
        0,
        ge=0,
        description="Number of unique users reached",
    )
    impressions: int = Field(
        0,
        ge=0,
        description="Total number of times post was displayed",
    )
    engagement_rate: Optional[Decimal] = Field(
        None,
        description="Calculated engagement rate percentage",
    )
    collected_at: datetime = Field(
        ...,
        description="When these metrics were collected",
    )
    raw_data: Optional[dict] = Field(
        None,
        description="Full raw analytics data from platform",
    )


class PostAnalyticsCreate(PostAnalyticsBase):
    """Schema for creating post analytics.
    
    Used for POST requests.
    """
    pass


class PostAnalyticsUpdate(BaseModel):
    """Schema for updating post analytics.
    
    Used for PUT/PATCH requests.
    All fields are optional for partial updates.
    """
    
    likes: Optional[int] = Field(None, ge=0)
    shares: Optional[int] = Field(None, ge=0)
    comments: Optional[int] = Field(None, ge=0)
    clicks: Optional[int] = Field(None, ge=0)
    reach: Optional[int] = Field(None, ge=0)
    impressions: Optional[int] = Field(None, ge=0)
    engagement_rate: Optional[Decimal] = None
    collected_at: Optional[datetime] = None
    raw_data: Optional[dict] = None


class PostAnalyticsResponse(PostAnalyticsBase):
    """Schema for post analytics responses.
    
    Used for GET requests.
    Includes database fields like id and timestamps.
    """
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    created_at: datetime


class PlatformAnalyticsSummary(BaseModel):
    """Summary analytics for a specific platform."""
    
    platform: str
    total_posts: int
    total_likes: int
    total_shares: int
    total_comments: int
    total_reach: int
    total_impressions: int
    avg_engagement_rate: Optional[float]
