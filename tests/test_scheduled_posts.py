"""Tests for Scheduled Posts API endpoints."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.scheduled_post import ScheduledPost
from app.models.social_account import SocialAccount
from app.models.campaign import Campaign


class TestScheduledPostsAPI:
    """Test suite for Scheduled Posts endpoints."""

    @pytest.mark.asyncio
    async def test_create_scheduled_post(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_social_account: SocialAccount,
        test_campaign: Campaign
    ):
        """Test creating a new scheduled post."""
        payload = {
            "social_account_id": test_social_account.id,
            "campaign_id": test_campaign.id,
            "content": "Test post content #test",
            "scheduled_time": "2025-12-25T10:00:00",
            "platform": "twitter"
        }

        response = await client.post(
            "/api/v1/posts",
            json=payload,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "Test post content #test"
        assert data["status"] == "draft"
        assert data["platform"] == "twitter"

    @pytest.mark.asyncio
    async def test_get_scheduled_post(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_scheduled_post: ScheduledPost
    ):
        """Test retrieving a scheduled post by ID."""
        response = await client.get(
            f"/api/v1/posts/{test_scheduled_post.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_scheduled_post.id
        assert data["content"] == test_scheduled_post.content

    @pytest.mark.asyncio
    async def test_list_scheduled_posts(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_scheduled_post: ScheduledPost
    ):
        """Test listing all scheduled posts."""
        response = await client.get(
            "/api/v1/posts",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_update_scheduled_post(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_scheduled_post: ScheduledPost
    ):
        """Test updating a scheduled post."""
        payload = {
            "content": "Updated post content",
            "scheduled_time": "2025-12-26T15:00:00"
        }

        response = await client.put(
            f"/api/v1/posts/{test_scheduled_post.id}",
            json=payload,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "Updated post content"

    @pytest.mark.asyncio
    async def test_delete_scheduled_post(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_scheduled_post: ScheduledPost
    ):
        """Test deleting a scheduled post."""
        response = await client.delete(
            f"/api/v1/posts/{test_scheduled_post.id}",
            headers=auth_headers
        )

        assert response.status_code == 200

        # Verify post is deleted
        get_response = await client.get(
            f"/api/v1/posts/{test_scheduled_post.id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_schedule_post_to_buffer(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_scheduled_post: ScheduledPost
    ):
        """Test scheduling a post via Buffer."""
        response = await client.post(
            f"/api/v1/posts/{test_scheduled_post.id}/schedule",
            headers=auth_headers
        )

        # Should return success or failure
        assert response.status_code in [200, 400, 503]

    @pytest.mark.asyncio
    async def test_get_content_calendar(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_scheduled_post: ScheduledPost
    ):
        """Test retrieving content calendar."""
        response = await client.get(
            "/api/v1/posts/calendar?start_date=2025-12-01&end_date=2025-12-31",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_bulk_schedule_posts(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_social_account: SocialAccount,
        test_campaign: Campaign
    ):
        """Test bulk scheduling posts."""
        payload = {
            "posts": [
                {
                    "social_account_id": test_social_account.id,
                    "campaign_id": test_campaign.id,
                    "content": f"Bulk post {i}",
                    "scheduled_time": f"2025-12-{25+i}T10:00:00",
                    "platform": "twitter"
                }
                for i in range(3)
            ]
        }

        response = await client.post(
            "/api/v1/posts/bulk",
            json=payload,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3

    @pytest.mark.asyncio
    async def test_filter_posts_by_status(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_scheduled_post: ScheduledPost
    ):
        """Test filtering posts by status."""
        response = await client.get(
            "/api/v1/posts?status=draft",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert all(post["status"] == "draft" for post in data)

    @pytest.mark.asyncio
    async def test_filter_posts_by_platform(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_scheduled_post: ScheduledPost
    ):
        """Test filtering posts by platform."""
        response = await client.get(
            "/api/v1/posts?platform=twitter",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert all(post["platform"] == "twitter" for post in data)
