"""Confluence API endpoints."""
from fastapi import APIRouter, HTTPException, Depends, Cookie, Query
from typing import Optional
from src.services.confluence_service import ConfluenceService, ConfluenceServiceError
from src.auth.utils import get_session
from src.utils.error_handler import APIErrorHandler, log_api_error

router = APIRouter(prefix="/confluence", tags=["Confluence"])


async def get_confluence_service(session_id: Optional[str] = Cookie(None)) -> ConfluenceService:
    """
    Dependency to get authenticated Confluence service.
    
    Args:
        session_id: Session ID from cookie
        
    Returns:
        ConfluenceService instance
        
    Raises:
        HTTPException: If authentication fails
    """
    if not session_id:
        raise HTTPException(status_code=401, detail="Session ID not found")
    
    token_info = get_session(session_id)
    if not token_info:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    if token_info.provider.value != "confluence":
        raise HTTPException(status_code=403, detail="Session not authenticated for Confluence")
    
    return ConfluenceService(token_info)


# PUBLIC_INTERFACE
@router.get("/spaces",
           summary="Get Confluence Spaces",
           description="Fetch all accessible Confluence spaces for the authenticated user")
async def get_spaces(confluence_service: ConfluenceService = Depends(get_confluence_service)):
    """
    Get all accessible Confluence spaces for the authenticated user.
    
    This endpoint requires valid authentication (either OAuth or API token)
    and returns a list of spaces the user has access to.
    
    Returns:
        List of space objects containing:
        - id: Space ID
        - key: Space key
        - name: Space name
        - type: Space type (global, personal, etc.)
        - status: Space status
        - description: Space description
        - icon: Space icon information
        - _links: Related links
    
    Raises:
        HTTPException: If authentication fails or API call fails
    """
    try:
        spaces = await confluence_service.get_spaces()
        return APIErrorHandler.create_success_response(
            data=spaces,
            message=f"Retrieved {len(spaces)} spaces",
            meta={"total": len(spaces)}
        )
    except (ConfluenceServiceError, Exception) as e:
        log_api_error("/confluence/spaces", e)
        raise APIErrorHandler.handle_service_error(e, "Confluence")


# PUBLIC_INTERFACE
@router.get("/spaces/{space_key}",
           summary="Get Confluence Space Details",
           description="Fetch detailed information about a specific Confluence space")
async def get_space_details(
    space_key: str,
    confluence_service: ConfluenceService = Depends(get_confluence_service)
):
    """
    Get detailed information about a specific Confluence space.
    
    Args:
        space_key: The space key (e.g., 'SPACE', 'TEAM')
    
    Returns:
        Detailed space information including:
        - Basic space details
        - Space configuration
        - Permissions
        - Description and icon
    
    Raises:
        HTTPException: If space not found, authentication fails, or API call fails
    """
    try:
        space = await confluence_service.get_space_details(space_key)
        if not space:
            raise HTTPException(status_code=404, detail=f"Space with key '{space_key}' not found")
        
        return {
            "success": True,
            "data": space
        }
    except ConfluenceServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# PUBLIC_INTERFACE
@router.get("/spaces/{space_key}/content",
           summary="Get Confluence Space Content",
           description="Fetch content from a specific Confluence space")
async def get_space_content(
    space_key: str,
    limit: int = Query(25, ge=1, le=100, description="Number of content items to return"),
    confluence_service: ConfluenceService = Depends(get_confluence_service)
):
    """
    Get content from a specific Confluence space.
    
    Args:
        space_key: The space key (e.g., 'SPACE', 'TEAM')
        limit: Maximum number of content items to return (1-100)
    
    Returns:
        List of content items in the space including:
        - Pages
        - Blog posts
        - Other content types
    
    Raises:
        HTTPException: If space not found, authentication fails, or API call fails
    """
    try:
        content = await confluence_service.get_space_content(space_key, limit)
        return {
            "success": True,
            "data": content,
            "total": len(content),
            "space_key": space_key
        }
    except ConfluenceServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# PUBLIC_INTERFACE
@router.get("/connection/validate",
           summary="Validate Confluence Connection",
           description="Validate the current Confluence authentication and connection")
async def validate_connection(confluence_service: ConfluenceService = Depends(get_confluence_service)):
    """
    Validate the current Confluence authentication and connection.
    
    This endpoint checks if the current authentication is valid
    and the user can access Confluence APIs.
    
    Returns:
        Connection status and basic validation info
    
    Raises:
        HTTPException: If validation fails
    """
    try:
        is_valid = await confluence_service.validate_connection()
        return {
            "success": True,
            "valid": is_valid,
            "message": "Connection is valid" if is_valid else "Connection is invalid"
        }
    except Exception as e:
        return {
            "success": False,
            "valid": False,
            "message": f"Connection validation failed: {str(e)}"
        }
