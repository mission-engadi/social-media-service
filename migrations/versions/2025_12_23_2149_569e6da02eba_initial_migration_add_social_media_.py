"""Initial migration: Add social media models

Revision ID: 569e6da02eba
Revises: 
Create Date: 2025-12-23 21:49:02.473161+00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '569e6da02eba'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema."""
    # Create enums
    social_platform_enum = postgresql.ENUM(
        'facebook', 'twitter', 'instagram', 'linkedin', 'tiktok', 'youtube',
        name='socialplatform', create_type=True
    )
    account_status_enum = postgresql.ENUM(
        'active', 'inactive', 'disconnected', 'error',
        name='accountstatus', create_type=True
    )
    post_type_enum = postgresql.ENUM(
        'text', 'image', 'video', 'link', 'carousel',
        name='posttype', create_type=True
    )
    post_status_enum = postgresql.ENUM(
        'draft', 'scheduled', 'published', 'failed', 'cancelled',
        name='poststatus', create_type=True
    )
    campaign_type_enum = postgresql.ENUM(
        'awareness', 'fundraising', 'event', 'general',
        name='campaigntype', create_type=True
    )
    campaign_status_enum = postgresql.ENUM(
        'draft', 'active', 'completed', 'cancelled',
        name='campaignstatus', create_type=True
    )
    
    social_platform_enum.create(op.get_bind(), checkfirst=True)
    account_status_enum.create(op.get_bind(), checkfirst=True)
    post_type_enum.create(op.get_bind(), checkfirst=True)
    post_status_enum.create(op.get_bind(), checkfirst=True)
    campaign_type_enum.create(op.get_bind(), checkfirst=True)
    campaign_status_enum.create(op.get_bind(), checkfirst=True)
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('username', sa.String(255), nullable=False, unique=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_users_id', 'users', ['id'])
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_username', 'users', ['username'])
    
    # Create campaigns table
    op.create_table(
        'campaigns',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('campaign_type', campaign_type_enum, nullable=False, server_default='general'),
        sa.Column('status', campaign_status_enum, nullable=False, server_default='draft'),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('target_platforms', postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column('goals', postgresql.JSONB(), nullable=True),
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_campaigns_id', 'campaigns', ['id'])
    op.create_index('ix_campaigns_name', 'campaigns', ['name'])
    op.create_index('ix_campaigns_campaign_type', 'campaigns', ['campaign_type'])
    op.create_index('ix_campaigns_status', 'campaigns', ['status'])
    op.create_index('ix_campaigns_start_date', 'campaigns', ['start_date'])
    op.create_index('ix_campaigns_end_date', 'campaigns', ['end_date'])
    op.create_index('ix_campaigns_created_by', 'campaigns', ['created_by'])
    
    # Create social_accounts table
    op.create_table(
        'social_accounts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('platform', social_platform_enum, nullable=False),
        sa.Column('account_name', sa.String(255), nullable=False),
        sa.Column('account_handle', sa.String(255), nullable=False),
        sa.Column('account_id', sa.String(255), nullable=True),
        sa.Column('status', account_status_enum, nullable=False, server_default='active'),
        sa.Column('access_token', sa.Text(), nullable=True),
        sa.Column('refresh_token', sa.Text(), nullable=True),
        sa.Column('token_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('buffer_profile_id', sa.String(255), nullable=True),
        sa.Column('is_primary', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('platform_metadata', postgresql.JSONB(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_social_accounts_id', 'social_accounts', ['id'])
    op.create_index('ix_social_accounts_platform', 'social_accounts', ['platform'])
    op.create_index('ix_social_accounts_account_name', 'social_accounts', ['account_name'])
    op.create_index('ix_social_accounts_account_id', 'social_accounts', ['account_id'])
    op.create_index('ix_social_accounts_status', 'social_accounts', ['status'])
    op.create_index('ix_social_accounts_buffer_profile_id', 'social_accounts', ['buffer_profile_id'])
    op.create_index('ix_social_accounts_created_by', 'social_accounts', ['created_by'])
    
    # Create scheduled_posts table
    op.create_table(
        'scheduled_posts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('content_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('title', sa.String(500), nullable=True),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('media_urls', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('platforms', postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column('post_type', post_type_enum, nullable=False, server_default='text'),
        sa.Column('scheduled_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('published_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', post_status_enum, nullable=False, server_default='draft'),
        sa.Column('buffer_post_ids', postgresql.JSONB(), nullable=True),
        sa.Column('platform_post_ids', postgresql.JSONB(), nullable=True),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_scheduled_posts_id', 'scheduled_posts', ['id'])
    op.create_index('ix_scheduled_posts_content_id', 'scheduled_posts', ['content_id'])
    op.create_index('ix_scheduled_posts_scheduled_time', 'scheduled_posts', ['scheduled_time'])
    op.create_index('ix_scheduled_posts_published_time', 'scheduled_posts', ['published_time'])
    op.create_index('ix_scheduled_posts_status', 'scheduled_posts', ['status'])
    op.create_index('ix_scheduled_posts_campaign_id', 'scheduled_posts', ['campaign_id'])
    op.create_index('ix_scheduled_posts_created_by', 'scheduled_posts', ['created_by'])
    
    # Create scheduled_post_accounts association table
    op.create_table(
        'scheduled_post_accounts',
        sa.Column('scheduled_post_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('social_account_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['scheduled_post_id'], ['scheduled_posts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['social_account_id'], ['social_accounts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('scheduled_post_id', 'social_account_id'),
    )
    
    # Create post_analytics table
    op.create_table(
        'post_analytics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('scheduled_post_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('social_account_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('platform', sa.String(50), nullable=False),
        sa.Column('platform_post_id', sa.String(255), nullable=False),
        sa.Column('likes', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('shares', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('comments', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('clicks', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('reach', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('impressions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('engagement_rate', sa.Numeric(5, 2), nullable=True),
        sa.Column('collected_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('raw_data', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['scheduled_post_id'], ['scheduled_posts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['social_account_id'], ['social_accounts.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_post_analytics_id', 'post_analytics', ['id'])
    op.create_index('ix_post_analytics_scheduled_post_id', 'post_analytics', ['scheduled_post_id'])
    op.create_index('ix_post_analytics_social_account_id', 'post_analytics', ['social_account_id'])
    op.create_index('ix_post_analytics_platform', 'post_analytics', ['platform'])
    op.create_index('ix_post_analytics_platform_post_id', 'post_analytics', ['platform_post_id'])
    op.create_index('ix_post_analytics_collected_at', 'post_analytics', ['collected_at'])
    
    # Create buffer_configs table
    op.create_table(
        'buffer_configs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('access_token', sa.Text(), nullable=False),
        sa.Column('refresh_token', sa.Text(), nullable=True),
        sa.Column('token_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('organization_id', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_buffer_configs_id', 'buffer_configs', ['id'])
    op.create_index('ix_buffer_configs_token_expires_at', 'buffer_configs', ['token_expires_at'])
    op.create_index('ix_buffer_configs_organization_id', 'buffer_configs', ['organization_id'])
    op.create_index('ix_buffer_configs_is_active', 'buffer_configs', ['is_active'])
    op.create_index('ix_buffer_configs_created_by', 'buffer_configs', ['created_by'])


def downgrade() -> None:
    """Downgrade database schema."""
    # Drop tables in reverse order (respecting foreign key constraints)
    op.drop_table('buffer_configs')
    op.drop_table('post_analytics')
    op.drop_table('scheduled_post_accounts')
    op.drop_table('scheduled_posts')
    op.drop_table('social_accounts')
    op.drop_table('campaigns')
    op.drop_table('users')
    
    # Drop enums
    postgresql.ENUM(name='campaignstatus').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='campaigntype').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='poststatus').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='posttype').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='accountstatus').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='socialplatform').drop(op.get_bind(), checkfirst=True)
