"""Campaign service layer.

Handles business logic for social media campaigns.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.campaign import Campaign, CampaignStatus, CampaignType
from app.models.scheduled_post import ScheduledPost
from app.models.post_analytics import PostAnalytics
from app.schemas.campaign import CampaignCreate, CampaignUpdate

logger = logging.getLogger(__name__)


class CampaignService:
    """Service for managing campaigns."""
    
    def __init__(self, db: AsyncSession):
        """Initialize service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    async def create_campaign(
        self,
        user_id: int,
        campaign_data: CampaignCreate,
    ) -> Campaign:
        """Create a new campaign.
        
        Args:
            user_id: ID of the user creating the campaign
            campaign_data: Campaign data
        
        Returns:
            Created campaign
        """
        campaign = Campaign(
            user_id=user_id,
            name=campaign_data.name,
            description=campaign_data.description,
            campaign_type=campaign_data.campaign_type,
            start_date=campaign_data.start_date,
            end_date=campaign_data.end_date,
            status=campaign_data.status or CampaignStatus.DRAFT,
            goals=campaign_data.goals or {},
            metadata=campaign_data.metadata or {},
        )
        
        self.db.add(campaign)
        await self.db.commit()
        await self.db.refresh(campaign)
        
        logger.info(f"Created campaign {campaign.id} for user {user_id}")
        return campaign
    
    async def get_campaign(self, campaign_id: int) -> Optional[Campaign]:
        """Get a campaign by ID.
        
        Args:
            campaign_id: Campaign ID
        
        Returns:
            Campaign or None
        """
        result = await self.db.execute(
            select(Campaign).where(Campaign.id == campaign_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_campaigns(
        self,
        user_id: int,
        status: Optional[CampaignStatus] = None,
        campaign_type: Optional[CampaignType] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Campaign]:
        """Get campaigns for a user.
        
        Args:
            user_id: User ID
            status: Filter by status (optional)
            campaign_type: Filter by type (optional)
            limit: Maximum number of results
            offset: Number of results to skip
        
        Returns:
            List of campaigns
        """
        query = select(Campaign).where(Campaign.user_id == user_id)
        
        if status:
            query = query.where(Campaign.status == status)
        
        if campaign_type:
            query = query.where(Campaign.campaign_type == campaign_type)
        
        query = query.order_by(Campaign.created_at.desc())
        query = query.limit(limit).offset(offset)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def update_campaign(
        self,
        campaign_id: int,
        campaign_data: CampaignUpdate,
    ) -> Optional[Campaign]:
        """Update a campaign.
        
        Args:
            campaign_id: Campaign ID
            campaign_data: Updated campaign data
        
        Returns:
            Updated campaign or None
        """
        campaign = await self.get_campaign(campaign_id)
        if not campaign:
            return None
        
        # Update fields
        update_data = campaign_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(campaign, field, value)
        
        await self.db.commit()
        await self.db.refresh(campaign)
        
        logger.info(f"Updated campaign {campaign_id}")
        return campaign
    
    async def delete_campaign(self, campaign_id: int) -> bool:
        """Delete a campaign.
        
        Args:
            campaign_id: Campaign ID
        
        Returns:
            True if deleted, False if not found
        """
        campaign = await self.get_campaign(campaign_id)
        if not campaign:
            return False
        
        await self.db.delete(campaign)
        await self.db.commit()
        
        logger.info(f"Deleted campaign {campaign_id}")
        return True
    
    async def get_campaign_posts(
        self,
        campaign_id: int,
        limit: int = 100,
        offset: int = 0,
    ) -> List[ScheduledPost]:
        """Get all posts in a campaign.
        
        Args:
            campaign_id: Campaign ID
            limit: Maximum number of results
            offset: Number of results to skip
        
        Returns:
            List of scheduled posts
        """
        query = (
            select(ScheduledPost)
            .options(selectinload(ScheduledPost.social_accounts))
            .where(ScheduledPost.campaign_id == campaign_id)
            .order_by(ScheduledPost.scheduled_time.desc())
            .limit(limit)
            .offset(offset)
        )
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_campaign_analytics(
        self,
        campaign_id: int,
    ) -> Dict[str, Any]:
        """Get aggregated analytics for a campaign.
        
        Args:
            campaign_id: Campaign ID
        
        Returns:
            Campaign analytics summary
        """
        # Get post count
        post_count_query = (
            select(func.count(ScheduledPost.id))
            .where(ScheduledPost.campaign_id == campaign_id)
        )
        post_count_result = await self.db.execute(post_count_query)
        post_count = post_count_result.scalar() or 0
        
        # Get analytics summary
        analytics_query = (
            select(
                func.count(PostAnalytics.id).label('total_analytics'),
                func.sum(PostAnalytics.likes).label('total_likes'),
                func.sum(PostAnalytics.comments).label('total_comments'),
                func.sum(PostAnalytics.shares).label('total_shares'),
                func.sum(PostAnalytics.clicks).label('total_clicks'),
                func.sum(PostAnalytics.reach).label('total_reach'),
                func.sum(PostAnalytics.impressions).label('total_impressions'),
                func.avg(PostAnalytics.engagement_rate).label('avg_engagement_rate'),
            )
            .join(ScheduledPost)
            .where(ScheduledPost.campaign_id == campaign_id)
        )
        
        analytics_result = await self.db.execute(analytics_query)
        analytics_row = analytics_result.first()
        
        return {
            'campaign_id': campaign_id,
            'total_posts': post_count,
            'total_analytics_records': analytics_row.total_analytics or 0 if analytics_row else 0,
            'total_likes': analytics_row.total_likes or 0 if analytics_row else 0,
            'total_comments': analytics_row.total_comments or 0 if analytics_row else 0,
            'total_shares': analytics_row.total_shares or 0 if analytics_row else 0,
            'total_clicks': analytics_row.total_clicks or 0 if analytics_row else 0,
            'total_reach': analytics_row.total_reach or 0 if analytics_row else 0,
            'total_impressions': analytics_row.total_impressions or 0 if analytics_row else 0,
            'avg_engagement_rate': float(analytics_row.avg_engagement_rate or 0.0) if analytics_row else 0.0,
        }
