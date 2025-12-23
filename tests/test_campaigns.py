"""Tests for Campaigns API endpoints."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.campaign import Campaign


class TestCampaignsAPI:
    """Test suite for Campaigns endpoints."""

    @pytest.mark.asyncio
    async def test_create_campaign(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test creating a new campaign."""
        payload = {
            "name": "Summer Campaign 2025",
            "description": "Summer promotion campaign",
            "start_date": "2025-06-01",
            "end_date": "2025-08-31",
            "status": "active"
        }

        response = await client.post(
            "/api/v1/campaigns",
            json=payload,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Summer Campaign 2025"
        assert data["status"] == "active"

    @pytest.mark.asyncio
    async def test_get_campaign(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_campaign: Campaign
    ):
        """Test retrieving a campaign by ID."""
        response = await client.get(
            f"/api/v1/campaigns/{test_campaign.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_campaign.id
        assert data["name"] == test_campaign.name

    @pytest.mark.asyncio
    async def test_list_campaigns(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_campaign: Campaign
    ):
        """Test listing all campaigns."""
        response = await client.get(
            "/api/v1/campaigns",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_update_campaign(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_campaign: Campaign
    ):
        """Test updating a campaign."""
        payload = {
            "name": "Updated Campaign Name",
            "status": "paused"
        }

        response = await client.put(
            f"/api/v1/campaigns/{test_campaign.id}",
            json=payload,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Campaign Name"
        assert data["status"] == "paused"

    @pytest.mark.asyncio
    async def test_delete_campaign(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_campaign: Campaign
    ):
        """Test deleting a campaign."""
        response = await client.delete(
            f"/api/v1/campaigns/{test_campaign.id}",
            headers=auth_headers
        )

        assert response.status_code == 200

        # Verify campaign is deleted
        get_response = await client.get(
            f"/api/v1/campaigns/{test_campaign.id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_campaign_analytics(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_campaign: Campaign
    ):
        """Test retrieving campaign analytics."""
        response = await client.get(
            f"/api/v1/campaigns/{test_campaign.id}/analytics",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "total_posts" in data or isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_get_campaign_posts(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_campaign: Campaign
    ):
        """Test retrieving posts for a campaign."""
        response = await client.get(
            f"/api/v1/campaigns/{test_campaign.id}/posts",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_filter_campaigns_by_status(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_campaign: Campaign
    ):
        """Test filtering campaigns by status."""
        response = await client.get(
            "/api/v1/campaigns?status=active",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert all(campaign["status"] == "active" for campaign in data)

    @pytest.mark.asyncio
    async def test_unauthorized_campaign_access(
        self,
        client: AsyncClient,
        test_campaign: Campaign
    ):
        """Test accessing campaign without authentication."""
        response = await client.get(
            f"/api/v1/campaigns/{test_campaign.id}"
        )

        assert response.status_code == 401
