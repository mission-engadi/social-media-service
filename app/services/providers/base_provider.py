"""Abstract base class for social media providers.

This module defines the interface that all social media providers must implement.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime


class ProviderError(Exception):
    """Base exception for provider errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)


class SocialMediaProvider(ABC):
    """Abstract base class for social media management providers.
    
    All social media providers (Ayrshare, Buffer, etc.) must implement this interface
    to ensure consistent behavior across different platforms.
    """
    
    @abstractmethod
    async def authenticate(self) -> Dict[str, Any]:
        """Verify provider authentication and get account info.
        
        Returns:
            Account/user information from the provider
            
        Raises:
            ProviderError: If authentication fails
        """
        pass
    
    @abstractmethod
    async def get_profiles(self) -> List[Dict[str, Any]]:
        """Get all connected social media profiles.
        
        Returns:
            List of profile dictionaries with standardized format:
            {
                'id': 'profile_id',
                'platform': 'facebook'|'twitter'|'instagram'|'linkedin'|etc.,
                'username': 'username',
                'name': 'Display Name',
                'is_active': True|False,
                'metadata': {}, # Platform-specific data
            }
            
        Raises:
            ProviderError: If request fails
        """
        pass
    
    @abstractmethod
    async def create_post(
        self,
        profile_ids: List[str],
        text: str,
        media: Optional[Dict[str, Any]] = None,
        scheduled_at: Optional[datetime] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create and optionally schedule a post.
        
        Args:
            profile_ids: List of profile IDs to post to
            text: Post content/caption
            media: Media attachments (photos, videos, links)
                {
                    'photos': ['url1', 'url2'],
                    'videos': ['url1'],
                    'link': 'url',
                    'thumbnail': 'url',
                }
            scheduled_at: When to publish (None for immediate/queue)
            **kwargs: Provider-specific options
            
        Returns:
            Created post information with standardized format:
            {
                'id': 'post_id',
                'status': 'scheduled'|'published'|'draft',
                'scheduled_at': 'ISO timestamp',
                'profiles': ['profile_id1', 'profile_id2'],
                'metadata': {}, # Provider-specific data
            }
            
        Raises:
            ProviderError: If request fails
        """
        pass
    
    @abstractmethod
    async def update_post(self, post_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing post.
        
        Args:
            post_id: Provider's post/update ID
            data: Updated post data (text, media, scheduled_at, etc.)
            
        Returns:
            Updated post information
            
        Raises:
            ProviderError: If request fails
        """
        pass
    
    @abstractmethod
    async def delete_post(self, post_id: str) -> Dict[str, Any]:
        """Delete a post.
        
        Args:
            post_id: Provider's post/update ID
            
        Returns:
            Deletion confirmation
            
        Raises:
            ProviderError: If request fails
        """
        pass
    
    @abstractmethod
    async def get_post_analytics(self, post_id: str) -> Dict[str, Any]:
        """Get analytics for a specific post.
        
        Args:
            post_id: Provider's post/update ID
            
        Returns:
            Analytics data with standardized format:
            {
                'post_id': 'post_id',
                'likes': 0,
                'comments': 0,
                'shares': 0,
                'clicks': 0,
                'reach': 0,
                'impressions': 0,
                'engagement_rate': 0.0,
                'retrieved_at': 'ISO timestamp',
            }
            
        Raises:
            ProviderError: If request fails
        """
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """Test the provider API connection.
        
        Returns:
            True if connection is successful, False otherwise
        """
        pass
