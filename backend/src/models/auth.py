"""Authentication models and schemas."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from enum import Enum


class AuthProvider(str, Enum):
    """Supported authentication providers."""
    JIRA = "jira"
    CONFLUENCE = "confluence"


class AuthMethod(str, Enum):
    """Supported authentication methods."""
    OAUTH = "oauth"
    API_TOKEN = "api_token"


class OAuthStartResponse(BaseModel):
    """Response for OAuth start endpoint."""
    auth_url: str = Field(..., description="OAuth authorization URL to redirect user to")
    state: str = Field(..., description="OAuth state parameter for security")


class OAuthCallbackRequest(BaseModel):
    """Request model for OAuth callback."""
    code: str = Field(..., description="Authorization code from OAuth provider")
    state: str = Field(..., description="OAuth state parameter")


class APITokenRequest(BaseModel):
    """Request model for API token authentication."""
    domain: str = Field(..., description="Atlassian domain (e.g., your-company.atlassian.net)")
    email: str = Field(..., description="User email address")
    api_token: str = Field(..., description="API token from Atlassian")


class AuthResponse(BaseModel):
    """Standard authentication response."""
    success: bool = Field(..., description="Whether authentication was successful")
    message: str = Field(..., description="Response message")
    session_id: Optional[str] = Field(None, description="Session ID for authenticated user")
    user_info: Optional[Dict[str, Any]] = Field(None, description="User information")


class TokenInfo(BaseModel):
    """Token information stored in session."""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "Bearer"
    expires_at: Optional[int] = None
    domain: Optional[str] = None
    user_info: Optional[Dict[str, Any]] = None
    auth_method: AuthMethod
    provider: AuthProvider
