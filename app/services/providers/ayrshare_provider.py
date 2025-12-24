"""Ayrshare API integration provider.

This provider implements the SocialMediaProvider interface for Ayrshare,
the default social media management platform for white-label reselling.

Ayrshare Documentation: https://www.ayrshare.com/docs/introduction
API Endpoint: https://app.ayrshare.com/api
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

import httpx

from app.core.config import settings
from app.services.providers.base_provider import SocialMediaProvider, ProviderError

logger = logging.getLogger(__name__)


class AyrshareProvider(SocialMediaProvider):
    """Ayrshare API provider implementation.
    
    Supports: Facebook, Twitter/X, Instagram, LinkedIn, TikTok, YouTube,
    Pinterest, Reddit, Telegram, Threads, Bluesky, Google Business, Snapchat.
    
    Features:
    - Multi-platform posting
    - Post scheduling
    - Analytics and insights
    - Multi-user accounts
    - Webhooks for post status
    - White-label reselling support
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Ayrshare provider.
        
        Args:
            api_key: Ayrshare API key. If not provided, uses environment variable.
        """
        self.api_key = api_key or getattr(settings, 'AYRSHARE_API_KEY', None)
        self.base_url = getattr(settings, 'AYRSHARE_API_URL', 'https://app.ayrshare.com/api')
        self.timeout = 30.0
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make an HTTP request to Ayrshare API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters
        
        Returns:
            API response as dictionary
        
        Raises:
            ProviderError: If API request fails
        """
        if not self.api_key:
            raise ProviderError("Ayrshare API key not configured")
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    headers=headers,
                )
                
                # Check for errors
                if response.status_code >= 400:
                    error_msg = f"Ayrshare API error: {response.status_code}"
                    try:
                        error_data = response.json()
                        error_msg = error_data.get('message', error_data.get('error', error_msg))
                    except Exception:
                        error_msg = response.text or error_msg
                    
                    raise ProviderError(
                        message=error_msg,
                        status_code=response.status_code,
                        response=response.json() if response.text else None,
                    )
                
                return response.json() if response.text else {}
        
        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling Ayrshare API: {e}")
            raise ProviderError(f"Network error: {str(e)}")
        except ProviderError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error calling Ayrshare API: {e}")
            raise ProviderError(f"Unexpected error: {str(e)}")
    
    async def authenticate(self) -> Dict[str, Any]:
        """Verify Ayrshare authentication and get account info.
        
        Returns:
            Account information from Ayrshare
        
        Raises:
            ProviderError: If authentication fails
        """
        try:
            # Use the user endpoint to verify authentication
            user_info = await self._make_request('GET', '/user')
            logger.info(f"Successfully authenticated with Ayrshare")
            return user_info
        except ProviderError as e:
            logger.error(f"Ayrshare authentication failed: {e.message}")
            raise
    
    async def get_profiles(self) -> List[Dict[str, Any]]:
        """Get all social media profiles connected to Ayrshare.
        
        Returns:
            List of profile dictionaries with standardized format
        
        Raises:
            ProviderError: If request fails
        """
        try:
            response = await self._make_request('GET', '/profiles')
            
            # Ayrshare returns profiles in different formats
            # Normalize to our standard format
            raw_profiles = response.get('profiles', [])
            
            profiles = []
            for profile in raw_profiles:
                normalized = {
                    'id': profile.get('id', profile.get('profileKey')),
                    'platform': profile.get('platform', profile.get('type', '')).lower(),
                    'username': profile.get('username', profile.get('handle', '')),
                    'name': profile.get('name', profile.get('displayName', '')),
                    'is_active': profile.get('active', profile.get('isActive', True)),
                    'metadata': profile,  # Keep original data
                }
                profiles.append(normalized)
            
            logger.info(f"Retrieved {len(profiles)} Ayrshare profiles")
            return profiles
        except ProviderError as e:
            logger.error(f"Failed to get Ayrshare profiles: {e.message}")
            raise
    
    async def create_post(
        self,
        profile_ids: List[str],
        text: str,
        media: Optional[Dict[str, Any]] = None,
        scheduled_at: Optional[datetime] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create and optionally schedule a post via Ayrshare.
        
        Args:
            profile_ids: List of profile IDs (platform names or profile keys)
            text: Post content/caption
            media: Media attachments
            scheduled_at: When to publish (None for immediate)
            **kwargs: Additional Ayrshare options (shortenLinks, etc.)
        
        Returns:
            Created post information
        
        Raises:
            ProviderError: If request fails
        """
        data: Dict[str, Any] = {
            'post': text,
            'platforms': profile_ids,  # Ayrshare uses 'platforms'
        }
        
        # Add media if provided
        if media:
            if 'photos' in media and media['photos']:
                data['mediaUrls'] = media['photos']
            if 'videos' in media and media['videos']:
                data['videoUrls'] = media['videos']
            if 'link' in media:
                data['url'] = media['link']
        
        # Add scheduled time if provided
        if scheduled_at:
            # Ayrshare expects ISO 8601 format or Unix timestamp
            data['scheduleDate'] = scheduled_at.isoformat()
        
        # Add optional parameters
        data['shortenLinks'] = kwargs.get('shorten_links', True)
        
        # Add any other Ayrshare-specific parameters
        for key in ['title', 'description', 'hashtags', 'isVideo', 'autoHashtag']:
            if key in kwargs:
                data[key] = kwargs[key]
        
        try:
            response = await self._make_request('POST', '/post', data=data)
            
            # Normalize response to standard format
            normalized = {
                'id': response.get('id', response.get('postId')),
                'status': response.get('status', 'scheduled' if scheduled_at else 'published'),
                'scheduled_at': scheduled_at.isoformat() if scheduled_at else None,
                'profiles': profile_ids,
                'metadata': response,  # Keep original response
            }
            
            logger.info(f"Created Ayrshare post for {len(profile_ids)} profiles")
            return normalized
        except ProviderError as e:
            logger.error(f"Failed to create Ayrshare post: {e.message}")
            raise
    
    async def update_post(self, post_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing Ayrshare post.
        
        Args:
            post_id: Ayrshare post ID
            data: Updated post data
        
        Returns:
            Updated post information
        
        Raises:
            ProviderError: If request fails
        """
        # Convert our standard format to Ayrshare format
        ayrshare_data: Dict[str, Any] = {'id': post_id}
        
        if 'text' in data:
            ayrshare_data['post'] = data['text']
        if 'scheduled_at' in data:
            scheduled_at = data['scheduled_at']
            if isinstance(scheduled_at, datetime):
                ayrshare_data['scheduleDate'] = scheduled_at.isoformat()
            else:
                ayrshare_data['scheduleDate'] = scheduled_at
        
        try:
            response = await self._make_request('PUT', '/post', data=ayrshare_data)
            logger.info(f"Updated Ayrshare post: {post_id}")
            return response
        except ProviderError as e:
            logger.error(f"Failed to update Ayrshare post {post_id}: {e.message}")
            raise
    
    async def delete_post(self, post_id: str) -> Dict[str, Any]:
        """Delete an Ayrshare post.
        
        Args:
            post_id: Ayrshare post ID
        
        Returns:
            Deletion confirmation
        
        Raises:
            ProviderError: If request fails
        """
        try:
            response = await self._make_request('DELETE', f'/post/{post_id}')
            logger.info(f"Deleted Ayrshare post: {post_id}")
            return response
        except ProviderError as e:
            logger.error(f"Failed to delete Ayrshare post {post_id}: {e.message}")
            raise
    
    async def get_post_analytics(self, post_id: str) -> Dict[str, Any]:
        """Get analytics for a specific Ayrshare post.
        
        Args:
            post_id: Ayrshare post ID
        
        Returns:
            Analytics data with standardized format
        
        Raises:
            ProviderError: If request fails
        """
        try:
            # Ayrshare uses /analytics/post endpoint
            response = await self._make_request('GET', '/analytics/post', params={'id': post_id})
            
            # Normalize to standard format
            raw_analytics = response.get('analytics', {})
            
            analytics = {
                'post_id': post_id,
                'likes': raw_analytics.get('likes', raw_analytics.get('likeCount', 0)),
                'comments': raw_analytics.get('comments', raw_analytics.get('commentCount', 0)),
                'shares': raw_analytics.get('shares', raw_analytics.get('shareCount', 0)),
                'clicks': raw_analytics.get('clicks', raw_analytics.get('clickCount', 0)),
                'reach': raw_analytics.get('reach', 0),
                'impressions': raw_analytics.get('impressions', 0),
                'engagement_rate': raw_analytics.get('engagementRate', 0.0),
                'retrieved_at': datetime.utcnow().isoformat(),
            }
            
            logger.info(f"Retrieved analytics for Ayrshare post: {post_id}")
            return analytics
        except ProviderError as e:
            logger.error(f"Failed to get analytics for Ayrshare post {post_id}: {e.message}")
            raise
    
    async def test_connection(self) -> bool:
        """Test the Ayrshare API connection.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            await self.authenticate()
            return True
        except ProviderError:
            return False
    
    # Additional Ayrshare-specific methods
    
    async def get_post_status(self, post_id: str) -> Dict[str, Any]:
        """Get the current status of a post.
        
        Args:
            post_id: Ayrshare post ID
        
        Returns:
            Post status information
        
        Raises:
            ProviderError: If request fails
        """
        try:
            response = await self._make_request('GET', f'/post/{post_id}')
            logger.info(f"Retrieved status for Ayrshare post: {post_id}")
            return response
        except ProviderError as e:
            logger.error(f"Failed to get status for Ayrshare post {post_id}: {e.message}")
            raise
    
    async def get_history(
        self,
        platform: Optional[str] = None,
        last_days: int = 30,
    ) -> List[Dict[str, Any]]:
        """Get post history from Ayrshare.
        
        Args:
            platform: Filter by platform (optional)
            last_days: Number of days to retrieve (default: 30)
        
        Returns:
            List of historical posts
        
        Raises:
            ProviderError: If request fails
        """
        params = {'lastDays': last_days}
        if platform:
            params['platform'] = platform
        
        try:
            response = await self._make_request('GET', '/history', params=params)
            logger.info(f"Retrieved Ayrshare history for last {last_days} days")
            return response.get('posts', [])
        except ProviderError as e:
            logger.error(f"Failed to get Ayrshare history: {e.message}")
            raise
