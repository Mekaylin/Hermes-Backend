"""initial

Revision ID: 0001_initial
Revises: 
Create Date: 2025-09-17 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'assets',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('symbol', sa.String(length=255), nullable=False, unique=True),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('category', sa.Enum('crypto','forex','stocks','commodities', name='assetcategory'), nullable=False),
    )

    op.create_table(
        'candles',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('asset_id', sa.Integer, sa.ForeignKey('assets.id'), nullable=False),
        sa.Column('timestamp', sa.DateTime, index=True),
        sa.Column('open', sa.Float),
        sa.Column('high', sa.Float),
        sa.Column('low', sa.Float),
        sa.Column('close', sa.Float),
        sa.Column('volume', sa.Float),
    )

    op.create_table(
        'predictions',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('asset_id', sa.Integer, sa.ForeignKey('assets.id'), nullable=False),
        sa.Column('timestamp', sa.DateTime, index=True),
        sa.Column('signal', sa.String(length=50)),
        sa.Column('confidence', sa.Float),
        sa.Column('entry', sa.Float),
        sa.Column('target', sa.Float),
        sa.Column('stop', sa.Float),
        sa.Column('rationale', sa.Text),
    )

    op.create_table(
        'news_items',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('asset_id', sa.Integer, sa.ForeignKey('assets.id'), nullable=True),
        sa.Column('timestamp', sa.DateTime),
        sa.Column('source', sa.String(length=255)),
        sa.Column('headline', sa.String(length=1024)),
        sa.Column('sentiment', sa.Float),
    )


def downgrade():
    op.drop_table('news_items')
    op.drop_table('predictions')
    op.drop_table('candles')
    op.drop_table('assets')
    # drop enum type if present
    try:
        op.execute('DROP TYPE IF EXISTS assetcategory')
    except Exception:
        pass
