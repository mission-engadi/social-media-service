"""Pydantic schemas for BufferConfig model.

Schemas define the structure of API requests and responses.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BufferConfigBase(BaseModel):
    """Base schema with common fields."""
    
    organization_id: Optional[str] = Field(
        None,
        max_length=255,
        description="Buffer organization ID",
    )
    is_active: bool = Field(
        True,
        description="Whether this configuration is active",
    )


class BufferConfigCreate(BufferConfigBase):
    """Schema for creating a Buffer configuration.
    
    Used for POST requests.
    """
    access_token: str = Field(
        ...,
        min_length=1,
        description="Buffer API access token (will be encrypted)",
    )
    refresh_token: Optional[str] = Field(
        None,
        description="Buffer API refresh token (will be encrypted)",
    )
    token_expires_at: Optional[datetime] = Field(
        None,
        description="Token expiration timestamp",
    )


class BufferConfigUpdate(BaseModel):
    """Schema for updating a Buffer configuration.
    
    Used for PUT/PATCH requests.
    All fields are optional for partial updates.
    """
    
    access_token: Optional[str] = Field(None, min_length=1)
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    organization_id: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None


class BufferConfigResponse(BufferConfigBase):
    """Schema for Buffer configuration responses.
    
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


class BufferConfigWithTokens(BufferConfigResponse):
    """Schema with sensitive token fields.
    
    Only for internal use or privileged operations.
    """
    
    access_token: str
    refresh_token: Optional[str] = None
