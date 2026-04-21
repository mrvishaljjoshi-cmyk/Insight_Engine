"""Initial schema and new tables (market_data, watchlists, trade_journal)

Revision ID: 5f4e2a1c8d3b
Revises: 41a8f656bad0
Create Date: 2026-04-21 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

revision: str = '5f4e2a1c8d3b'
down_revision: Union[str, Sequence[str], None] = '41a8f656bad0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create market_data table
    op.create_table(
        'market_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(), nullable=False),
        sa.Column('exchange', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('open_price', sa.Float(), nullable=True),
        sa.Column('high_price', sa.Float(), nullable=True),
        sa.Column('low_price', sa.Float(), nullable=True),
        sa.Column('close_price', sa.Float(), nullable=True),
        sa.Column('volume', sa.Integer(), nullable=True),
        sa.Column('last_price', sa.Float(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_market_data_symbol'), 'market_data', ['symbol'], unique=False)
    op.create_index('ix_market_data_symbol_exchange', 'market_data', ['symbol', 'exchange'], unique=False)
    op.create_index(op.f('ix_market_data_timestamp'), 'market_data', ['timestamp'], unique=False)

    # Create watchlists table
    op.create_table(
        'watchlists',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_watchlists_user_id'), 'watchlists', ['user_id'], unique=False)

    # Create watchlist_items table
    op.create_table(
        'watchlist_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('watchlist_id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(), nullable=False),
        sa.Column('exchange', sa.String(), nullable=False),
        sa.Column('added_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['watchlist_id'], ['watchlists.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_watchlist_items_watchlist_id'), 'watchlist_items', ['watchlist_id'], unique=False)

    # Create trade_journal table
    op.create_table(
        'trade_journal',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('broker_id', sa.Integer(), nullable=True),
        sa.Column('symbol', sa.String(), nullable=False),
        sa.Column('exchange', sa.String(), nullable=False),
        sa.Column('trade_type', sa.Enum('INTRADAY', 'DELIVERY', 'FNO', name='tradetype'), nullable=False),
        sa.Column('entry_price', sa.Float(), nullable=False),
        sa.Column('exit_price', sa.Float(), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('entry_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('exit_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('pnl', sa.Float(), nullable=True),
        sa.Column('pnl_percentage', sa.Float(), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'OPEN', 'CLOSED', 'CANCELLED', name='tradestatus'), nullable=True),
        sa.Column('strategy', sa.String(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['broker_id'], ['broker_credentials.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_trade_journal_user_id'), 'trade_journal', ['user_id'], unique=False)
    op.create_index(op.f('ix_trade_journal_symbol'), 'trade_journal', ['symbol'], unique=False)
    op.create_index(op.f('ix_trade_journal_status'), 'trade_journal', ['status'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_trade_journal_status'), table_name='trade_journal')
    op.drop_index(op.f('ix_trade_journal_symbol'), table_name='trade_journal')
    op.drop_index(op.f('ix_trade_journal_user_id'), table_name='trade_journal')
    op.drop_table('trade_journal')
    op.drop_index(op.f('ix_watchlist_items_watchlist_id'), table_name='watchlist_items')
    op.drop_table('watchlist_items')
    op.drop_index(op.f('ix_watchlists_user_id'), table_name='watchlists')
    op.drop_table('watchlists')
    op.drop_index(op.f('ix_market_data_timestamp'), table_name='market_data')
    op.drop_index('ix_market_data_symbol_exchange', table_name='market_data')
    op.drop_index(op.f('ix_market_data_symbol'), table_name='market_data')
    op.drop_table('market_data')