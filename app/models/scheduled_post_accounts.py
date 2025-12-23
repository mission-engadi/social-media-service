"""Association table for ScheduledPost and SocialAccount many-to-many relationship.

This table links scheduled posts to the social accounts they will be published on.
"""

from uuid import UUID

from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.db.base_class import Base

scheduled_post_accounts = Table(
    "scheduled_post_accounts",
    Base.metadata,
    Column(
        "scheduled_post_id",
        PGUUID(as_uuid=True),
        ForeignKey("scheduled_posts.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "social_account_id",
        PGUUID(as_uuid=True),
        ForeignKey("social_accounts.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
