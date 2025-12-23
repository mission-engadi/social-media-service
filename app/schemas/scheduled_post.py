"""Pydantic schemas for ScheduledPost model.

Schemas define the structure of API requests and responses.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.scheduled_post import PostStatus, PostType


class ScheduledPostBase(BaseModel):
    """Base schema with common fields."""
    
    content_id: Optional[UUID] = Field(
        None,
        description="Optional link to Content Service content",
    )
    title: Optional[str] = Field(
        None,
        max_length=500,
        description="Post title",
    )
    text: str = Field(
        ...,
        min_length=1,
        description="Post text content",
    )
    media_urls: Optional[list[str]] = Field(
        None,
        description="Array of image/video URLs",
    )
    platforms: list[str] = Field(
        ...,
        min_items=1,
        description="Target platforms for this post",
    )
    post_type: PostType = Field(
        PostType.TEXT,
        description="Type of post",
    )
    scheduled_time: datetime = Field(
        ...,
        description="When to publish the post",
    )
    campaign_id: Optional[UUID] = Field(
        None,
        description="Optional campaign association",
    )


class ScheduledPostCreate(ScheduledPostBase):
    """Schema for creating a scheduled post.
    
    Used for POST requests.
    """
    social_account_ids: list[UUID] = Field(
        ...,
        min_items=1,
        description="Social accounts to publish to",
    )


class ScheduledPostUpdate(BaseModel):
    """Schema for updating a scheduled post.
    
    Used for PUT/PATCH requests.
    All fields are optional for partial updates.
    """
    
    title: Optional[str] = Field(None, max_length=500)
    text: Optional[str] = Field(None, min_length=1)
    media_urls: Optional[list[str]] = None
    platforms: Optional[list[str]] = Field(None, min_items=1)
    post_type: Optional[PostType] = None
    scheduled_time: Optional[datetime] = None
    status: Optional[PostStatus] = None
    campaign_id: Optional[UUID] = None
    social_account_ids: Optional[list[UUID]] = Field(None, min_items=1)


class ScheduledPostResponse(ScheduledPostBase):
    """Schema for scheduled post responses.
    
    Used for GET requests.
    Includes database fields like id and timestamps.
    """
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    published_time: Optional[datetime] = None
    status: PostStatus
    buffer_post_ids: Optional[dict] = None
    platform_post_ids: Optional[dict] = None
    error_message: Optional[str] = None
    created_by: UUID
    created_at: datetime
    updated_at: datetime


class ScheduledPostWithAnalytics(ScheduledPostResponse):
    """Schema with analytics data included.
    
    For detailed views with performance metrics.
    """
    
    total_likes: int = Field(0, description="Total likes across all platforms")
    total_shares: int = Field(0, description="Total shares across all platforms")
    total_comments: int = Field(0, description="Total comments across all platforms")
    total_reach: int = Field(0, description="Total reach across all platforms")
    avg_engagement_rate: Optional[float] = Field(
        None,
        description="Average engagement rate across all platforms",
    )
