"""Social Account service layer.

Handles business logic for social media accounts.
"""

import logging
from typing import List, Optional
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.social_account import SocialAccount, SocialPlatform, AccountStatus
from app.schemas.social_account import SocialAccountCreate, SocialAccountUpdate
from app.services.buffer_service import BufferService, BufferAPIError

logger = logging.getLogger(__name__)


class SocialAccountService:
    """Service for managing social media accounts."""
    
    def __init__(self, db: AsyncSession):
        """Initialize service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    async def create_account(
        self,
        user_id: int,
        account_data: SocialAccountCreate,
    ) -> SocialAccount:
        """Create a new social media account.
        
        Args:
            user_id: ID of the user creating the account
            account_data: Account data
        
        Returns:
            Created social account
        """
        account = SocialAccount(
            user_id=user_id,
            platform=account_data.platform,
            account_name=account_data.account_name,
            username=account_data.username,
            access_token=account_data.access_token,
            refresh_token=account_data.refresh_token,
            token_expires_at=account_data.token_expires_at,
            buffer_profile_id=account_data.buffer_profile_id,
            status=account_data.status or AccountStatus.ACTIVE,
            profile_data=account_data.profile_data or {},
        )
        
        self.db.add(account)
        await self.db.commit()
        await self.db.refresh(account)
        
        logger.info(f"Created social account {account.id} for user {user_id}")
        return account
    
    async def get_account(self, account_id: int) -> Optional[SocialAccount]:
        """Get a social account by ID.
        
        Args:
            account_id: Account ID
        
        Returns:
            Social account or None
        """
        result = await self.db.execute(
            select(SocialAccount).where(SocialAccount.id == account_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_accounts(
        self,
        user_id: int,
        platform: Optional[SocialPlatform] = None,
        status: Optional[AccountStatus] = None,
    ) -> List[SocialAccount]:
        """Get all social accounts for a user.
        
        Args:
            user_id: User ID
            platform: Filter by platform (optional)
            status: Filter by status (optional)
        
        Returns:
            List of social accounts
        """
        query = select(SocialAccount).where(SocialAccount.user_id == user_id)
        
        if platform:
            query = query.where(SocialAccount.platform == platform)
        
        if status:
            query = query.where(SocialAccount.status == status)
        
        query = query.order_by(SocialAccount.created_at.desc())
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def update_account(
        self,
        account_id: int,
        account_data: SocialAccountUpdate,
    ) -> Optional[SocialAccount]:
        """Update a social account.
        
        Args:
            account_id: Account ID
            account_data: Updated account data
        
        Returns:
            Updated account or None
        """
        account = await self.get_account(account_id)
        if not account:
            return None
        
        # Update fields
        update_data = account_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(account, field, value)
        
        await self.db.commit()
        await self.db.refresh(account)
        
        logger.info(f"Updated social account {account_id}")
        return account
    
    async def delete_account(self, account_id: int) -> bool:
        """Delete a social account.
        
        Args:
            account_id: Account ID
        
        Returns:
            True if deleted, False if not found
        """
        account = await self.get_account(account_id)
        if not account:
            return False
        
        await self.db.delete(account)
        await self.db.commit()
        
        logger.info(f"Deleted social account {account_id}")
        return True
    
    async def sync_with_buffer(
        self,
        account_id: int,
        buffer_service: BufferService,
    ) -> Optional[SocialAccount]:
        """Sync account with Buffer profile.
        
        Args:
            account_id: Account ID
            buffer_service: Buffer service instance
        
        Returns:
            Updated account or None
        """
        account = await self.get_account(account_id)
        if not account or not account.buffer_profile_id:
            return None
        
        try:
            # Get profile from Buffer
            profile = await buffer_service.get_profile(account.buffer_profile_id)
            
            # Update account with Buffer profile data
            account.profile_data = {
                **account.profile_data,
                'buffer_sync': {
                    'synced_at': datetime.utcnow().isoformat(),
                    'profile_data': profile,
                }
            }
            account.status = AccountStatus.ACTIVE if profile.get('default', False) else account.status
            
            await self.db.commit()
            await self.db.refresh(account)
            
            logger.info(f"Synced account {account_id} with Buffer")
            return account
        
        except BufferAPIError as e:
            logger.error(f"Failed to sync account {account_id} with Buffer: {e.message}")
            account.status = AccountStatus.ERROR
            await self.db.commit()
            await self.db.refresh(account)
            return account
    
    async def test_connection(
        self,
        account_id: int,
        buffer_service: BufferService,
    ) -> bool:
        """Test connection to social account via Buffer.
        
        Args:
            account_id: Account ID
            buffer_service: Buffer service instance
        
        Returns:
            True if connection successful
        """
        account = await self.get_account(account_id)
        if not account or not account.buffer_profile_id:
            return False
        
        try:
            profile = await buffer_service.get_profile(account.buffer_profile_id)
            return profile is not None
        except BufferAPIError:
            return False
