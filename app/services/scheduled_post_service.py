"""Scheduled Post service layer.

Handles business logic for scheduled social media posts.
"""

import logging
from typing import List, Optional
from datetime import datetime, date

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.scheduled_post import ScheduledPost, PostStatus, PostType
from app.models.social_account import SocialAccount
from app.schemas.scheduled_post import ScheduledPostCreate, ScheduledPostUpdate
from app.services.providers.provider_factory import get_provider
from app.services.providers.base_provider import ProviderError

logger = logging.getLogger(__name__)


class ScheduledPostService:
    """Service for managing scheduled posts."""
    
    def __init__(self, db: AsyncSession):
        """Initialize service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    async def create_post(
        self,
        user_id: int,
        post_data: ScheduledPostCreate,
    ) -> ScheduledPost:
        """Create a new scheduled post.
        
        Args:
            user_id: ID of the user creating the post
            post_data: Post data
        
        Returns:
            Created scheduled post
        """
        post = ScheduledPost(
            user_id=user_id,
            campaign_id=post_data.campaign_id,
            post_type=post_data.post_type,
            content=post_data.content,
            media_urls=post_data.media_urls or [],
            scheduled_time=post_data.scheduled_time,
            status=post_data.status or PostStatus.DRAFT,
            buffer_post_id=post_data.buffer_post_id,
            platform_post_ids=post_data.platform_post_ids or {},
            metadata=post_data.metadata or {},
        )
        
        self.db.add(post)
        await self.db.commit()
        await self.db.refresh(post, ['social_accounts'])
        
        # Add social accounts if provided
        if post_data.social_account_ids:
            accounts = await self.db.execute(
                select(SocialAccount).where(
                    SocialAccount.id.in_(post_data.social_account_ids)
                )
            )
            post.social_accounts = list(accounts.scalars().all())
            await self.db.commit()
            await self.db.refresh(post, ['social_accounts'])
        
        logger.info(f"Created scheduled post {post.id} for user {user_id}")
        return post
    
    async def get_post(self, post_id: int) -> Optional[ScheduledPost]:
        """Get a scheduled post by ID.
        
        Args:
            post_id: Post ID
        
        Returns:
            Scheduled post or None
        """
        result = await self.db.execute(
            select(ScheduledPost)
            .options(selectinload(ScheduledPost.social_accounts))
            .where(ScheduledPost.id == post_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_posts(
        self,
        user_id: int,
        status: Optional[PostStatus] = None,
        post_type: Optional[PostType] = None,
        campaign_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[ScheduledPost]:
        """Get scheduled posts for a user with filters.
        
        Args:
            user_id: User ID
            status: Filter by status (optional)
            post_type: Filter by post type (optional)
            campaign_id: Filter by campaign (optional)
            start_date: Filter by start date (optional)
            end_date: Filter by end date (optional)
            limit: Maximum number of results
            offset: Number of results to skip
        
        Returns:
            List of scheduled posts
        """
        query = select(ScheduledPost).options(
            selectinload(ScheduledPost.social_accounts)
        ).where(ScheduledPost.user_id == user_id)
        
        if status:
            query = query.where(ScheduledPost.status == status)
        
        if post_type:
            query = query.where(ScheduledPost.post_type == post_type)
        
        if campaign_id:
            query = query.where(ScheduledPost.campaign_id == campaign_id)
        
        if start_date:
            query = query.where(ScheduledPost.scheduled_time >= start_date)
        
        if end_date:
            query = query.where(ScheduledPost.scheduled_time <= end_date)
        
        query = query.order_by(ScheduledPost.scheduled_time.desc())
        query = query.limit(limit).offset(offset)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def update_post(
        self,
        post_id: int,
        post_data: ScheduledPostUpdate,
    ) -> Optional[ScheduledPost]:
        """Update a scheduled post.
        
        Args:
            post_id: Post ID
            post_data: Updated post data
        
        Returns:
            Updated post or None
        """
        post = await self.get_post(post_id)
        if not post:
            return None
        
        # Update fields
        update_data = post_data.model_dump(exclude_unset=True)
        
        # Handle social_account_ids separately
        social_account_ids = update_data.pop('social_account_ids', None)
        
        for field, value in update_data.items():
            setattr(post, field, value)
        
        # Update social accounts if provided
        if social_account_ids is not None:
            accounts = await self.db.execute(
                select(SocialAccount).where(
                    SocialAccount.id.in_(social_account_ids)
                )
            )
            post.social_accounts = list(accounts.scalars().all())
        
        await self.db.commit()
        await self.db.refresh(post, ['social_accounts'])
        
        logger.info(f"Updated scheduled post {post_id}")
        return post
    
    async def delete_post(self, post_id: int) -> bool:
        """Delete a scheduled post.
        
        Args:
            post_id: Post ID
        
        Returns:
            True if deleted, False if not found
        """
        post = await self.get_post(post_id)
        if not post:
            return False
        
        await self.db.delete(post)
        await self.db.commit()
        
        logger.info(f"Deleted scheduled post {post_id}")
        return True
    
    async def schedule_with_provider(
        self,
        post_id: int,
    ) -> Optional[ScheduledPost]:
        """Schedule a post via social media provider.
        
        Args:
            post_id: Post ID
        
        Returns:
            Updated post or None
        """
        post = await self.get_post(post_id)
        if not post:
            return None
        
        try:
            # Get provider instance
            provider = get_provider()
            
            # Get profile IDs from associated accounts
            profile_ids = [
                acc.buffer_profile_id
                for acc in post.social_accounts
                if acc.buffer_profile_id
            ]
            
            if not profile_ids:
                logger.error(f"No profiles found for post {post_id}")
                return None
            
            # Prepare media data
            media = None
            if post.media_urls:
                media = {'photos': post.media_urls}  # Use photos array for compatibility
            
            # Create post via provider
            provider_response = await provider.create_post(
                profile_ids=profile_ids,
                text=post.content,
                media=media,
                scheduled_at=post.scheduled_time,
            )
            
            # Update post with Buffer IDs
            post.buffer_post_id = provider_response.get('updates', [{}])[0].get('id')
            post.status = PostStatus.SCHEDULED
            post.metadata = {
                **post.metadata,
                'provider_response': provider_response,
                'scheduled_at': datetime.utcnow().isoformat(),
            }
            
            await self.db.commit()
            await self.db.refresh(post)
            
            logger.info(f"Scheduled post {post_id} via Buffer")
            return post
        
        except ProviderError as e:
            logger.error(f"Failed to schedule post {post_id} via Buffer: {e.message}")
            post.status = PostStatus.FAILED
            post.metadata = {
                **post.metadata,
                'error': e.message,
                'error_time': datetime.utcnow().isoformat(),
            }
            await self.db.commit()
            return post
    
    async def publish_now(
        self,
        post_id: int,
        
    ) -> Optional[ScheduledPost]:
        """Publish a post immediately via Buffer.
        
        Args:
            post_id: Post ID
            buffer_service: Buffer service instance
        
        Returns:
            Updated post or None
        """
        post = await self.get_post(post_id)
        if not post:
            return None
        
        try:
            # Get Buffer profile IDs
            profile_ids = [
                acc.buffer_profile_id
                for acc in post.social_accounts
                if acc.buffer_profile_id
            ]
            
            if not profile_ids:
                logger.error(f"No Buffer profiles found for post {post_id}")
                return None
            
            # Prepare media
            media = None
            if post.media_urls:
                media = {'photo': post.media_urls[0]}
            
            # Publish immediately
            provider_response = await provider.create_post(
                profile_ids=profile_ids,
                text=post.content,
                media=media,
                now=True,
            )
            
            # Update post
            post.buffer_post_id = provider_response.get('updates', [{}])[0].get('id')
            post.status = PostStatus.PUBLISHED
            post.published_at = datetime.utcnow()
            post.metadata = {
                **post.metadata,
                'provider_response': provider_response,
                'published_at': datetime.utcnow().isoformat(),
            }
            
            await self.db.commit()
            await self.db.refresh(post)
            
            logger.info(f"Published post {post_id} immediately")
            return post
        
        except ProviderError as e:
            logger.error(f"Failed to publish post {post_id}: {e.message}")
            post.status = PostStatus.FAILED
            await self.db.commit()
            return post
    
    async def cancel_scheduled_post(
        self,
        post_id: int,
        
    ) -> Optional[ScheduledPost]:
        """Cancel a scheduled post in Buffer.
        
        Args:
            post_id: Post ID
            buffer_service: Buffer service instance
        
        Returns:
            Updated post or None
        """
        post = await self.get_post(post_id)
        if not post or not post.buffer_post_id:
            return None
        
        try:
            # Delete from Buffer
            await provider.delete_post(post.buffer_post_id)
            
            # Update post status
            post.status = PostStatus.CANCELLED
            post.metadata = {
                **post.metadata,
                'cancelled_at': datetime.utcnow().isoformat(),
            }
            
            await self.db.commit()
            await self.db.refresh(post)
            
            logger.info(f"Cancelled scheduled post {post_id}")
            return post
        
        except ProviderError as e:
            logger.error(f"Failed to cancel post {post_id}: {e.message}")
            return post
    
    async def get_calendar(
        self,
        user_id: int,
        start_date: date,
        end_date: date,
    ) -> List[ScheduledPost]:
        """Get content calendar for a date range.
        
        Args:
            user_id: User ID
            start_date: Calendar start date
            end_date: Calendar end date
        
        Returns:
            List of scheduled posts in date range
        """
        query = select(ScheduledPost).options(
            selectinload(ScheduledPost.social_accounts)
        ).where(
            and_(
                ScheduledPost.user_id == user_id,
                ScheduledPost.scheduled_time >= start_date,
                ScheduledPost.scheduled_time <= end_date,
            )
        ).order_by(ScheduledPost.scheduled_time.asc())
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def bulk_schedule(
        self,
        user_id: int,
        posts_data: List[ScheduledPostCreate],
        
    ) -> List[ScheduledPost]:
        """Create and optionally schedule multiple posts.
        
        Args:
            user_id: User ID
            posts_data: List of post data
            buffer_service: Buffer service for immediate scheduling (optional)
        
        Returns:
            List of created posts
        """
        created_posts = []
        
        for post_data in posts_data:
            post = await self.create_post(user_id, post_data)
            
            # Schedule immediately if Buffer service provided
            if buffer_service and post.status == PostStatus.DRAFT:
                post = await self.schedule_with_buffer(post.id, buffer_service)
            
            if post:
                created_posts.append(post)
        
        logger.info(f"Bulk created {len(created_posts)} posts for user {user_id}")
        return created_posts
