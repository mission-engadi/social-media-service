"""Database models.

Import all models here for Alembic migrations to work properly.
"""

from app.models.buffer_config import BufferConfig
from app.models.campaign import Campaign, CampaignStatus, CampaignType
from app.models.post_analytics import PostAnalytics
from app.models.scheduled_post import PostStatus, PostType, ScheduledPost
from app.models.scheduled_post_accounts import scheduled_post_accounts
from app.models.social_account import (
    AccountStatus,
    SocialAccount,
    SocialPlatform,
)
from app.models.user import User

__all__ = [
    "User",
    "SocialAccount",
    "SocialPlatform",
    "AccountStatus",
    "ScheduledPost",
    "PostType",
    "PostStatus",
    "PostAnalytics",
    "Campaign",
    "CampaignType",
    "CampaignStatus",
    "BufferConfig",
    "scheduled_post_accounts",
]
