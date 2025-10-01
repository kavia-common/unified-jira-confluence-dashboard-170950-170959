"""Authentication middleware for token validation."""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from src.auth.utils import get_session
import logging

logger = logging.getLogger(__name__)


class TokenValidationMiddleware(BaseHTTPMiddleware):
    """Middleware for validating authentication tokens on protected routes."""
    
    def __init__(self, app, protected_paths: list = None):
        """
        Initialize the middleware.
        
        Args:
            app: FastAPI application instance
            protected_paths: List of path prefixes that require authentication
        """
        super().__init__(app)
        self.protected_paths = protected_paths or ["/jira", "/confluence"]
    
    async def dispatch(self, request: Request, call_next):
        """
        Process the request and validate authentication if needed.
        
        Args:
            request: The incoming request
            call_next: The next middleware/endpoint to call
            
        Returns:
            Response from the next handler or error response
        """
        # Skip validation for non-protected paths
        path = request.url.path
        
        # Check if this path requires authentication
        requires_auth = any(path.startswith(protected_path) for protected_path in self.protected_paths)
        
        if not requires_auth:
            # Allow request to proceed without authentication
            return await call_next(request)
        
        # Skip validation for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)
        
        try:
            # Extract session ID from cookie
            session_id = request.cookies.get("session_id")
            
            if not session_id:
                logger.warning(f"No session ID found for protected path: {path}")
                return JSONResponse(
                    status_code=401,
                    content={
                        "success": False,
                        "error": "Authentication required",
                        "detail": "No session ID found. Please authenticate first."
                    }
                )
            
            # Validate session
            token_info = get_session(session_id)
            if not token_info:
                logger.warning(f"Invalid session ID for protected path: {path}")
                return JSONResponse(
                    status_code=401,
                    content={
                        "success": False,
                        "error": "Invalid session",
                        "detail": "Session has expired or is invalid. Please authenticate again."
                    }
                )
            
            # Check if the session is for the correct provider
            provider_required = None
            if path.startswith("/jira"):
                provider_required = "jira"
            elif path.startswith("/confluence"):
                provider_required = "confluence"
            
            if provider_required and token_info.provider.value != provider_required:
                logger.warning(f"Session not authenticated for {provider_required}: {path}")
                return JSONResponse(
                    status_code=403,
                    content={
                        "success": False,
                        "error": "Insufficient permissions",
                        "detail": f"Session not authenticated for {provider_required.title()}. Please authenticate with {provider_required.title()} first."
                    }
                )
            
            # Add token info to request state for use in endpoints
            request.state.token_info = token_info
            request.state.session_id = session_id
            
            # Proceed with the request
            response = await call_next(request)
            return response
            
        except Exception as e:
            logger.error(f"Error in token validation middleware: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": "Internal server error",
                    "detail": "An error occurred during authentication validation."
                }
            )


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for standardized error handling."""
    
    async def dispatch(self, request: Request, call_next):
        """
        Process the request and handle any unhandled exceptions.
        
        Args:
            request: The incoming request
            call_next: The next middleware/endpoint to call
            
        Returns:
            Response from the next handler or standardized error response
        """
        try:
            response = await call_next(request)
            return response
        except HTTPException:
            # Re-raise HTTP exceptions to be handled by FastAPI
            raise
        except Exception as e:
            logger.error(f"Unhandled exception in {request.url.path}: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": "Internal server error",
                    "detail": "An unexpected error occurred. Please try again later."
                }
            )
