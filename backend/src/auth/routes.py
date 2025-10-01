"""Authentication routes for Jira and Confluence."""
from fastapi import APIRouter, HTTPException, Response
from src.models.auth import (
    OAuthStartResponse, OAuthCallbackRequest, APITokenRequest, 
    AuthResponse, AuthProvider, AuthMethod, TokenInfo
)
from src.auth.utils import (
    generate_session_id, generate_oauth_state, store_oauth_state,
    validate_oauth_state, store_session, build_oauth_url,
    exchange_code_for_token, get_user_info, validate_api_token
)
from src.config.settings import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


# PUBLIC_INTERFACE
@router.get("/jira/oauth/start", response_model=OAuthStartResponse, 
           summary="Start Jira OAuth Flow",
           description="Initiate OAuth2 authentication flow for Jira")
async def start_jira_oauth():
    """Start OAuth authentication flow for Jira."""
    if not settings.ATLASSIAN_CLIENT_ID or not settings.JIRA_REDIRECT_URI:
        raise HTTPException(
            status_code=500, 
            detail="OAuth configuration not properly set. Please configure ATLASSIAN_CLIENT_ID and JIRA_REDIRECT_URI."
        )
    
    state = generate_oauth_state()
    store_oauth_state(state, "jira", settings.JIRA_REDIRECT_URI)
    
    auth_url = build_oauth_url("jira", settings.JIRA_REDIRECT_URI, state)
    
    return OAuthStartResponse(auth_url=auth_url, state=state)


# PUBLIC_INTERFACE
@router.post("/jira/oauth/callback", response_model=AuthResponse,
            summary="Handle Jira OAuth Callback",
            description="Handle OAuth callback from Jira and exchange code for token")
async def jira_oauth_callback(request: OAuthCallbackRequest, response: Response):
    """Handle OAuth callback from Jira."""
    # Validate state
    if not validate_oauth_state(request.state, "jira"):
        raise HTTPException(status_code=400, detail="Invalid OAuth state")
    
    # Exchange code for token
    token_data = await exchange_code_for_token(request.code, settings.JIRA_REDIRECT_URI)
    if not token_data:
        raise HTTPException(status_code=400, detail="Failed to exchange code for token")
    
    # Get user info
    user_info = await get_user_info(token_data["access_token"])
    
    # Create session
    session_id = generate_session_id()
    token_info = TokenInfo(
        access_token=token_data["access_token"],
        refresh_token=token_data.get("refresh_token"),
        token_type=token_data.get("token_type", "Bearer"),
        user_info=user_info,
        auth_method=AuthMethod.OAUTH,
        provider=AuthProvider.JIRA
    )
    
    store_session(session_id, token_info)
    
    # Set session cookie
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=True,
        samesite="lax"
    )
    
    return AuthResponse(
        success=True,
        message="Successfully authenticated with Jira",
        session_id=session_id,
        user_info=user_info
    )


# PUBLIC_INTERFACE
@router.post("/jira/api-token", response_model=AuthResponse,
            summary="Authenticate with Jira API Token",
            description="Authenticate using Jira API token credentials")
async def jira_api_token(request: APITokenRequest, response: Response):
    """Authenticate with Jira using API token."""
    # Validate credentials
    validation_result = await validate_api_token(
        request.domain, request.email, request.api_token, "jira"
    )
    
    if not validation_result:
        raise HTTPException(status_code=401, detail="Invalid API token credentials")
    
    # Create session
    session_id = generate_session_id()
    token_info = TokenInfo(
        access_token=request.api_token,  # Store API token as access token
        token_type="Basic",
        domain=request.domain,
        user_info=validation_result["user_info"],
        auth_method=AuthMethod.API_TOKEN,
        provider=AuthProvider.JIRA
    )
    
    store_session(session_id, token_info)
    
    # Set session cookie
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=True,
        samesite="lax"
    )
    
    return AuthResponse(
        success=True,
        message="Successfully authenticated with Jira API token",
        session_id=session_id,
        user_info=validation_result["user_info"]
    )


# PUBLIC_INTERFACE
@router.get("/confluence/oauth/start", response_model=OAuthStartResponse,
           summary="Start Confluence OAuth Flow",
           description="Initiate OAuth2 authentication flow for Confluence")
async def start_confluence_oauth():
    """Start OAuth authentication flow for Confluence."""
    if not settings.ATLASSIAN_CLIENT_ID or not settings.CONFLUENCE_REDIRECT_URI:
        raise HTTPException(
            status_code=500,
            detail="OAuth configuration not properly set. Please configure ATLASSIAN_CLIENT_ID and CONFLUENCE_REDIRECT_URI."
        )
    
    state = generate_oauth_state()
    store_oauth_state(state, "confluence", settings.CONFLUENCE_REDIRECT_URI)
    
    auth_url = build_oauth_url("confluence", settings.CONFLUENCE_REDIRECT_URI, state)
    
    return OAuthStartResponse(auth_url=auth_url, state=state)


# PUBLIC_INTERFACE
@router.post("/confluence/oauth/callback", response_model=AuthResponse,
            summary="Handle Confluence OAuth Callback", 
            description="Handle OAuth callback from Confluence and exchange code for token")
async def confluence_oauth_callback(request: OAuthCallbackRequest, response: Response):
    """Handle OAuth callback from Confluence."""
    # Validate state
    if not validate_oauth_state(request.state, "confluence"):
        raise HTTPException(status_code=400, detail="Invalid OAuth state")
    
    # Exchange code for token
    token_data = await exchange_code_for_token(request.code, settings.CONFLUENCE_REDIRECT_URI)
    if not token_data:
        raise HTTPException(status_code=400, detail="Failed to exchange code for token")
    
    # Get user info
    user_info = await get_user_info(token_data["access_token"])
    
    # Create session
    session_id = generate_session_id()
    token_info = TokenInfo(
        access_token=token_data["access_token"],
        refresh_token=token_data.get("refresh_token"),
        token_type=token_data.get("token_type", "Bearer"),
        user_info=user_info,
        auth_method=AuthMethod.OAUTH,
        provider=AuthProvider.CONFLUENCE
    )
    
    store_session(session_id, token_info)
    
    # Set session cookie
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=True,
        samesite="lax"
    )
    
    return AuthResponse(
        success=True,
        message="Successfully authenticated with Confluence",
        session_id=session_id,
        user_info=user_info
    )


# PUBLIC_INTERFACE
@router.post("/confluence/api-token", response_model=AuthResponse,
            summary="Authenticate with Confluence API Token",
            description="Authenticate using Confluence API token credentials")
async def confluence_api_token(request: APITokenRequest, response: Response):
    """Authenticate with Confluence using API token."""
    # Validate credentials
    validation_result = await validate_api_token(
        request.domain, request.email, request.api_token, "confluence"
    )
    
    if not validation_result:
        raise HTTPException(status_code=401, detail="Invalid API token credentials")
    
    # Create session
    session_id = generate_session_id()
    token_info = TokenInfo(
        access_token=request.api_token,  # Store API token as access token
        token_type="Basic",
        domain=request.domain,
        user_info=validation_result["user_info"],
        auth_method=AuthMethod.API_TOKEN,
        provider=AuthProvider.CONFLUENCE
    )
    
    store_session(session_id, token_info)
    
    # Set session cookie
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=True,
        samesite="lax"
    )
    
    return AuthResponse(
        success=True,
        message="Successfully authenticated with Confluence API token",
        session_id=session_id,
        user_info=validation_result["user_info"]
    )


# PUBLIC_INTERFACE
@router.post("/logout", response_model=AuthResponse,
            summary="Logout User",
            description="Logout user and clear session")
async def logout(response: Response, session_id: str = None):
    """Logout user and clear session."""
    if session_id:
        from src.auth.utils import delete_session
        delete_session(session_id)
    
    response.delete_cookie("session_id")
    
    return AuthResponse(
        success=True,
        message="Successfully logged out"
    )
