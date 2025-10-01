"""Error handling utilities for API operations."""
import logging
from typing import Dict, Any, Optional
from fastapi import HTTPException
from src.services.jira_service import JiraServiceError
from src.services.confluence_service import ConfluenceServiceError

logger = logging.getLogger(__name__)


class APIErrorHandler:
    """Centralized error handling for API operations."""
    
    @staticmethod
    def handle_service_error(error: Exception, service_name: str = "API") -> HTTPException:
        """
        Handle service-specific errors and convert them to HTTP exceptions.
        
        Args:
            error: The exception that occurred
            service_name: Name of the service for logging
            
        Returns:
            HTTPException with appropriate status code and message
        """
        if isinstance(error, (JiraServiceError, ConfluenceServiceError)):
            # Handle authentication errors
            if "authentication failed" in str(error).lower() or "invalid or expired token" in str(error).lower():
                logger.warning(f"{service_name} authentication error: {str(error)}")
                return HTTPException(
                    status_code=401,
                    detail={
                        "error": "Authentication Error",
                        "message": str(error),
                        "code": "AUTH_FAILED"
                    }
                )
            
            # Handle permission errors
            if "access forbidden" in str(error).lower() or "insufficient permissions" in str(error).lower():
                logger.warning(f"{service_name} permission error: {str(error)}")
                return HTTPException(
                    status_code=403,
                    detail={
                        "error": "Permission Error", 
                        "message": str(error),
                        "code": "ACCESS_FORBIDDEN"
                    }
                )
            
            # Handle network errors
            if "network error" in str(error).lower():
                logger.error(f"{service_name} network error: {str(error)}")
                return HTTPException(
                    status_code=502,
                    detail={
                        "error": "Network Error",
                        "message": "Unable to connect to external service",
                        "code": "NETWORK_ERROR"
                    }
                )
            
            # Handle rate limiting
            if "rate limit" in str(error).lower() or "too many requests" in str(error).lower():
                logger.warning(f"{service_name} rate limit error: {str(error)}")
                return HTTPException(
                    status_code=429,
                    detail={
                        "error": "Rate Limit Exceeded",
                        "message": "Too many requests. Please try again later.",
                        "code": "RATE_LIMIT"
                    }
                )
            
            # Generic service error
            logger.error(f"{service_name} service error: {str(error)}")
            return HTTPException(
                status_code=400,
                detail={
                    "error": f"{service_name} Error",
                    "message": str(error),
                    "code": "SERVICE_ERROR"
                }
            )
        
        # Handle generic exceptions
        logger.error(f"Unexpected {service_name} error: {str(error)}")
        return HTTPException(
            status_code=500,
            detail={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred",
                "code": "INTERNAL_ERROR"
            }
        )
    
    @staticmethod
    def create_error_response(
        error_code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a standardized error response.
        
        Args:
            error_code: Error code identifier
            message: Human-readable error message
            details: Additional error details
            
        Returns:
            Standardized error response dictionary
        """
        response = {
            "success": False,
            "error": {
                "code": error_code,
                "message": message
            }
        }
        
        if details:
            response["error"]["details"] = details
        
        return response
    
    @staticmethod
    def create_success_response(
        data: Any,
        message: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a standardized success response.
        
        Args:
            data: Response data
            message: Optional success message
            meta: Optional metadata
            
        Returns:
            Standardized success response dictionary
        """
        response = {
            "success": True,
            "data": data
        }
        
        if message:
            response["message"] = message
        
        if meta:
            response["meta"] = meta
        
        return response


def log_api_error(endpoint: str, error: Exception, user_id: Optional[str] = None):
    """
    Log API errors with context information.
    
    Args:
        endpoint: The API endpoint where error occurred
        error: The exception that occurred
        user_id: Optional user identifier
    """
    context = {
        "endpoint": endpoint,
        "error_type": type(error).__name__,
        "error_message": str(error)
    }
    
    if user_id:
        context["user_id"] = user_id
    
    logger.error(f"API Error in {endpoint}: {error}", extra=context)


def handle_validation_error(error: Exception) -> HTTPException:
    """
    Handle validation errors from Pydantic models.
    
    Args:
        error: Pydantic validation error
        
    Returns:
        HTTPException with validation error details
    """
    return HTTPException(
        status_code=422,
        detail={
            "error": "Validation Error",
            "message": "Request data validation failed",
            "details": str(error),
            "code": "VALIDATION_ERROR"
        }
    )
