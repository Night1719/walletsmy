from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyUrl
from typing import Optional
import secrets


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    APP_NAME: str = "BG Surveys"
    APP_DESCRIPTION: str = "Corporate survey platform for Banter Group"
    APP_VERSION: str = "0.1.0"

    SECRET_KEY: str = secrets.token_urlsafe(32)

    # Database
    DATABASE_URL: str = "sqlite:///./bg_surveys.db"

    # Domain / networking
    DOMAIN: str = ""
    PUBLIC_URL: Optional[str] = None

    # LDAP settings (optional)
    LDAP_SERVER_URI: str = ""
    LDAP_BIND_DN: str = ""
    LDAP_BIND_PASSWORD: str = ""
    LDAP_BASE_DN: str = ""
    LDAP_USER_FILTER: str = "(objectClass=person)"
    LDAP_USERNAME_ATTRIBUTE: str = "uid"
    LDAP_EMAIL_ATTRIBUTE: str = "mail"

    # Default admin bootstrap (used by install.sh)
    BOOTSTRAP_ADMIN_USERNAME: str = ""
    BOOTSTRAP_ADMIN_EMAIL: str = ""
    BOOTSTRAP_ADMIN_PASSWORD: str = ""


settings = Settings()