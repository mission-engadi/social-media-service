"""API endpoints package.

Exports all endpoint routers for version 1.
"""

from app.api.v1.endpoints import (
    health,
    social_accounts,
    scheduled_posts,
    post_analytics,
    campaigns,
    buffer_config,
)

__all__ = [
    "health",
    "social_accounts",
    "scheduled_posts",
    "post_analytics",
    "campaigns",
    "buffer_config",
]
