"""Application settings and configuration."""
from pydantic import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Atlassian OAuth Configuration
    ATLASSIAN_CLIENT_ID: Optional[str] = None
    ATLASSIAN_CLIENT_SECRET: Optional[str] = None
    JIRA_REDIRECT_URI: Optional[str] = None
    CONFLUENCE_REDIRECT_URI: Optional[str] = None
    
    # Application settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ATLASSIAN_OAUTH_URL: str = "https://auth.atlassian.com/authorize"
    ATLASSIAN_TOKEN_URL: str = "https://auth.atlassian.com/oauth/token"
    ATLASSIAN_API_BASE: str = "https://api.atlassian.com"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
