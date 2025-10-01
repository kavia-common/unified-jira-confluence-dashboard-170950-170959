"""Jira API endpoints."""
from fastapi import APIRouter, HTTPException, Depends, Cookie
from typing import Optional
from src.services.jira_service import JiraService, JiraServiceError
from src.auth.utils import get_session
from src.utils.error_handler import APIErrorHandler, log_api_error

router = APIRouter(prefix="/jira", tags=["Jira"])


async def get_jira_service(session_id: Optional[str] = Cookie(None)) -> JiraService:
    """
    Dependency to get authenticated Jira service.
    
    Args:
        session_id: Session ID from cookie
        
    Returns:
        JiraService instance
        
    Raises:
        HTTPException: If authentication fails
    """
    if not session_id:
        raise HTTPException(status_code=401, detail="Session ID not found")
    
    token_info = get_session(session_id)
    if not token_info:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    if token_info.provider.value != "jira":
        raise HTTPException(status_code=403, detail="Session not authenticated for Jira")
    
    return JiraService(token_info)


# PUBLIC_INTERFACE
@router.get("/projects", 
           summary="Get Jira Projects",
           description="Fetch all accessible Jira projects for the authenticated user")
async def get_projects(jira_service: JiraService = Depends(get_jira_service)):
    """
    Get all accessible Jira projects for the authenticated user.
    
    This endpoint requires valid authentication (either OAuth or API token)
    and returns a list of projects the user has access to.
    
    Returns:
        List of project objects containing:
        - id: Project ID
        - key: Project key
        - name: Project name
        - projectTypeKey: Type of project
        - simplified: Whether it's a simplified project
        - style: Project style
        - isPrivate: Whether the project is private
        - avatarUrls: Project avatar URLs
    
    Raises:
        HTTPException: If authentication fails or API call fails
    """
    try:
        projects = await jira_service.get_projects()
        return APIErrorHandler.create_success_response(
            data=projects,
            message=f"Retrieved {len(projects)} projects",
            meta={"total": len(projects)}
        )
    except (JiraServiceError, Exception) as e:
        log_api_error("/jira/projects", e)
        raise APIErrorHandler.handle_service_error(e, "Jira")


# PUBLIC_INTERFACE
@router.get("/projects/{project_key}",
           summary="Get Jira Project Details",
           description="Fetch detailed information about a specific Jira project")
async def get_project_details(
    project_key: str,
    jira_service: JiraService = Depends(get_jira_service)
):
    """
    Get detailed information about a specific Jira project.
    
    Args:
        project_key: The project key (e.g., 'PROJ', 'TEST')
    
    Returns:
        Detailed project information including:
        - Basic project details
        - Project configuration
        - Permissions
        - Components and versions
    
    Raises:
        HTTPException: If project not found, authentication fails, or API call fails
    """
    try:
        project = await jira_service.get_project_details(project_key)
        if not project:
            raise HTTPException(status_code=404, detail=f"Project with key '{project_key}' not found")
        
        return {
            "success": True,
            "data": project
        }
    except JiraServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# PUBLIC_INTERFACE
@router.get("/connection/validate",
           summary="Validate Jira Connection",
           description="Validate the current Jira authentication and connection")
async def validate_connection(jira_service: JiraService = Depends(get_jira_service)):
    """
    Validate the current Jira authentication and connection.
    
    This endpoint checks if the current authentication is valid
    and the user can access Jira APIs.
    
    Returns:
        Connection status and basic validation info
    
    Raises:
        HTTPException: If validation fails
    """
    try:
        is_valid = await jira_service.validate_connection()
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
