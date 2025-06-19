"""Add user verification and security fields

Revision ID: add_user_security_fields
Revises: previous_migration
Create Date: 2025-06-19 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_user_security_fields'
down_revision = None  # Replace with actual previous revision
branch_labels = None
depends_on = None


def upgrade():
    """Add user verification and security fields"""
    # Add new columns to nguoi_dung table
    op.add_column('nguoi_dung', sa.Column('is_verified', sa.Boolean(), nullable=True))
    op.add_column('nguoi_dung', sa.Column('verification_token', sa.String(100), nullable=True))
    op.add_column('nguoi_dung', sa.Column('verification_token_expiry', sa.Integer(), nullable=True))
    op.add_column('nguoi_dung', sa.Column('active', sa.Boolean(), nullable=True))
    op.add_column('nguoi_dung', sa.Column('failed_login_attempts', sa.Integer(), nullable=True))
    op.add_column('nguoi_dung', sa.Column('last_failed_login', sa.DateTime(), nullable=True))
    op.add_column('nguoi_dung', sa.Column('account_locked_until', sa.DateTime(), nullable=True))
    
    # Set default values for existing users
    op.execute("UPDATE nguoi_dung SET is_verified = true WHERE is_verified IS NULL")
    op.execute("UPDATE nguoi_dung SET active = true WHERE active IS NULL") 
    op.execute("UPDATE nguoi_dung SET failed_login_attempts = 0 WHERE failed_login_attempts IS NULL")
    
    # Make columns non-nullable after setting defaults
    op.alter_column('nguoi_dung', 'is_verified', nullable=False, server_default=sa.text('false'))
    op.alter_column('nguoi_dung', 'active', nullable=False, server_default=sa.text('true'))
    op.alter_column('nguoi_dung', 'failed_login_attempts', nullable=False, server_default=sa.text('0'))


def downgrade():
    """Remove user verification and security fields"""
    op.drop_column('nguoi_dung', 'account_locked_until')
    op.drop_column('nguoi_dung', 'last_failed_login')
    op.drop_column('nguoi_dung', 'failed_login_attempts')
    op.drop_column('nguoi_dung', 'active')
    op.drop_column('nguoi_dung', 'verification_token_expiry')
    op.drop_column('nguoi_dung', 'verification_token')
    op.drop_column('nguoi_dung', 'is_verified')
