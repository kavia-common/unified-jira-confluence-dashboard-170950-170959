"""Authentication utilities and helpers."""
import secrets
import uuid
from typing import Dict, Optional
import httpx
from src.models.auth import TokenInfo
from src.config.settings import settings


# In-memory storage for sessions and OAuth states
session_store: Dict[str, TokenInfo] = {}
oauth_states: Dict[str, Dict[str, str]] = {}


def generate_session_id() -> str:
    """Generate a unique session ID."""
    return str(uuid.uuid4())


def generate_oauth_state() -> str:
    """Generate a secure OAuth state parameter."""
    return secrets.token_urlsafe(32)


def store_oauth_state(state: str, provider: str, redirect_uri: str) -> None:
    """Store OAuth state for validation."""
    oauth_states[state] = {
        "provider": provider,
        "redirect_uri": redirect_uri
    }


def validate_oauth_state(state: str, provider: str) -> bool:
    """Validate OAuth state parameter."""
    if state not in oauth_states:
        return False
    
    stored_data = oauth_states[state]
    if stored_data["provider"] != provider:
        return False
    
    # Clean up used state
    del oauth_states[state]
    return True


def store_session(session_id: str, token_info: TokenInfo) -> None:
    """Store session token information."""
    session_store[session_id] = token_info


def get_session(session_id: str) -> Optional[TokenInfo]:
    """Get session token information."""
    return session_store.get(session_id)


def delete_session(session_id: str) -> bool:
    """Delete session."""
    if session_id in session_store:
        del session_store[session_id]
        return True
    return False


def build_oauth_url(provider: str, redirect_uri: str, state: str) -> str:
    """Build OAuth authorization URL."""
    scopes = {
        "jira": "read:jira-user read:jira-work",
        "confluence": "read:confluence-user read:confluence-content.summary"
    }
    
    scope = scopes.get(provider, "")
    
    params = {
        "audience": "api.atlassian.com",
        "client_id": settings.ATLASSIAN_CLIENT_ID,
        "scope": scope,
        "redirect_uri": redirect_uri,
        "state": state,
        "response_type": "code",
        "prompt": "consent"
    }
    
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    return f"{settings.ATLASSIAN_OAUTH_URL}?{query_string}"


async def exchange_code_for_token(code: str, redirect_uri: str) -> Optional[Dict]:
    """Exchange authorization code for access token."""
    if not settings.ATLASSIAN_CLIENT_ID or not settings.ATLASSIAN_CLIENT_SECRET:
        return None
    
    token_data = {
        "grant_type": "authorization_code",
        "client_id": settings.ATLASSIAN_CLIENT_ID,
        "client_secret": settings.ATLASSIAN_CLIENT_SECRET,
        "code": code,
        "redirect_uri": redirect_uri
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                settings.ATLASSIAN_TOKEN_URL,
                data=token_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None


async def get_user_info(access_token: str) -> Optional[Dict]:
    """Get user information from Atlassian API."""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{settings.ATLASSIAN_API_BASE}/me",
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None


async def validate_api_token(domain: str, email: str, api_token: str, provider: str) -> Optional[Dict]:
    """Validate API token credentials."""
    # Build the API URL based on provider
    if provider == "jira":
        api_url = f"https://{domain}/rest/api/3/myself"
    elif provider == "confluence":
        api_url = f"https://{domain}/wiki/rest/api/user/current"
    else:
        return None
    
    auth = (email, api_token)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(api_url, auth=auth)
            
            if response.status_code == 200:
                user_data = response.json()
                return {
                    "user_info": user_data,
                    "domain": domain,
                    "email": email
                }
            return None
        except Exception:
            return None
