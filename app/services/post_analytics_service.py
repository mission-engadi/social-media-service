"""Post Analytics service layer.

Handles business logic for social media post analytics.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post_analytics import PostAnalytics
from app.models.scheduled_post import ScheduledPost
from app.schemas.post_analytics import PostAnalyticsCreate, PostAnalyticsUpdate
from app.services.providers.provider_factory import get_provider
from app.services.providers.base_provider import ProviderError

logger = logging.getLogger(__name__)


class PostAnalyticsService:
    """Service for managing post analytics."""
    
    def __init__(self, db: AsyncSession):
        """Initialize service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    async def create_analytics(
        self,
        analytics_data: PostAnalyticsCreate,
    ) -> PostAnalytics:
        """Create new analytics record.
        
        Args:
            analytics_data: Analytics data
        
        Returns:
            Created analytics record
        """
        analytics = PostAnalytics(
            post_id=analytics_data.post_id,
            platform=analytics_data.platform,
            likes=analytics_data.likes,
            comments=analytics_data.comments,
            shares=analytics_data.shares,
            clicks=analytics_data.clicks,
            reach=analytics_data.reach,
            impressions=analytics_data.impressions,
            engagement_rate=analytics_data.engagement_rate,
            recorded_at=analytics_data.recorded_at or datetime.utcnow(),
            metadata=analytics_data.metadata or {},
        )
        
        self.db.add(analytics)
        await self.db.commit()
        await self.db.refresh(analytics)
        
        logger.info(f"Created analytics record {analytics.id} for post {analytics_data.post_id}")
        return analytics
    
    async def get_analytics(self, analytics_id: int) -> Optional[PostAnalytics]:
        """Get analytics record by ID.
        
        Args:
            analytics_id: Analytics record ID
        
        Returns:
            Analytics record or None
        """
        result = await self.db.execute(
            select(PostAnalytics).where(PostAnalytics.id == analytics_id)
        )
        return result.scalar_one_or_none()
    
    async def get_post_analytics(
        self,
        post_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[PostAnalytics]:
        """Get all analytics records for a post.
        
        Args:
            post_id: Post ID
            start_date: Filter by start date (optional)
            end_date: Filter by end date (optional)
        
        Returns:
            List of analytics records
        """
        query = select(PostAnalytics).where(PostAnalytics.post_id == post_id)
        
        if start_date:
            query = query.where(PostAnalytics.recorded_at >= start_date)
        
        if end_date:
            query = query.where(PostAnalytics.recorded_at <= end_date)
        
        query = query.order_by(PostAnalytics.recorded_at.desc())
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_user_analytics(
        self,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[PostAnalytics]:
        """Get analytics for all posts by a user.
        
        Args:
            user_id: User ID
            start_date: Filter by start date (optional)
            end_date: Filter by end date (optional)
            limit: Maximum number of results
            offset: Number of results to skip
        
        Returns:
            List of analytics records
        """
        query = (
            select(PostAnalytics)
            .join(ScheduledPost)
            .where(ScheduledPost.user_id == user_id)
        )
        
        if start_date:
            query = query.where(PostAnalytics.recorded_at >= start_date)
        
        if end_date:
            query = query.where(PostAnalytics.recorded_at <= end_date)
        
        query = query.order_by(PostAnalytics.recorded_at.desc())
        query = query.limit(limit).offset(offset)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def update_analytics(
        self,
        analytics_id: int,
        analytics_data: PostAnalyticsUpdate,
    ) -> Optional[PostAnalytics]:
        """Update analytics record.
        
        Args:
            analytics_id: Analytics record ID
            analytics_data: Updated analytics data
        
        Returns:
            Updated analytics or None
        """
        analytics = await self.get_analytics(analytics_id)
        if not analytics:
            return None
        
        # Update fields
        update_data = analytics_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(analytics, field, value)
        
        await self.db.commit()
        await self.db.refresh(analytics)
        
        logger.info(f"Updated analytics record {analytics_id}")
        return analytics
    
    async def get_analytics_summary(
        self,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get aggregated analytics summary for a user.
        
        Args:
            user_id: User ID
            start_date: Filter by start date (optional)
            end_date: Filter by end date (optional)
        
        Returns:
            Analytics summary dictionary
        """
        query = (
            select(
                func.count(PostAnalytics.id).label('total_records'),
                func.sum(PostAnalytics.likes).label('total_likes'),
                func.sum(PostAnalytics.comments).label('total_comments'),
                func.sum(PostAnalytics.shares).label('total_shares'),
                func.sum(PostAnalytics.clicks).label('total_clicks'),
                func.sum(PostAnalytics.reach).label('total_reach'),
                func.sum(PostAnalytics.impressions).label('total_impressions'),
                func.avg(PostAnalytics.engagement_rate).label('avg_engagement_rate'),
            )
            .join(ScheduledPost)
            .where(ScheduledPost.user_id == user_id)
        )
        
        if start_date:
            query = query.where(PostAnalytics.recorded_at >= start_date)
        
        if end_date:
            query = query.where(PostAnalytics.recorded_at <= end_date)
        
        result = await self.db.execute(query)
        row = result.first()
        
        if not row:
            return {
                'total_records': 0,
                'total_likes': 0,
                'total_comments': 0,
                'total_shares': 0,
                'total_clicks': 0,
                'total_reach': 0,
                'total_impressions': 0,
                'avg_engagement_rate': 0.0,
            }
        
        return {
            'total_records': row.total_records or 0,
            'total_likes': row.total_likes or 0,
            'total_comments': row.total_comments or 0,
            'total_shares': row.total_shares or 0,
            'total_clicks': row.total_clicks or 0,
            'total_reach': row.total_reach or 0,
            'total_impressions': row.total_impressions or 0,
            'avg_engagement_rate': float(row.avg_engagement_rate or 0.0),
        }
    
    async def sync_analytics_from_buffer(
        self,
        post_id: int,
        
    ) -> Optional[PostAnalytics]:
        """Sync analytics from Buffer for a post.
        
        Args:
            post_id: Post ID
            buffer_service: Buffer service instance
        
        Returns:
            Created analytics record or None
        """
        # Get post with Buffer ID
        result = await self.db.execute(
            select(ScheduledPost).where(ScheduledPost.id == post_id)
        )
        post = result.scalar_one_or_none()
        
        if not post or not post.buffer_post_id:
            logger.warning(f"Post {post_id} not found or missing Buffer ID")
            return None
        
        try:
            # Get analytics from Buffer
            buffer_analytics = await provider.get_post_analytics(post.buffer_post_id)
            
            # Create analytics record
            analytics_data = PostAnalyticsCreate(
                post_id=post_id,
                platform=post.social_accounts[0].platform if post.social_accounts else 'twitter',
                likes=buffer_analytics.get('likes', 0),
                comments=buffer_analytics.get('comments', 0),
                shares=buffer_analytics.get('shares', 0),
                clicks=buffer_analytics.get('clicks', 0),
                reach=buffer_analytics.get('reach', 0),
                impressions=buffer_analytics.get('impressions', 0),
                engagement_rate=buffer_analytics.get('engagement_rate', 0.0),
                recorded_at=datetime.utcnow(),
                metadata={'source': 'buffer', 'raw_data': buffer_analytics},
            )
            
            analytics = await self.create_analytics(analytics_data)
            logger.info(f"Synced analytics from Buffer for post {post_id}")
            return analytics
        
        except ProviderError as e:
            logger.error(f"Failed to sync analytics for post {post_id}: {e.message}")
            return None
    
    async def bulk_sync_analytics(
        self,
        user_id: int,
        
        days: int = 7,
    ) -> List[PostAnalytics]:
        """Bulk sync analytics for recent posts.
        
        Args:
            user_id: User ID
            buffer_service: Buffer service instance
            days: Number of days to look back
        
        Returns:
            List of created analytics records
        """
        # Get recent published posts
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        query = (
            select(ScheduledPost)
            .where(
                and_(
                    ScheduledPost.user_id == user_id,
                    ScheduledPost.buffer_post_id.isnot(None),
                    ScheduledPost.published_at >= cutoff_date,
                )
            )
        )
        
        result = await self.db.execute(query)
        posts = list(result.scalars().all())
        
        analytics_records = []
        for post in posts:
            analytics = await self.sync_analytics_from_buffer(post.id, buffer_service)
            if analytics:
                analytics_records.append(analytics)
        
        logger.info(f"Bulk synced analytics for {len(analytics_records)} posts")
        return analytics_records
