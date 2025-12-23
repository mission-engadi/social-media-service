"""API router configuration.

This module aggregates all API routers for version 1.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    health,
    social_accounts,
    scheduled_posts,
    post_analytics,
    campaigns,
    buffer_config,
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    health.router,
    tags=["health"],
)

# Social Media Management endpoints
api_router.include_router(
    social_accounts.router,
    prefix="/social-accounts",
    tags=["social-accounts"],
)

api_router.include_router(
    scheduled_posts.router,
    prefix="/posts",
    tags=["posts"],
)

api_router.include_router(
    post_analytics.router,
    prefix="/analytics",
    tags=["analytics"],
)

api_router.include_router(
    campaigns.router,
    prefix="/campaigns",
    tags=["campaigns"],
)

api_router.include_router(
    buffer_config.router,
    prefix="/buffer",
    tags=["buffer"],
)
