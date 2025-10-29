"""Initial migration

Revision ID: 001
Revises:
Create Date: 2025-10-28 23:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create stocks table
    op.create_table('stocks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('market', sa.String(length=10), nullable=False),
        sa.Column('sector', sa.String(length=50), nullable=True),
        sa.Column('industry', sa.String(length=100), nullable=True),
        sa.Column('market_cap', sa.Float(), nullable=True),
        sa.Column('total_shares', sa.Float(), nullable=True),
        sa.Column('float_shares', sa.Float(), nullable=True),
        sa.Column('list_date', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_stocks_id'), 'stocks', ['id'], unique=False)
    op.create_index('idx_stock_symbol', 'stocks', ['symbol'], unique=False)
    op.create_index('idx_stock_market', 'stocks', ['market'], unique=False)
    op.create_index('idx_stock_sector', 'stocks', ['sector'], unique=False)
    op.create_index('idx_stock_active', 'stocks', ['is_active'], unique=False)
    op.create_constraint('uq_stock_symbol', 'stocks', ['symbol'], type_='unique')

    # Create stock_prices table
    op.create_table('stock_prices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('stock_id', sa.Integer(), nullable=False),
        sa.Column('trade_date', sa.DateTime(), nullable=False),
        sa.Column('open_price', sa.Float(), nullable=False),
        sa.Column('close_price', sa.Float(), nullable=False),
        sa.Column('high_price', sa.Float(), nullable=False),
        sa.Column('low_price', sa.Float(), nullable=False),
        sa.Column('volume', sa.Float(), nullable=False),
        sa.Column('turnover', sa.Float(), nullable=True),
        sa.Column('change_amount', sa.Float(), nullable=True),
        sa.Column('change_percent', sa.Float(), nullable=True),
        sa.Column('turnover_rate', sa.Float(), nullable=True),
        sa.Column('pe_ratio', sa.Float(), nullable=True),
        sa.Column('pb_ratio', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['stock_id'], ['stocks.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_stock_prices_id'), 'stock_prices', ['id'], unique=False)
    op.create_index('idx_stock_price_date', 'stock_prices', ['trade_date'], unique=False)
    op.create_index('idx_stock_price_stock_date', 'stock_prices', ['stock_id', 'trade_date'], unique=False)
    op.create_index('idx_stock_price_volume', 'stock_prices', ['volume'], unique=False)
    op.create_constraint('uq_stock_price_date', 'stock_prices', ['stock_id', 'trade_date'], type_='unique')

    # Create stock_indicators table
    op.create_table('stock_indicators',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('stock_id', sa.Integer(), nullable=False),
        sa.Column('trade_date', sa.DateTime(), nullable=False),
        sa.Column('indicator_type', sa.String(length=50), nullable=False),
        sa.Column('period', sa.Integer(), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('metadata_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['stock_id'], ['stocks.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_stock_indicators_id'), 'stock_indicators', ['id'], unique=False)
    op.create_index('idx_stock_indicator_type', 'stock_indicators', ['indicator_type'], unique=False)
    op.create_index('idx_stock_indicator_date', 'stock_indicators', ['trade_date'], unique=False)
    op.create_index('idx_stock_indicator_stock_date', 'stock_indicators', ['stock_id', 'trade_date'], unique=False)
    op.create_constraint('uq_stock_indicator', 'stock_indicators', ['stock_id', 'trade_date', 'indicator_type', 'period'], type_='unique')

    # Create stock_sectors table
    op.create_table('stock_sectors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=20), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('parent_code', sa.String(length=20), nullable=True),
        sa.Column('level', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_stock_sectors_id'), 'stock_sectors', ['id'], unique=False)
    op.create_index('idx_sector_code', 'stock_sectors', ['code'], unique=False)
    op.create_index('idx_sector_parent', 'stock_sectors', ['parent_code'], unique=False)
    op.create_index('idx_sector_level', 'stock_sectors', ['level'], unique=False)
    op.create_index('idx_sector_active', 'stock_sectors', ['is_active'], unique=False)
    op.create_constraint('uq_sector_code', 'stock_sectors', ['code'], type_='unique')

    # Create news_sources table
    op.create_table('news_sources',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('language', sa.String(length=10), nullable=True),
        sa.Column('country', sa.String(length=10), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('last_fetch', sa.DateTime(), nullable=True),
        sa.Column('fetch_interval', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_news_sources_id'), 'news_sources', ['id'], unique=False)
    op.create_index('idx_source_name', 'news_sources', ['name'], unique=False)
    op.create_index('idx_source_active', 'news_sources', ['is_active'], unique=False)
    op.create_index('idx_source_category', 'news_sources', ['category'], unique=False)
    op.create_index('idx_source_last_fetch', 'news_sources', ['last_fetch'], unique=False)
    op.create_constraint('uq_source_name', 'news_sources', ['name'], type_='unique')

    # Create news table
    op.create_table('news',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('url', sa.String(length=1000), nullable=False),
        sa.Column('author', sa.String(length=100), nullable=True),
        sa.Column('publish_time', sa.DateTime(), nullable=False),
        sa.Column('fetch_time', sa.DateTime(), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('tags', sa.String(length=500), nullable=True),
        sa.Column('language', sa.String(length=10), nullable=True),
        sa.Column('word_count', sa.Integer(), nullable=True),
        sa.Column('read_count', sa.Integer(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['source_id'], ['news_sources.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_news_id'), 'news', ['id'], unique=False)
    op.create_index('idx_news_publish_time', 'news', ['publish_time'], unique=False)
    op.create_index('idx_news_fetch_time', 'news', ['fetch_time'], unique=False)
    op.create_index('idx_news_category', 'news', ['category'], unique=False)
    op.create_index('idx_news_source', 'news', ['source_id'], unique=False)
    op.create_index('idx_news_deleted', 'news', ['is_deleted'], unique=False)
    op.create_index('idx_news_title_fulltext', 'news', ['title'], unique=False)
    op.create_constraint('uq_news_url', 'news', ['url'], type_='unique')

    # Create news_sentiments table
    op.create_table('news_sentiments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('news_id', sa.Integer(), nullable=False),
        sa.Column('model_name', sa.String(length=50), nullable=False),
        sa.Column('sentiment_label', sa.String(length=20), nullable=False),
        sa.Column('sentiment_score', sa.Float(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('positive_prob', sa.Float(), nullable=True),
        sa.Column('negative_prob', sa.Float(), nullable=True),
        sa.Column('neutral_prob', sa.Float(), nullable=True),
        sa.Column('analysis_time', sa.DateTime(), nullable=True),
        sa.Column('metadata_json', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['news_id'], ['news.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_news_sentiments_id'), 'news_sentiments', ['id'], unique=False)
    op.create_index('idx_sentiment_news', 'news_sentiments', ['news_id'], unique=False)
    op.create_index('idx_sentiment_label', 'news_sentiments', ['sentiment_label'], unique=False)
    op.create_index('idx_sentiment_score', 'news_sentiments', ['sentiment_score'], unique=False)
    op.create_index('idx_sentiment_analysis_time', 'news_sentiments', ['analysis_time'], unique=False)
    op.create_constraint('uq_news_sentiment_model', 'news_sentiments', ['news_id', 'model_name'], type_='unique')

    # Create news_entities table
    op.create_table('news_entities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('news_id', sa.Integer(), nullable=False),
        sa.Column('entity_text', sa.String(length=100), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_subtype', sa.String(length=50), nullable=True),
        sa.Column('start_position', sa.Integer(), nullable=True),
        sa.Column('end_position', sa.Integer(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('metadata_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['news_id'], ['news.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_news_entities_id'), 'news_entities', ['id'], unique=False)
    op.create_index('idx_entity_news', 'news_entities', ['news_id'], unique=False)
    op.create_index('idx_entity_type', 'news_entities', ['entity_type'], unique=False)
    op.create_index('idx_entity_text', 'news_entities', ['entity_text'], unique=False)
    op.create_index('idx_entity_subtype', 'news_entities', ['entity_subtype'], unique=False)

    # Create stock_realtime table
    op.create_table('stock_realtime',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('stock_id', sa.Integer(), nullable=False),
        sa.Column('current_price', sa.Float(), nullable=False),
        sa.Column('change_amount', sa.Float(), nullable=True),
        sa.Column('change_percent', sa.Float(), nullable=True),
        sa.Column('volume', sa.Float(), nullable=True),
        sa.Column('turnover', sa.Float(), nullable=True),
        sa.Column('bid_price', sa.Float(), nullable=True),
        sa.Column('ask_price', sa.Float(), nullable=True),
        sa.Column('bid_volume', sa.Float(), nullable=True),
        sa.Column('ask_volume', sa.Float(), nullable=True),
        sa.Column('high_price', sa.Float(), nullable=True),
        sa.Column('low_price', sa.Float(), nullable=True),
        sa.Column('open_price', sa.Float(), nullable=True),
        sa.Column('prev_close', sa.Float(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['stock_id'], ['stocks.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_stock_realtime_id'), 'stock_realtime', ['id'], unique=False)
    op.create_index('idx_realtime_stock', 'stock_realtime', ['stock_id'], unique=False)
    op.create_index('idx_realtime_updated', 'stock_realtime', ['updated_at'], unique=False)
    op.create_index('idx_realtime_change', 'stock_realtime', ['change_percent'], unique=False)
    op.create_constraint('uq_realtime_stock', 'stock_realtime', ['stock_id'], type_='unique')


def downgrade() -> None:
    # Drop tables in reverse order of creation
    op.drop_table('stock_realtime')
    op.drop_table('news_entities')
    op.drop_table('news_sentiments')
    op.drop_table('news')
    op.drop_table('news_sources')
    op.drop_table('stock_indicators')
    op.drop_table('stock_prices')
    op.drop_table('stock_sectors')
    op.drop_table('stocks')