"""Tests for Social Accounts API endpoints."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.social_account import SocialAccount


class TestSocialAccountsAPI:
    """Test suite for Social Accounts endpoints."""

    @pytest.mark.asyncio
    async def test_create_social_account(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession
    ):
        """Test creating a new social account."""
        payload = {
            "platform": "twitter",
            "account_name": "@testuser",
            "buffer_profile_id": "buf_123",
            "access_token": "token_123"
        }

        response = await client.post(
            "/api/v1/social-accounts",
            json=payload,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["platform"] == "twitter"
        assert data["account_name"] == "@testuser"
        assert data["is_active"] is True

    @pytest.mark.asyncio
    async def test_get_social_account(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_social_account: SocialAccount
    ):
        """Test retrieving a social account by ID."""
        response = await client.get(
            f"/api/v1/social-accounts/{test_social_account.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_social_account.id
        assert data["platform"] == test_social_account.platform

    @pytest.mark.asyncio
    async def test_list_social_accounts(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_social_account: SocialAccount
    ):
        """Test listing all social accounts for a user."""
        response = await client.get(
            "/api/v1/social-accounts",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["platform"] == test_social_account.platform

    @pytest.mark.asyncio
    async def test_update_social_account(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_social_account: SocialAccount
    ):
        """Test updating a social account."""
        payload = {
            "account_name": "@updated_user",
            "is_active": False
        }

        response = await client.put(
            f"/api/v1/social-accounts/{test_social_account.id}",
            json=payload,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["account_name"] == "@updated_user"
        assert data["is_active"] is False

    @pytest.mark.asyncio
    async def test_delete_social_account(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_social_account: SocialAccount
    ):
        """Test deleting a social account."""
        response = await client.delete(
            f"/api/v1/social-accounts/{test_social_account.id}",
            headers=auth_headers
        )

        assert response.status_code == 200

        # Verify account is deleted
        get_response = await client.get(
            f"/api/v1/social-accounts/{test_social_account.id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_test_connection(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_social_account: SocialAccount
    ):
        """Test testing social account connection."""
        response = await client.post(
            f"/api/v1/social-accounts/{test_social_account.id}/test-connection",
            headers=auth_headers
        )

        # Should return success or failure status
        assert response.status_code in [200, 400, 503]

    @pytest.mark.asyncio
    async def test_unauthorized_access(
        self,
        client: AsyncClient,
        test_social_account: SocialAccount
    ):
        """Test accessing social account without authentication."""
        response = await client.get(
            f"/api/v1/social-accounts/{test_social_account.id}"
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_create_duplicate_account(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_social_account: SocialAccount
    ):
        """Test creating duplicate social account."""
        payload = {
            "platform": test_social_account.platform,
            "account_name": test_social_account.account_name,
            "buffer_profile_id": "buf_new",
            "access_token": "token_new"
        }

        response = await client.post(
            "/api/v1/social-accounts",
            json=payload,
            headers=auth_headers
        )

        # May succeed or fail depending on business rules
        assert response.status_code in [200, 400, 409]
