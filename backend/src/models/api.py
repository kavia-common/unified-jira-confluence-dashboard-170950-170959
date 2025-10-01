"""API response models and schemas."""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class APIResponse(BaseModel):
    """Base API response model."""
    success: bool = Field(..., description="Whether the request was successful")
    message: Optional[str] = Field(None, description="Response message")


class ProjectResponse(BaseModel):
    """Jira project response model."""
    id: str = Field(..., description="Project ID")
    key: str = Field(..., description="Project key")
    name: str = Field(..., description="Project name")
    projectTypeKey: str = Field(..., description="Project type key")
    simplified: Optional[bool] = Field(None, description="Whether project is simplified")
    style: Optional[str] = Field(None, description="Project style")
    isPrivate: Optional[bool] = Field(None, description="Whether project is private")
    avatarUrls: Optional[Dict[str, str]] = Field(None, description="Avatar URLs")


class ProjectsResponse(APIResponse):
    """Response model for Jira projects list."""
    data: List[ProjectResponse] = Field(..., description="List of projects")
    total: int = Field(..., description="Total number of projects")


class ProjectDetailsResponse(APIResponse):
    """Response model for Jira project details."""
    data: Dict[str, Any] = Field(..., description="Detailed project information")


class SpaceResponse(BaseModel):
    """Confluence space response model."""
    id: str = Field(..., description="Space ID")
    key: str = Field(..., description="Space key")
    name: str = Field(..., description="Space name")
    type: str = Field(..., description="Space type")
    status: Optional[str] = Field(None, description="Space status")
    description: Optional[str] = Field(None, description="Space description")
    icon: Optional[Dict[str, Any]] = Field(None, description="Space icon information")
    _links: Optional[Dict[str, str]] = Field(None, description="Related links")


class SpacesResponse(APIResponse):
    """Response model for Confluence spaces list."""
    data: List[SpaceResponse] = Field(..., description="List of spaces")
    total: int = Field(..., description="Total number of spaces")


class SpaceDetailsResponse(APIResponse):
    """Response model for Confluence space details."""
    data: Dict[str, Any] = Field(..., description="Detailed space information")


class ContentResponse(BaseModel):
    """Confluence content response model."""
    id: str = Field(..., description="Content ID")
    type: str = Field(..., description="Content type")
    title: str = Field(..., description="Content title")
    status: Optional[str] = Field(None, description="Content status")
    _links: Optional[Dict[str, str]] = Field(None, description="Related links")


class SpaceContentResponse(APIResponse):
    """Response model for Confluence space content."""
    data: List[Dict[str, Any]] = Field(..., description="List of content items")
    total: int = Field(..., description="Total number of content items")
    space_key: str = Field(..., description="Space key")


class ConnectionValidationResponse(APIResponse):
    """Response model for connection validation."""
    valid: bool = Field(..., description="Whether the connection is valid")
