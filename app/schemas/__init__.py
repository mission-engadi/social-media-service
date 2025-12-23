"""Pydantic schemas for request/response validation."""

from app.schemas.buffer_config import (
    BufferConfigCreate,
    BufferConfigResponse,
    BufferConfigUpdate,
    BufferConfigWithTokens,
)
from app.schemas.campaign import (
    CampaignCreate,
    CampaignResponse,
    CampaignUpdate,
    CampaignWithStats,
)
from app.schemas.post_analytics import (
    PlatformAnalyticsSummary,
    PostAnalyticsCreate,
    PostAnalyticsResponse,
    PostAnalyticsUpdate,
)
from app.schemas.scheduled_post import (
    ScheduledPostCreate,
    ScheduledPostResponse,
    ScheduledPostUpdate,
    ScheduledPostWithAnalytics,
)
from app.schemas.social_account import (
    SocialAccountCreate,
    SocialAccountResponse,
    SocialAccountUpdate,
    SocialAccountWithTokens,
)

__all__ = [
    # Social Account
    "SocialAccountCreate",
    "SocialAccountUpdate",
    "SocialAccountResponse",
    "SocialAccountWithTokens",
    # Scheduled Post
    "ScheduledPostCreate",
    "ScheduledPostUpdate",
    "ScheduledPostResponse",
    "ScheduledPostWithAnalytics",
    # Post Analytics
    "PostAnalyticsCreate",
    "PostAnalyticsUpdate",
    "PostAnalyticsResponse",
    "PlatformAnalyticsSummary",
    # Campaign
    "CampaignCreate",
    "CampaignUpdate",
    "CampaignResponse",
    "CampaignWithStats",
    # Buffer Config
    "BufferConfigCreate",
    "BufferConfigUpdate",
    "BufferConfigResponse",
    "BufferConfigWithTokens",
]
