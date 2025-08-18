from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Solana Configuration
    solana_rpc_url: str = "https://api.mainnet-beta.solana.com"
    solana_devnet_rpc_url: str = "https://api.devnet.solana.com"
    solana_network: str = "mainnet"
    jupiter_api_url: str = "https://quote-api.jup.ag/v6"
    
    # Trading Configuration
    enable_real_trades: bool = False
    wallet_private_key: Optional[str] = None
    max_position_size_usd: float = 1000.0
    max_daily_loss_usd: float = 100.0
    min_liquidity_usd: float = 10000.0
    max_slippage_percent: float = 5.0
    
    # Database Configuration
    database_url: str = "postgresql://trading_bot:password@localhost:5432/trading_bot"
    redis_url: str = "redis://localhost:6379/0"
    
    # Risk Engine Configuration
    min_tvl_usd: float = 50000.0
    max_fee_percent: float = 3.0
    enable_honeypot_check: bool = True
    enable_rugpull_check: bool = True
    max_tax_percent: float = 10.0
    
    # Sniper Bot Configuration
    sniper_enabled: bool = True
    sniper_min_liquidity_usd: float = 10000.0
    sniper_max_slippage_percent: float = 3.0
    sniper_quick_exit_percent: float = 2.0
    
    # Notifications
    telegram_bot_token: Optional[str] = None
    discord_webhook_url: Optional[str] = None
    email_smtp_server: Optional[str] = None
    email_smtp_port: int = 587
    email_username: Optional[str] = None
    email_password: Optional[str] = None
    
    # Monitoring
    prometheus_enabled: bool = True
    grafana_enabled: bool = True
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    jwt_secret_key: str = "your-jwt-secret-key-change-in-production"
    access_token_expire_minutes: int = 30
    
    # API Rate Limits
    jupiter_rate_limit: int = 100
    solana_rpc_rate_limit: int = 1000
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Environment check
def is_production() -> bool:
    return os.getenv("ENVIRONMENT", "development").lower() == "production"

def is_devnet() -> bool:
    return settings.solana_network.lower() == "devnet"

def get_solana_rpc_url() -> str:
    return settings.solana_devnet_rpc_url if is_devnet() else settings.solana_rpc_url