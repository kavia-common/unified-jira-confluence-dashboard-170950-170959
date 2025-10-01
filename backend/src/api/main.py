from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.auth.routes import router as auth_router
from src.api.endpoints.jira import router as jira_router
from src.api.endpoints.confluence import router as confluence_router
from src.middleware.auth import TokenValidationMiddleware, ErrorHandlingMiddleware

# FastAPI app with metadata for OpenAPI documentation
app = FastAPI(
    title="Unified Jira & Confluence Dashboard API",
    description="Backend API for connecting and managing Jira and Confluence accounts with OAuth2 and API token authentication",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "Authentication endpoints for Jira and Confluence OAuth2 and API token flows"
        },
        {
            "name": "Jira",
            "description": "Jira API endpoints for projects and project management"
        },
        {
            "name": "Confluence",
            "description": "Confluence API endpoints for spaces and content management"
        },
        {
            "name": "Health",
            "description": "Health check and system status endpoints"
        }
    ]
)

# Add middleware in the correct order
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(TokenValidationMiddleware, protected_paths=["/jira", "/confluence"])

# Include routers
app.include_router(auth_router)
app.include_router(jira_router)
app.include_router(confluence_router)

@app.get("/", tags=["Health"], summary="Health Check", description="Check if the API is running and healthy")
def health_check():
    """
    Health check endpoint to verify the API is running.
    
    Returns:
        dict: Status message indicating the API is healthy
    """
    return {"message": "Healthy", "status": "ok"}
