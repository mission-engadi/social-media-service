"""Buffer Configuration service layer.

Handles business logic for Buffer API configuration.
"""

import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.buffer_config import BufferConfig
from app.schemas.buffer_config import BufferConfigCreate, BufferConfigUpdate
from app.services.buffer_service import BufferService

logger = logging.getLogger(__name__)


class BufferConfigService:
    """Service for managing Buffer configuration."""
    
    def __init__(self, db: AsyncSession):
        """Initialize service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    async def create_config(
        self,
        user_id: int,
        config_data: BufferConfigCreate,
    ) -> BufferConfig:
        """Create Buffer configuration.
        
        Args:
            user_id: User ID
            config_data: Configuration data
        
        Returns:
            Created configuration
        """
        # Check if config already exists for user
        existing = await self.get_user_config(user_id)
        if existing:
            logger.warning(f"Buffer config already exists for user {user_id}")
            # Update instead of create
            return await self.update_config(
                existing.id,
                BufferConfigUpdate(**config_data.model_dump()),
            )
        
        config = BufferConfig(
            user_id=user_id,
            access_token=config_data.access_token,
            refresh_token=config_data.refresh_token,
            token_expires_at=config_data.token_expires_at,
            is_active=config_data.is_active if config_data.is_active is not None else True,
            settings=config_data.settings or {},
        )
        
        self.db.add(config)
        await self.db.commit()
        await self.db.refresh(config)
        
        logger.info(f"Created Buffer config for user {user_id}")
        return config
    
    async def get_config(self, config_id: int) -> Optional[BufferConfig]:
        """Get Buffer configuration by ID.
        
        Args:
            config_id: Config ID
        
        Returns:
            Configuration or None
        """
        result = await self.db.execute(
            select(BufferConfig).where(BufferConfig.id == config_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_config(self, user_id: int) -> Optional[BufferConfig]:
        """Get Buffer configuration for a user.
        
        Args:
            user_id: User ID
        
        Returns:
            Configuration or None
        """
        result = await self.db.execute(
            select(BufferConfig)
            .where(BufferConfig.user_id == user_id)
            .order_by(BufferConfig.created_at.desc())
        )
        return result.scalar_one_or_none()
    
    async def update_config(
        self,
        config_id: int,
        config_data: BufferConfigUpdate,
    ) -> Optional[BufferConfig]:
        """Update Buffer configuration.
        
        Args:
            config_id: Config ID
            config_data: Updated configuration data
        
        Returns:
            Updated configuration or None
        """
        config = await self.get_config(config_id)
        if not config:
            return None
        
        # Update fields
        update_data = config_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(config, field, value)
        
        await self.db.commit()
        await self.db.refresh(config)
        
        logger.info(f"Updated Buffer config {config_id}")
        return config
    
    async def delete_config(self, config_id: int) -> bool:
        """Delete Buffer configuration.
        
        Args:
            config_id: Config ID
        
        Returns:
            True if deleted, False if not found
        """
        config = await self.get_config(config_id)
        if not config:
            return False
        
        await self.db.delete(config)
        await self.db.commit()
        
        logger.info(f"Deleted Buffer config {config_id}")
        return True
    
    async def test_connection(
        self,
        config_id: int,
    ) -> bool:
        """Test Buffer connection using configuration.
        
        Args:
            config_id: Config ID
        
        Returns:
            True if connection successful
        """
        config = await self.get_config(config_id)
        if not config or not config.access_token:
            return False
        
        buffer_service = BufferService(access_token=config.access_token)
        return await buffer_service.test_connection()
    
    async def get_buffer_service(
        self,
        user_id: int,
    ) -> Optional[BufferService]:
        """Get Buffer service instance for a user.
        
        Args:
            user_id: User ID
        
        Returns:
            Buffer service instance or None
        """
        config = await self.get_user_config(user_id)
        if not config or not config.is_active or not config.access_token:
            return None
        
        return BufferService(access_token=config.access_token)
