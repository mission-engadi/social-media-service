"""Buffer API integration service.

This service handles all interactions with the Buffer API for social media scheduling.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class BufferAPIError(Exception):
    """Exception raised for Buffer API errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)


class BufferService:
    """Service for interacting with Buffer API.
    
    This service provides methods to:
    - Authenticate with Buffer
    - Get connected social profiles
    - Create, update, and delete scheduled posts
    - Retrieve post analytics
    """
    
    def __init__(self, access_token: Optional[str] = None):
        """Initialize Buffer service.
        
        Args:
            access_token: Buffer API access token. If not provided, uses environment variable.
        """
        self.access_token = access_token or getattr(settings, 'BUFFER_ACCESS_TOKEN', None)
        self.base_url = getattr(settings, 'BUFFER_API_URL', 'https://api.bufferapp.com/1')
        self.timeout = 30.0
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make an HTTP request to Buffer API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters
        
        Returns:
            API response as dictionary
        
        Raises:
            BufferAPIError: If API request fails
        """
        if not self.access_token:
            raise BufferAPIError("Buffer access token not configured")
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        # Add access token to params
        if params is None:
            params = {}
        params['access_token'] = self.access_token
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                )
                
                # Check for errors
                if response.status_code >= 400:
                    error_msg = f"Buffer API error: {response.status_code}"
                    try:
                        error_data = response.json()
                        error_msg = error_data.get('message', error_msg)
                    except Exception:
                        error_msg = response.text or error_msg
                    
                    raise BufferAPIError(
                        message=error_msg,
                        status_code=response.status_code,
                        response=response.json() if response.text else None,
                    )
                
                return response.json() if response.text else {}
        
        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling Buffer API: {e}")
            raise BufferAPIError(f"Network error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error calling Buffer API: {e}")
            raise BufferAPIError(f"Unexpected error: {str(e)}")
    
    async def authenticate(self) -> Dict[str, Any]:
        """Verify Buffer authentication and get user info.
        
        Returns:
            User information from Buffer
        
        Raises:
            BufferAPIError: If authentication fails
        """
        try:
            user_info = await self._make_request('GET', '/user.json')
            logger.info(f"Successfully authenticated with Buffer for user: {user_info.get('id')}")
            return user_info
        except BufferAPIError as e:
            logger.error(f"Buffer authentication failed: {e.message}")
            raise
    
    async def get_profiles(self) -> List[Dict[str, Any]]:
        """Get all social media profiles connected to Buffer.
        
        Returns:
            List of profile dictionaries
        
        Raises:
            BufferAPIError: If request fails
        """
        try:
            response = await self._make_request('GET', '/profiles.json')
            profiles = response if isinstance(response, list) else []
            logger.info(f"Retrieved {len(profiles)} Buffer profiles")
            return profiles
        except BufferAPIError as e:
            logger.error(f"Failed to get Buffer profiles: {e.message}")
            raise
    
    async def get_profile(self, profile_id: str) -> Dict[str, Any]:
        """Get a specific Buffer profile.
        
        Args:
            profile_id: Buffer profile ID
        
        Returns:
            Profile information
        
        Raises:
            BufferAPIError: If request fails
        """
        try:
            profile = await self._make_request('GET', f'/profiles/{profile_id}.json')
            logger.info(f"Retrieved Buffer profile: {profile_id}")
            return profile
        except BufferAPIError as e:
            logger.error(f"Failed to get Buffer profile {profile_id}: {e.message}")
            raise
    
    async def create_post(
        self,
        profile_ids: List[str],
        text: str,
        media: Optional[Dict[str, Any]] = None,
        scheduled_at: Optional[datetime] = None,
        shorten: bool = True,
        now: bool = False,
    ) -> Dict[str, Any]:
        """Create a new post in Buffer.
        
        Args:
            profile_ids: List of Buffer profile IDs to post to
            text: Post content
            media: Media attachments (photos, videos, links)
            scheduled_at: When to publish the post (None for queue)
            shorten: Whether to shorten links
            now: Whether to publish immediately
        
        Returns:
            Created post information
        
        Raises:
            BufferAPIError: If request fails
        """
        data: Dict[str, Any] = {
            'profile_ids': profile_ids,
            'text': text,
            'shorten': shorten,
            'now': now,
        }
        
        # Add media if provided
        if media:
            if 'photo' in media:
                data['media'] = {'photo': media['photo']}
            if 'link' in media:
                data['media'] = data.get('media', {})
                data['media']['link'] = media['link']
            if 'thumbnail' in media:
                data['media'] = data.get('media', {})
                data['media']['thumbnail'] = media['thumbnail']
        
        # Add scheduled time if provided
        if scheduled_at:
            # Convert to Unix timestamp
            data['scheduled_at'] = int(scheduled_at.timestamp())
        
        try:
            response = await self._make_request('POST', '/updates/create.json', data=data)
            logger.info(f"Created Buffer post for {len(profile_ids)} profiles")
            return response
        except BufferAPIError as e:
            logger.error(f"Failed to create Buffer post: {e.message}")
            raise
    
    async def update_post(self, post_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing Buffer post.
        
        Args:
            post_id: Buffer update/post ID
            data: Updated post data (text, media, scheduled_at, etc.)
        
        Returns:
            Updated post information
        
        Raises:
            BufferAPIError: If request fails
        """
        # Convert scheduled_at to timestamp if present
        if 'scheduled_at' in data and isinstance(data['scheduled_at'], datetime):
            data['scheduled_at'] = int(data['scheduled_at'].timestamp())
        
        try:
            response = await self._make_request('POST', f'/updates/{post_id}/update.json', data=data)
            logger.info(f"Updated Buffer post: {post_id}")
            return response
        except BufferAPIError as e:
            logger.error(f"Failed to update Buffer post {post_id}: {e.message}")
            raise
    
    async def delete_post(self, post_id: str) -> Dict[str, Any]:
        """Delete a Buffer post.
        
        Args:
            post_id: Buffer update/post ID
        
        Returns:
            Deletion confirmation
        
        Raises:
            BufferAPIError: If request fails
        """
        try:
            response = await self._make_request('POST', f'/updates/{post_id}/destroy.json')
            logger.info(f"Deleted Buffer post: {post_id}")
            return response
        except BufferAPIError as e:
            logger.error(f"Failed to delete Buffer post {post_id}: {e.message}")
            raise
    
    async def get_post(self, post_id: str) -> Dict[str, Any]:
        """Get information about a specific post.
        
        Args:
            post_id: Buffer update/post ID
        
        Returns:
            Post information
        
        Raises:
            BufferAPIError: If request fails
        """
        try:
            response = await self._make_request('GET', f'/updates/{post_id}.json')
            logger.info(f"Retrieved Buffer post: {post_id}")
            return response
        except BufferAPIError as e:
            logger.error(f"Failed to get Buffer post {post_id}: {e.message}")
            raise
    
    async def get_post_analytics(self, post_id: str) -> Dict[str, Any]:
        """Get analytics for a specific post.
        
        Args:
            post_id: Buffer update/post ID
        
        Returns:
            Post analytics data (likes, shares, clicks, reach, etc.)
        
        Raises:
            BufferAPIError: If request fails
        """
        try:
            # Get post details which include statistics
            post_data = await self._make_request('GET', f'/updates/{post_id}.json')
            
            # Extract analytics from statistics field
            statistics = post_data.get('statistics', {})
            
            analytics = {
                'post_id': post_id,
                'likes': statistics.get('likes', 0),
                'comments': statistics.get('comments', 0),
                'shares': statistics.get('shares', 0),
                'clicks': statistics.get('clicks', 0),
                'reach': statistics.get('reach', 0),
                'impressions': statistics.get('impressions', 0),
                'engagement_rate': statistics.get('engagement_rate', 0.0),
                'retrieved_at': datetime.utcnow().isoformat(),
            }
            
            logger.info(f"Retrieved analytics for Buffer post: {post_id}")
            return analytics
        except BufferAPIError as e:
            logger.error(f"Failed to get analytics for Buffer post {post_id}: {e.message}")
            raise
    
    async def get_profile_analytics(
        self,
        profile_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get analytics for a specific profile.
        
        Args:
            profile_id: Buffer profile ID
            start_date: Start date for analytics period
            end_date: End date for analytics period
        
        Returns:
            Profile analytics data
        
        Raises:
            BufferAPIError: If request fails
        """
        params = {}
        if start_date:
            params['start'] = start_date.strftime('%Y-%m-%d')
        if end_date:
            params['end'] = end_date.strftime('%Y-%m-%d')
        
        try:
            response = await self._make_request(
                'GET',
                f'/profiles/{profile_id}/analytics.json',
                params=params,
            )
            logger.info(f"Retrieved analytics for Buffer profile: {profile_id}")
            return response
        except BufferAPIError as e:
            logger.error(f"Failed to get analytics for Buffer profile {profile_id}: {e.message}")
            raise
    
    async def test_connection(self) -> bool:
        """Test the Buffer API connection.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            await self.authenticate()
            return True
        except BufferAPIError:
            return False
