"""Post Analytics API endpoints.

Provides REST API for managing post analytics.
"""

import logging
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.auth import CurrentUser, get_current_user
from app.schemas.post_analytics import (
    PostAnalyticsCreate,
    PostAnalyticsUpdate,
    PostAnalyticsResponse,
)
from app.services.post_analytics_service import PostAnalyticsService
from app.services.scheduled_post_service import ScheduledPostService
from app.services.buffer_config_service import BufferConfigService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "",
    response_model=PostAnalyticsResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record analytics",
    description="Record analytics data for a post",
)
async def create_analytics(
    analytics_data: PostAnalyticsCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Record analytics for a post."""
    service = PostAnalyticsService(db)
    post_service = ScheduledPostService(db)
    
    # Verify post ownership
    post = await post_service.get_post(analytics_data.post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post {analytics_data.post_id} not found",
        )
    
    if post.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to record analytics for this post",
        )
    
    try:
        analytics = await service.create_analytics(analytics_data)
        return analytics
    except Exception as e:
        logger.error(f"Failed to create analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create analytics: {str(e)}",
        )


@router.get(
    "/{analytics_id}",
    response_model=PostAnalyticsResponse,
    summary="Get analytics",
    description="Get analytics record by ID",
)
async def get_analytics(
    analytics_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get analytics by ID."""
    service = PostAnalyticsService(db)
    post_service = ScheduledPostService(db)
    
    analytics = await service.get_analytics(analytics_id)
    if not analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analytics {analytics_id} not found",
        )
    
    # Verify ownership through post
    post = await post_service.get_post(analytics.post_id)
    if not post or post.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this analytics",
        )
    
    return analytics


@router.get(
    "/posts/{post_id}/analytics",
    response_model=List[PostAnalyticsResponse],
    summary="Get post analytics",
    description="Get all analytics for a specific post",
)
async def get_post_analytics(
    post_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get analytics for a specific post."""
    service = PostAnalyticsService(db)
    post_service = ScheduledPostService(db)
    
    # Verify post ownership
    post = await post_service.get_post(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post {post_id} not found",
        )
    
    if post.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access analytics for this post",
        )
    
    analytics = await service.get_post_analytics(
        post_id=post_id,
        start_date=start_date,
        end_date=end_date,
    )
    return analytics


@router.get(
    "",
    response_model=List[PostAnalyticsResponse],
    summary="List analytics",
    description="Get analytics for all posts with filters",
)
async def list_analytics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List analytics for the current user."""
    service = PostAnalyticsService(db)
    
    analytics = await service.get_user_analytics(
        user_id=current_user.user_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )
    return analytics


@router.get(
    "/summary",
    response_model=dict,
    summary="Get analytics summary",
    description="Get aggregated analytics summary",
)
async def get_analytics_summary(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get analytics summary."""
    service = PostAnalyticsService(db)
    
    summary = await service.get_analytics_summary(
        user_id=current_user.user_id,
        start_date=start_date,
        end_date=end_date,
    )
    return summary


@router.post(
    "/sync",
    response_model=List[PostAnalyticsResponse],
    summary="Sync analytics",
    description="Sync analytics from Buffer for recent posts",
)
async def sync_analytics(
    days: int = Query(7, ge=1, le=30, description="Number of days to look back"),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Sync analytics from Buffer."""
    service = PostAnalyticsService(db)
    buffer_config_service = BufferConfigService(db)
    
    # Get Buffer service
    buffer_service = await buffer_config_service.get_buffer_service(current_user.user_id)
    if not buffer_service:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Buffer is not configured for this user",
        )
    
    try:
        analytics = await service.bulk_sync_analytics(
            user_id=current_user.user_id,
            buffer_service=buffer_service,
            days=days,
        )
        return analytics
    except Exception as e:
        logger.error(f"Failed to sync analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync analytics: {str(e)}",
        )
