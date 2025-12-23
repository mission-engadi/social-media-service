"""Social Accounts API endpoints.

Provides REST API for managing social media accounts.
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.auth import CurrentUser, get_current_user
from app.models.social_account import SocialPlatform, AccountStatus
from app.schemas.social_account import (
    SocialAccountCreate,
    SocialAccountUpdate,
    SocialAccountResponse,
)
from app.services.social_account_service import SocialAccountService
from app.services.buffer_config_service import BufferConfigService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "",
    response_model=SocialAccountResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create social account",
    description="Create a new social media account connection",
)
async def create_social_account(
    account_data: SocialAccountCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new social media account."""
    service = SocialAccountService(db)
    
    try:
        account = await service.create_account(
            user_id=current_user.user_id,
            account_data=account_data,
        )
        return account
    except Exception as e:
        logger.error(f"Failed to create social account: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create social account: {str(e)}",
        )


@router.get(
    "/{account_id}",
    response_model=SocialAccountResponse,
    summary="Get social account",
    description="Get a social media account by ID",
)
async def get_social_account(
    account_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a social account by ID."""
    service = SocialAccountService(db)
    
    account = await service.get_account(account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Social account {account_id} not found",
        )
    
    # Verify ownership
    if account.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this account",
        )
    
    return account


@router.get(
    "",
    response_model=List[SocialAccountResponse],
    summary="List social accounts",
    description="Get all social media accounts for the current user",
)
async def list_social_accounts(
    platform: SocialPlatform = None,
    status_filter: AccountStatus = None,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all social accounts for the current user."""
    service = SocialAccountService(db)
    
    accounts = await service.get_user_accounts(
        user_id=current_user.user_id,
        platform=platform,
        status=status_filter,
    )
    return accounts


@router.put(
    "/{account_id}",
    response_model=SocialAccountResponse,
    summary="Update social account",
    description="Update a social media account",
)
async def update_social_account(
    account_id: int,
    account_data: SocialAccountUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a social account."""
    service = SocialAccountService(db)
    
    # Check ownership
    account = await service.get_account(account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Social account {account_id} not found",
        )
    
    if account.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this account",
        )
    
    try:
        updated_account = await service.update_account(account_id, account_data)
        return updated_account
    except Exception as e:
        logger.error(f"Failed to update social account: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update social account: {str(e)}",
        )


@router.delete(
    "/{account_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete social account",
    description="Delete a social media account",
)
async def delete_social_account(
    account_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a social account."""
    service = SocialAccountService(db)
    
    # Check ownership
    account = await service.get_account(account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Social account {account_id} not found",
        )
    
    if account.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this account",
        )
    
    deleted = await service.delete_account(account_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete social account",
        )


@router.post(
    "/{account_id}/sync-buffer",
    response_model=SocialAccountResponse,
    summary="Sync with Buffer",
    description="Sync social account with Buffer profile",
)
async def sync_account_with_buffer(
    account_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Sync account with Buffer."""
    service = SocialAccountService(db)
    buffer_config_service = BufferConfigService(db)
    
    # Check ownership
    account = await service.get_account(account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Social account {account_id} not found",
        )
    
    if account.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to sync this account",
        )
    
    # Get Buffer service
    buffer_service = await buffer_config_service.get_buffer_service(current_user.user_id)
    if not buffer_service:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Buffer is not configured for this user",
        )
    
    try:
        synced_account = await service.sync_with_buffer(account_id, buffer_service)
        if not synced_account:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to sync with Buffer",
            )
        return synced_account
    except Exception as e:
        logger.error(f"Failed to sync account with Buffer: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync with Buffer: {str(e)}",
        )


@router.post(
    "/{account_id}/test-connection",
    response_model=dict,
    summary="Test connection",
    description="Test connection to social account via Buffer",
)
async def test_account_connection(
    account_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Test connection to social account."""
    service = SocialAccountService(db)
    buffer_config_service = BufferConfigService(db)
    
    # Check ownership
    account = await service.get_account(account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Social account {account_id} not found",
        )
    
    if account.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to test this account",
        )
    
    # Get Buffer service
    buffer_service = await buffer_config_service.get_buffer_service(current_user.user_id)
    if not buffer_service:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Buffer is not configured for this user",
        )
    
    try:
        is_connected = await service.test_connection(account_id, buffer_service)
        return {
            "account_id": account_id,
            "connected": is_connected,
            "message": "Connection successful" if is_connected else "Connection failed",
        }
    except Exception as e:
        logger.error(f"Failed to test account connection: {e}")
        return {
            "account_id": account_id,
            "connected": False,
            "message": f"Connection test failed: {str(e)}",
        }
