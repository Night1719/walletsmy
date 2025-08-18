-- Инициализация базы данных для Solana Trading Bot

-- Создание расширений
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Создание таблиц (если не существуют)
-- Примечание: SQLAlchemy создаст таблицы автоматически, но можно добавить дополнительные индексы

-- Индексы для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_trades_profile_id ON trades(profile_id);
CREATE INDEX IF NOT EXISTS idx_trades_created_at ON trades(created_at);
CREATE INDEX IF NOT EXISTS idx_trades_status ON trades(status);
CREATE INDEX IF NOT EXISTS idx_trades_strategy ON trades(strategy_name);

CREATE INDEX IF NOT EXISTS idx_positions_profile_id ON positions(profile_id);
CREATE INDEX IF NOT EXISTS idx_positions_token_mint ON positions(token_mint);
CREATE INDEX IF NOT EXISTS idx_positions_is_open ON positions(is_open);

CREATE INDEX IF NOT EXISTS idx_metric_snapshots_timestamp ON metric_snapshots(timestamp);

-- Создание представлений для аналитики
CREATE OR REPLACE VIEW daily_pnl_summary AS
SELECT 
    DATE(created_at) as trade_date,
    COUNT(*) as total_trades,
    COUNT(CASE WHEN pnl_usd > 0 THEN 1 END) as profitable_trades,
    COUNT(CASE WHEN pnl_usd < 0 THEN 1 END) as losing_trades,
    SUM(pnl_usd) as total_pnl,
    AVG(pnl_usd) as avg_pnl,
    SUM(CASE WHEN pnl_usd > 0 THEN pnl_usd ELSE 0 END) as total_profit,
    SUM(CASE WHEN pnl_usd < 0 THEN ABS(pnl_usd) ELSE 0 END) as total_loss
FROM trades 
WHERE status = 'executed'
GROUP BY DATE(created_at)
ORDER BY trade_date DESC;

-- Создание представления для статистики по стратегиям
CREATE OR REPLACE VIEW strategy_performance AS
SELECT 
    strategy_name,
    COUNT(*) as total_trades,
    COUNT(CASE WHEN pnl_usd > 0 THEN 1 END) as profitable_trades,
    COUNT(CASE WHEN pnl_usd < 0 THEN 1 END) as losing_trades,
    SUM(pnl_usd) as total_pnl,
    AVG(pnl_usd) as avg_pnl,
    (COUNT(CASE WHEN pnl_usd > 0 THEN 1 END)::float / COUNT(*) * 100) as win_rate
FROM trades 
WHERE status = 'executed'
GROUP BY strategy_name
ORDER BY total_pnl DESC;

-- Создание представления для активных позиций
CREATE OR REPLACE VIEW active_positions_summary AS
SELECT 
    token_symbol,
    COUNT(*) as position_count,
    SUM(amount) as total_amount,
    AVG(entry_price_usd) as avg_entry_price,
    SUM(unrealized_pnl_usd) as total_unrealized_pnl
FROM positions 
WHERE is_open = true
GROUP BY token_symbol
ORDER BY total_unrealized_pnl DESC;