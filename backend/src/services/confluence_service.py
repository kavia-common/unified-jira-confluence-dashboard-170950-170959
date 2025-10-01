"""Confluence API service client for managing Confluence operations."""
import httpx
from typing import Dict, List, Optional, Any
from src.models.auth import TokenInfo, AuthMethod


class ConfluenceServiceError(Exception):
    """Custom exception for Confluence service errors."""
    pass


class ConfluenceService:
    """Service class for Confluence API interactions."""
    
    def __init__(self, token_info: TokenInfo):
        """Initialize Confluence service with authentication info."""
        self.token_info = token_info
        self.base_url = self._get_base_url()
        
    def _get_base_url(self) -> str:
        """Get the base URL for Confluence API."""
        if self.token_info.auth_method == AuthMethod.API_TOKEN:
            if not self.token_info.domain:
                raise ConfluenceServiceError("Domain is required for API token authentication")
            return f"https://{self.token_info.domain}/wiki/rest/api"
        else:
            # For OAuth, we need to get the cloudid from accessible resources
            return "https://api.atlassian.com/ex/confluence"
    
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
    
    async def get_spaces(self) -> List[Dict[str, Any]]:
        """
        Fetch Confluence spaces.
        
        Returns:
            List of space dictionaries with space information
            
        Raises:
            ConfluenceServiceError: If API call fails
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
                        raise ConfluenceServiceError(f"Failed to get accessible resources: {resources_response.status_code}")
                    
                    resources = resources_response.json()
                    if not resources:
                        return []
                    
                    # Use the first available site
                    site_id = resources[0]["id"]
                    url = f"https://api.atlassian.com/ex/confluence/{site_id}/wiki/rest/api/space"
                else:
                    # For API token
                    url = f"{self.base_url}/space"
                
                # Add query parameters for expanded information
                params = {
                    "expand": "description.plain,icon",
                    "limit": 50
                }
                
                response = await client.get(url, headers=headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    spaces = data.get("results", [])
                    
                    # Return formatted space data
                    return [
                        {
                            "id": space.get("id"),
                            "key": space.get("key"),
                            "name": space.get("name"),
                            "type": space.get("type"),
                            "status": space.get("status"),
                            "description": space.get("description", {}).get("plain", ""),
                            "icon": space.get("icon", {}),
                            "_links": space.get("_links", {})
                        }
                        for space in spaces
                    ]
                elif response.status_code == 401:
                    raise ConfluenceServiceError("Authentication failed - invalid or expired token")
                elif response.status_code == 403:
                    raise ConfluenceServiceError("Access forbidden - insufficient permissions")
                else:
                    raise ConfluenceServiceError(f"Failed to fetch spaces: HTTP {response.status_code}")
                    
            except httpx.RequestError as e:
                raise ConfluenceServiceError(f"Network error while fetching spaces: {str(e)}")
            except Exception as e:
                if isinstance(e, ConfluenceServiceError):
                    raise
                raise ConfluenceServiceError(f"Unexpected error while fetching spaces: {str(e)}")
    
    async def get_space_details(self, space_key: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific space.
        
        Args:
            space_key: The space key (e.g., 'SPACE')
            
        Returns:
            Space details dictionary or None if not found
            
        Raises:
            ConfluenceServiceError: If API call fails
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
                        raise ConfluenceServiceError(f"Failed to get accessible resources: {resources_response.status_code}")
                    
                    resources = resources_response.json()
                    if not resources:
                        return None
                    
                    site_id = resources[0]["id"]
                    url = f"https://api.atlassian.com/ex/confluence/{site_id}/wiki/rest/api/space/{space_key}"
                else:
                    url = f"{self.base_url}/space/{space_key}"
                
                params = {
                    "expand": "description.plain,icon,permissions"
                }
                
                response = await client.get(url, headers=headers, params=params)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    return None
                elif response.status_code == 401:
                    raise ConfluenceServiceError("Authentication failed - invalid or expired token")
                elif response.status_code == 403:
                    raise ConfluenceServiceError("Access forbidden - insufficient permissions")
                else:
                    raise ConfluenceServiceError(f"Failed to fetch space details: HTTP {response.status_code}")
                    
            except httpx.RequestError as e:
                raise ConfluenceServiceError(f"Network error while fetching space details: {str(e)}")
            except Exception as e:
                if isinstance(e, ConfluenceServiceError):
                    raise
                raise ConfluenceServiceError(f"Unexpected error while fetching space details: {str(e)}")
    
    async def get_space_content(self, space_key: str, limit: int = 25) -> List[Dict[str, Any]]:
        """
        Get content from a specific space.
        
        Args:
            space_key: The space key
            limit: Maximum number of content items to return
            
        Returns:
            List of content items
            
        Raises:
            ConfluenceServiceError: If API call fails
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
                        raise ConfluenceServiceError(f"Failed to get accessible resources: {resources_response.status_code}")
                    
                    resources = resources_response.json()
                    if not resources:
                        return []
                    
                    site_id = resources[0]["id"]
                    url = f"https://api.atlassian.com/ex/confluence/{site_id}/wiki/rest/api/content"
                else:
                    url = f"{self.base_url}/content"
                
                params = {
                    "spaceKey": space_key,
                    "expand": "version,space",
                    "limit": limit
                }
                
                response = await client.get(url, headers=headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("results", [])
                elif response.status_code == 401:
                    raise ConfluenceServiceError("Authentication failed - invalid or expired token")
                elif response.status_code == 403:
                    raise ConfluenceServiceError("Access forbidden - insufficient permissions")
                else:
                    raise ConfluenceServiceError(f"Failed to fetch space content: HTTP {response.status_code}")
                    
            except httpx.RequestError as e:
                raise ConfluenceServiceError(f"Network error while fetching space content: {str(e)}")
            except Exception as e:
                if isinstance(e, ConfluenceServiceError):
                    raise
                raise ConfluenceServiceError(f"Unexpected error while fetching space content: {str(e)}")
    
    async def validate_connection(self) -> bool:
        """
        Validate the connection to Confluence API.
        
        Returns:
            True if connection is valid, False otherwise
        """
        try:
            await self.get_spaces()
            return True
        except ConfluenceServiceError:
            return False
