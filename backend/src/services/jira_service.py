"""Jira API service client for managing Jira operations."""
import httpx
from typing import Dict, List, Optional, Any
from src.models.auth import TokenInfo, AuthMethod


class JiraServiceError(Exception):
    """Custom exception for Jira service errors."""
    pass


class JiraService:
    """Service class for Jira API interactions."""
    
    def __init__(self, token_info: TokenInfo):
        """Initialize Jira service with authentication info."""
        self.token_info = token_info
        self.base_url = self._get_base_url()
        
    def _get_base_url(self) -> str:
        """Get the base URL for Jira API."""
        if self.token_info.auth_method == AuthMethod.API_TOKEN:
            if not self.token_info.domain:
                raise JiraServiceError("Domain is required for API token authentication")
            return f"https://{self.token_info.domain}/rest/api/3"
        else:
            # For OAuth, we need to get the cloudid from accessible resources
            # This is a simplified approach - in production you'd cache this
            return "https://api.atlassian.com/ex/jira"
    
    def _get_headers(self) -> Dict[str, str]:
        """Get authentication headers."""
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        if self.token_info.auth_method == AuthMethod.OAUTH:
            headers["Authorization"] = f"Bearer {self.token_info.access_token}"
        elif self.token_info.auth_method == AuthMethod.API_TOKEN:
            # For API token, we use basic auth with email and token
            import base64
            user_info = self.token_info.user_info or {}
            email = user_info.get("emailAddress", "")
            credentials = f"{email}:{self.token_info.access_token}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            headers["Authorization"] = f"Basic {encoded_credentials}"
        
        return headers
    
    async def get_projects(self) -> List[Dict[str, Any]]:
        """
        Fetch Jira projects.
        
        Returns:
            List of project dictionaries with project information
            
        Raises:
            JiraServiceError: If API call fails
        """
        headers = self._get_headers()
        
        async with httpx.AsyncClient() as client:
            try:
                if self.token_info.auth_method == AuthMethod.OAUTH:
                    # For OAuth, first get accessible resources
                    resources_response = await client.get(
                        "https://api.atlassian.com/oauth/token/accessible-resources",
                        headers=headers
                    )
                    
                    if resources_response.status_code != 200:
                        raise JiraServiceError(f"Failed to get accessible resources: {resources_response.status_code}")
                    
                    resources = resources_response.json()
                    if not resources:
                        return []
                    
                    # Use the first available site
                    site_id = resources[0]["id"]
                    url = f"https://api.atlassian.com/ex/jira/{site_id}/rest/api/3/project"
                else:
                    # For API token
                    url = f"{self.base_url}/project"
                
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    projects = response.json()
                    # Return formatted project data
                    return [
                        {
                            "id": project.get("id"),
                            "key": project.get("key"),
                            "name": project.get("name"),
                            "projectTypeKey": project.get("projectTypeKey"),
                            "simplified": project.get("simplified"),
                            "style": project.get("style"),
                            "isPrivate": project.get("isPrivate", False),
                            "avatarUrls": project.get("avatarUrls", {})
                        }
                        for project in projects
                    ]
                elif response.status_code == 401:
                    raise JiraServiceError("Authentication failed - invalid or expired token")
                elif response.status_code == 403:
                    raise JiraServiceError("Access forbidden - insufficient permissions")
                else:
                    raise JiraServiceError(f"Failed to fetch projects: HTTP {response.status_code}")
                    
            except httpx.RequestError as e:
                raise JiraServiceError(f"Network error while fetching projects: {str(e)}")
            except Exception as e:
                if isinstance(e, JiraServiceError):
                    raise
                raise JiraServiceError(f"Unexpected error while fetching projects: {str(e)}")
    
    async def get_project_details(self, project_key: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific project.
        
        Args:
            project_key: The project key (e.g., 'PROJ')
            
        Returns:
            Project details dictionary or None if not found
            
        Raises:
            JiraServiceError: If API call fails
        """
        headers = self._get_headers()
        
        async with httpx.AsyncClient() as client:
            try:
                if self.token_info.auth_method == AuthMethod.OAUTH:
                    # Get accessible resources first
                    resources_response = await client.get(
                        "https://api.atlassian.com/oauth/token/accessible-resources",
                        headers=headers
                    )
                    
                    if resources_response.status_code != 200:
                        raise JiraServiceError(f"Failed to get accessible resources: {resources_response.status_code}")
                    
                    resources = resources_response.json()
                    if not resources:
                        return None
                    
                    site_id = resources[0]["id"]
                    url = f"https://api.atlassian.com/ex/jira/{site_id}/rest/api/3/project/{project_key}"
                else:
                    url = f"{self.base_url}/project/{project_key}"
                
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    return None
                elif response.status_code == 401:
                    raise JiraServiceError("Authentication failed - invalid or expired token")
                elif response.status_code == 403:
                    raise JiraServiceError("Access forbidden - insufficient permissions")
                else:
                    raise JiraServiceError(f"Failed to fetch project details: HTTP {response.status_code}")
                    
            except httpx.RequestError as e:
                raise JiraServiceError(f"Network error while fetching project details: {str(e)}")
            except Exception as e:
                if isinstance(e, JiraServiceError):
                    raise
                raise JiraServiceError(f"Unexpected error while fetching project details: {str(e)}")
    
    async def validate_connection(self) -> bool:
        """
        Validate the connection to Jira API.
        
        Returns:
            True if connection is valid, False otherwise
        """
        try:
            await self.get_projects()
            return True
        except JiraServiceError:
            return False
