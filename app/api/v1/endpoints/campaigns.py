"""Campaigns API endpoints.

Provides REST API for managing social media campaigns.
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.auth import CurrentUser, get_current_user
from app.models.campaign import CampaignStatus, CampaignType
from app.schemas.campaign import (
    CampaignCreate,
    CampaignUpdate,
    CampaignResponse,
)
from app.schemas.scheduled_post import ScheduledPostResponse
from app.services.campaign_service import CampaignService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "",
    response_model=CampaignResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create campaign",
    description="Create a new social media campaign",
)
async def create_campaign(
    campaign_data: CampaignCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new campaign."""
    service = CampaignService(db)
    
    try:
        campaign = await service.create_campaign(
            user_id=current_user.user_id,
            campaign_data=campaign_data,
        )
        return campaign
    except Exception as e:
        logger.error(f"Failed to create campaign: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create campaign: {str(e)}",
        )


@router.get(
    "/{campaign_id}",
    response_model=CampaignResponse,
    summary="Get campaign",
    description="Get a campaign by ID",
)
async def get_campaign(
    campaign_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a campaign by ID."""
    service = CampaignService(db)
    
    campaign = await service.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign {campaign_id} not found",
        )
    
    # Verify ownership
    if campaign.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this campaign",
        )
    
    return campaign


@router.get(
    "",
    response_model=List[CampaignResponse],
    summary="List campaigns",
    description="Get campaigns with optional filters",
)
async def list_campaigns(
    status_filter: Optional[CampaignStatus] = Query(None, alias="status"),
    campaign_type: Optional[CampaignType] = None,
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List campaigns for the current user."""
    service = CampaignService(db)
    
    campaigns = await service.get_user_campaigns(
        user_id=current_user.user_id,
        status=status_filter,
        campaign_type=campaign_type,
        limit=limit,
        offset=offset,
    )
    return campaigns


@router.put(
    "/{campaign_id}",
    response_model=CampaignResponse,
    summary="Update campaign",
    description="Update a campaign",
)
async def update_campaign(
    campaign_id: int,
    campaign_data: CampaignUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a campaign."""
    service = CampaignService(db)
    
    # Check ownership
    campaign = await service.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign {campaign_id} not found",
        )
    
    if campaign.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this campaign",
        )
    
    try:
        updated_campaign = await service.update_campaign(campaign_id, campaign_data)
        return updated_campaign
    except Exception as e:
        logger.error(f"Failed to update campaign: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update campaign: {str(e)}",
        )


@router.delete(
    "/{campaign_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete campaign",
    description="Delete a campaign",
)
async def delete_campaign(
    campaign_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a campaign."""
    service = CampaignService(db)
    
    # Check ownership
    campaign = await service.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign {campaign_id} not found",
        )
    
    if campaign.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this campaign",
        )
    
    deleted = await service.delete_campaign(campaign_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete campaign",
        )


@router.get(
    "/{campaign_id}/posts",
    response_model=List[ScheduledPostResponse],
    summary="Get campaign posts",
    description="Get all posts in a campaign",
)
async def get_campaign_posts(
    campaign_id: int,
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get posts in a campaign."""
    service = CampaignService(db)
    
    # Verify campaign ownership
    campaign = await service.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign {campaign_id} not found",
        )
    
    if campaign.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this campaign",
        )
    
    posts = await service.get_campaign_posts(
        campaign_id=campaign_id,
        limit=limit,
        offset=offset,
    )
    return posts


@router.get(
    "/{campaign_id}/analytics",
    response_model=dict,
    summary="Get campaign analytics",
    description="Get aggregated analytics for a campaign",
)
async def get_campaign_analytics(
    campaign_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get campaign analytics."""
    service = CampaignService(db)
    
    # Verify campaign ownership
    campaign = await service.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign {campaign_id} not found",
        )
    
    if campaign.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this campaign",
        )
    
    analytics = await service.get_campaign_analytics(campaign_id)
    return analytics
