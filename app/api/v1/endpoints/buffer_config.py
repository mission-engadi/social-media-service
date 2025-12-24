"""Buffer Configuration API endpoints.

Provides REST API for managing Buffer API configuration.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.auth import CurrentUser, get_current_user, require_auth
from app.schemas.buffer_config import (
    BufferConfigCreate,
    BufferConfigUpdate,
    BufferConfigResponse,
)
from app.services.buffer_config_service import BufferConfigService
from app.services.providers.provider_factory import get_provider
from app.services.providers.base_provider import ProviderError

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/config",
    response_model=BufferConfigResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Configure Buffer",
    description="Configure Buffer API credentials",
)
async def create_buffer_config(
    config_data: BufferConfigCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Configure Buffer for the current user."""
    service = BufferConfigService(db)
    
    try:
        config = await service.create_config(
            user_id=current_user.user_id,
            config_data=config_data,
        )
        return config
    except Exception as e:
        logger.error(f"Failed to create Buffer config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create Buffer config: {str(e)}",
        )


@router.get(
    "/config",
    response_model=BufferConfigResponse,
    summary="Get Buffer config",
    description="Get Buffer configuration for the current user",
)
async def get_buffer_config(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get Buffer configuration."""
    service = BufferConfigService(db)
    
    config = await service.get_user_config(current_user.user_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Buffer is not configured for this user",
        )
    
    return config


@router.put(
    "/config",
    response_model=BufferConfigResponse,
    summary="Update Buffer config",
    description="Update Buffer configuration",
)
async def update_buffer_config(
    config_data: BufferConfigUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update Buffer configuration."""
    service = BufferConfigService(db)
    
    # Get existing config
    config = await service.get_user_config(current_user.user_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Buffer is not configured for this user",
        )
    
    try:
        updated_config = await service.update_config(config.id, config_data)
        return updated_config
    except Exception as e:
        logger.error(f"Failed to update Buffer config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update Buffer config: {str(e)}",
        )


@router.post(
    "/test",
    response_model=dict,
    summary="Test Buffer connection",
    description="Test connection to Buffer API",
)
async def test_buffer_connection(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Test Buffer connection."""
    service = BufferConfigService(db)
    
    # Get config
    config = await service.get_user_config(current_user.user_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Buffer is not configured for this user",
        )
    
    try:
        is_connected = await service.test_connection(config.id)
        return {
            "connected": is_connected,
            "message": "Connection successful" if is_connected else "Connection failed",
        }
    except Exception as e:
        logger.error(f"Failed to test Buffer connection: {e}")
        return {
            "connected": False,
            "message": f"Connection test failed: {str(e)}",
        }


@router.get(
    "/profiles",
    response_model=list,
    summary="Get Buffer profiles",
    description="Get all social media profiles connected to Buffer",
)
async def get_buffer_profiles(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get Buffer profiles."""
    service = BufferConfigService(db)
    
    # Get Buffer service
    buffer_service = await service.get_buffer_service(current_user.user_id)
    if not buffer_service:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Buffer is not configured for this user",
        )
    
    try:
        profiles = await buffer_service.get_profiles()
        return profiles
    except ProviderError as e:
        logger.error(f"Failed to get Buffer profiles: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get Buffer profiles: {e.message}",
        )
