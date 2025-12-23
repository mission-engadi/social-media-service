"""Scheduled Posts API endpoints.

Provides REST API for managing scheduled social media posts.
"""

import logging
from typing import List, Optional
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.auth import CurrentUser, get_current_user
from app.models.scheduled_post import PostStatus, PostType
from app.schemas.scheduled_post import (
    ScheduledPostCreate,
    ScheduledPostUpdate,
    ScheduledPostResponse,
)
from app.services.scheduled_post_service import ScheduledPostService
from app.services.buffer_config_service import BufferConfigService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "",
    response_model=ScheduledPostResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create scheduled post",
    description="Create a new scheduled social media post",
)
async def create_scheduled_post(
    post_data: ScheduledPostCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new scheduled post."""
    service = ScheduledPostService(db)
    
    try:
        post = await service.create_post(
            user_id=current_user.user_id,
            post_data=post_data,
        )
        return post
    except Exception as e:
        logger.error(f"Failed to create scheduled post: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create scheduled post: {str(e)}",
        )


@router.get(
    "/{post_id}",
    response_model=ScheduledPostResponse,
    summary="Get scheduled post",
    description="Get a scheduled post by ID",
)
async def get_scheduled_post(
    post_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a scheduled post by ID."""
    service = ScheduledPostService(db)
    
    post = await service.get_post(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scheduled post {post_id} not found",
        )
    
    # Verify ownership
    if post.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this post",
        )
    
    return post


@router.get(
    "",
    response_model=List[ScheduledPostResponse],
    summary="List scheduled posts",
    description="Get scheduled posts with optional filters",
)
async def list_scheduled_posts(
    status_filter: Optional[PostStatus] = Query(None, alias="status"),
    post_type: Optional[PostType] = None,
    campaign_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List scheduled posts for the current user."""
    service = ScheduledPostService(db)
    
    posts = await service.get_user_posts(
        user_id=current_user.user_id,
        status=status_filter,
        post_type=post_type,
        campaign_id=campaign_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )
    return posts


@router.put(
    "/{post_id}",
    response_model=ScheduledPostResponse,
    summary="Update scheduled post",
    description="Update a scheduled post",
)
async def update_scheduled_post(
    post_id: int,
    post_data: ScheduledPostUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a scheduled post."""
    service = ScheduledPostService(db)
    
    # Check ownership
    post = await service.get_post(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scheduled post {post_id} not found",
        )
    
    if post.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this post",
        )
    
    try:
        updated_post = await service.update_post(post_id, post_data)
        return updated_post
    except Exception as e:
        logger.error(f"Failed to update scheduled post: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update scheduled post: {str(e)}",
        )


@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete scheduled post",
    description="Delete a scheduled post",
)
async def delete_scheduled_post(
    post_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a scheduled post."""
    service = ScheduledPostService(db)
    
    # Check ownership
    post = await service.get_post(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scheduled post {post_id} not found",
        )
    
    if post.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this post",
        )
    
    deleted = await service.delete_post(post_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete scheduled post",
        )


@router.post(
    "/{post_id}/schedule",
    response_model=ScheduledPostResponse,
    summary="Schedule post",
    description="Schedule a post via Buffer",
)
async def schedule_post(
    post_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Schedule a post via Buffer."""
    service = ScheduledPostService(db)
    buffer_config_service = BufferConfigService(db)
    
    # Check ownership
    post = await service.get_post(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scheduled post {post_id} not found",
        )
    
    if post.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to schedule this post",
        )
    
    # Get Buffer service
    buffer_service = await buffer_config_service.get_buffer_service(current_user.user_id)
    if not buffer_service:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Buffer is not configured for this user",
        )
    
    try:
        scheduled_post = await service.schedule_with_buffer(post_id, buffer_service)
        if not scheduled_post:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to schedule post",
            )
        return scheduled_post
    except Exception as e:
        logger.error(f"Failed to schedule post: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to schedule post: {str(e)}",
        )


@router.post(
    "/{post_id}/publish-now",
    response_model=ScheduledPostResponse,
    summary="Publish now",
    description="Publish a post immediately",
)
async def publish_post_now(
    post_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Publish a post immediately."""
    service = ScheduledPostService(db)
    buffer_config_service = BufferConfigService(db)
    
    # Check ownership
    post = await service.get_post(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scheduled post {post_id} not found",
        )
    
    if post.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to publish this post",
        )
    
    # Get Buffer service
    buffer_service = await buffer_config_service.get_buffer_service(current_user.user_id)
    if not buffer_service:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Buffer is not configured for this user",
        )
    
    try:
        published_post = await service.publish_now(post_id, buffer_service)
        if not published_post:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to publish post",
            )
        return published_post
    except Exception as e:
        logger.error(f"Failed to publish post: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to publish post: {str(e)}",
        )


@router.post(
    "/{post_id}/cancel",
    response_model=ScheduledPostResponse,
    summary="Cancel scheduled post",
    description="Cancel a scheduled post",
)
async def cancel_scheduled_post(
    post_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cancel a scheduled post."""
    service = ScheduledPostService(db)
    buffer_config_service = BufferConfigService(db)
    
    # Check ownership
    post = await service.get_post(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scheduled post {post_id} not found",
        )
    
    if post.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to cancel this post",
        )
    
    # Get Buffer service
    buffer_service = await buffer_config_service.get_buffer_service(current_user.user_id)
    if not buffer_service:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Buffer is not configured for this user",
        )
    
    try:
        cancelled_post = await service.cancel_scheduled_post(post_id, buffer_service)
        if not cancelled_post:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to cancel post",
            )
        return cancelled_post
    except Exception as e:
        logger.error(f"Failed to cancel post: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel post: {str(e)}",
        )


@router.get(
    "/calendar",
    response_model=List[ScheduledPostResponse],
    summary="Get content calendar",
    description="Get content calendar for a date range",
)
async def get_content_calendar(
    start_date: date,
    end_date: date,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get content calendar."""
    service = ScheduledPostService(db)
    
    posts = await service.get_calendar(
        user_id=current_user.user_id,
        start_date=start_date,
        end_date=end_date,
    )
    return posts


@router.post(
    "/bulk-schedule",
    response_model=List[ScheduledPostResponse],
    summary="Bulk schedule posts",
    description="Create and schedule multiple posts at once",
)
async def bulk_schedule_posts(
    posts_data: List[ScheduledPostCreate],
    schedule_immediately: bool = Query(False, description="Schedule with Buffer immediately"),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Bulk schedule posts."""
    service = ScheduledPostService(db)
    buffer_config_service = BufferConfigService(db)
    
    # Get Buffer service if immediate scheduling requested
    buffer_service = None
    if schedule_immediately:
        buffer_service = await buffer_config_service.get_buffer_service(current_user.user_id)
        if not buffer_service:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Buffer is not configured for this user",
            )
    
    try:
        posts = await service.bulk_schedule(
            user_id=current_user.user_id,
            posts_data=posts_data,
            buffer_service=buffer_service,
        )
        return posts
    except Exception as e:
        logger.error(f"Failed to bulk schedule posts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk schedule posts: {str(e)}",
        )
