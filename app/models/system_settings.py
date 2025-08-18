from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base


class SystemSettings(Base):
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)

    # Risk engine
    min_tvl_usd = Column(Float, default=10000.0)
    max_fee_percent = Column(Float, default=1.0)
    max_slippage_percent = Column(Float, default=1.0)
    enable_honeypot_check = Column(Boolean, default=True)
    enable_rugpull_check = Column(Boolean, default=True)
    max_tax_percent = Column(Float, default=10.0)
    volatility_filter_enabled = Column(Boolean, default=True)

    # Execution / Solana
    use_jito_bundles = Column(Boolean, default=False)
    priority_fee_micro_lamports = Column(Integer, default=0)
    compute_unit_limit = Column(Integer, default=200000)
    rpc_primary_url = Column(String(255), default="https://api.mainnet-beta.solana.com")
    rpc_fallback_urls = Column(Text, default="")  # comma-separated

    # Capital and risk
    use_dynamic_position_sizing = Column(Boolean, default=False)
    position_size_usd = Column(Float, default=100.0)
    kelly_fraction = Column(Float, default=0.1)
    max_daily_loss_usd = Column(Float, default=100.0)
    drawdown_risk_scaling = Column(Boolean, default=True)
    drawdown_step_pct = Column(Float, default=5.0)
    drawdown_risk_scale_pct = Column(Float, default=30.0)

    # Partial take profits / stops
    tp1_percent = Column(Float, default=3.0)
    tp1_size_percent = Column(Float, default=50.0)
    trailing_stop_enabled = Column(Boolean, default=True)
    trailing_stop_pct = Column(Float, default=2.0)
    hard_stop_loss_pct = Column(Float, default=5.0)

    # Sniper bot
    sniper_enabled = Column(Boolean, default=False)
    sniper_auto_trading = Column(Boolean, default=False)
    sniper_min_liquidity_usd = Column(Float, default=5000.0)
    sniper_max_slippage_percent = Column(Float, default=3.0)
    sniper_quick_exit_tp_pct = Column(Float, default=10.0)
    sniper_quick_exit_sl_pct = Column(Float, default=5.0)
    sniper_min_token_age_minutes = Column(Integer, default=3)
    sniper_min_volume_usd = Column(Float, default=1000.0)

    # Lists
    token_denylist = Column(Text, default="")  # comma-separated mints
    token_allowlist = Column(Text, default="")
    wallet_watchlist = Column(Text, default="")  # comma-separated addresses

    # Kill switch
    kill_switch_enabled = Column(Boolean, default=True)
    kill_on_error_rate_pct = Column(Float, default=20.0)
    kill_on_block_rate_pct = Column(Float, default=50.0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @staticmethod
    def parse_csv(text: str) -> list[str]:
        if not text:
            return []
        return [x.strip() for x in text.split(",") if x.strip()]

    @staticmethod
    def to_csv(items: list[str]) -> str:
        return ",".join(items or [])

