"""Pydantic schemas for SocialAccount model.

Schemas define the structure of API requests and responses.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.social_account import AccountStatus, SocialPlatform


class SocialAccountBase(BaseModel):
    """Base schema with common fields."""
    
    platform: SocialPlatform = Field(..., description="Social media platform")
    account_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Account display name",
    )
    account_handle: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Account handle/username (e.g., @username)",
    )
    account_id: Optional[str] = Field(
        None,
        max_length=255,
        description="Platform-specific account ID",
    )
    status: AccountStatus = Field(
        AccountStatus.ACTIVE,
        description="Account status",
    )
    buffer_profile_id: Optional[str] = Field(
        None,
        max_length=255,
        description="Buffer profile ID",
    )
    is_primary: bool = Field(
        False,
        description="Whether this is the primary account for the platform",
    )
    platform_metadata: Optional[dict] = Field(
        None,
        description="Additional platform-specific metadata",
    )


class SocialAccountCreate(SocialAccountBase):
    """Schema for creating a social account.
    
    Used for POST requests.
    """
    access_token: Optional[str] = Field(
        None,
        description="OAuth access token (will be encrypted)",
    )
    refresh_token: Optional[str] = Field(
        None,
        description="OAuth refresh token (will be encrypted)",
    )
    token_expires_at: Optional[datetime] = Field(
        None,
        description="Token expiration timestamp",
    )


class SocialAccountUpdate(BaseModel):
    """Schema for updating a social account.
    
    Used for PUT/PATCH requests.
    All fields are optional for partial updates.
    """
    
    account_name: Optional[str] = Field(None, min_length=1, max_length=255)
    account_handle: Optional[str] = Field(None, min_length=1, max_length=255)
    account_id: Optional[str] = Field(None, max_length=255)
    status: Optional[AccountStatus] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    buffer_profile_id: Optional[str] = Field(None, max_length=255)
    is_primary: Optional[bool] = None
    platform_metadata: Optional[dict] = None


class SocialAccountResponse(SocialAccountBase):
    """Schema for social account responses.
    
    Used for GET requests.
    Includes database fields like id and timestamps.
    Excludes sensitive token fields.
    """
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    token_expires_at: Optional[datetime] = None


class SocialAccountWithTokens(SocialAccountResponse):
    """Schema with sensitive token fields.
    
    Only for internal use or privileged operations.
    """
    
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
