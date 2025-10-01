# Unified Jira & Confluence Dashboard - Backend API

FastAPI backend service for the Unified Jira & Confluence Dashboard application. Handles OAuth2 and API token authentication with Atlassian services, manages user sessions, and provides REST API endpoints for frontend consumption.

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Atlassian Developer Account (for OAuth setup)

### Environment Setup

1. **Clone and navigate to the backend directory:**
   ```bash
   cd unified-jira-confluence-dashboard-170950-170959/backend
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and configure the required variables (see [Environment Variables](#environment-variables) section).

5. **Run the development server:**
   ```bash
   uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
   ```

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`.

## 🔧 Environment Variables

Configure these variables in your `.env` file:

### Required OAuth Configuration

| Variable | Description | Example |
|----------|-------------|---------|
| `ATLASSIAN_CLIENT_ID` | OAuth client ID from Atlassian Developer Console | `1234567890abcdef` |
| `ATLASSIAN_CLIENT_SECRET` | OAuth client secret from Atlassian Developer Console | `your-secret-here` |
| `JIRA_REDIRECT_URI` | OAuth redirect URI for Jira | `http://localhost:3000/auth/jira/callback` |
| `CONFLUENCE_REDIRECT_URI` | OAuth redirect URI for Confluence | `http://localhost:3000/auth/confluence/callback` |

### Required Application Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Application secret key for session management | `your-secret-key-change-in-production` |

### Optional Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `ATLASSIAN_OAUTH_URL` | Atlassian OAuth authorization URL | `https://auth.atlassian.com/authorize` |
| `ATLASSIAN_TOKEN_URL` | Atlassian token exchange URL | `https://auth.atlassian.com/oauth/token` |
| `ATLASSIAN_API_BASE` | Atlassian API base URL | `https://api.atlassian.com` |

## 🔐 OAuth Configuration

### Setting up Atlassian OAuth App

1. **Visit the Atlassian Developer Console:**
   - Go to [https://developer.atlassian.com/console/myapps/](https://developer.atlassian.com/console/myapps/)
   - Sign in with your Atlassian account

2. **Create a new app:**
   - Click "Create" → "OAuth 2.0 (3LO)"
   - Enter app name: "Unified Dashboard"
   - Add app description

3. **Configure OAuth settings:**
   - **Authorization callback URL:** `http://localhost:3000/auth/jira/callback`
   - **Authorization callback URL:** `http://localhost:3000/auth/confluence/callback`
   - **Permissions:**
     - Jira: `read:jira-user`, `read:jira-work`
     - Confluence: `read:confluence-user`, `read:confluence-content.summary`

4. **Get credentials:**
   - Copy the **Client ID** and **Client Secret**
   - Add them to your `.env` file

### API Token Authentication (Alternative)

Users can also authenticate using API tokens:

1. **Generate API token:**
   - Go to [https://id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
   - Click "Create API token"
   - Copy the generated token

2. **Use with the application:**
   - Domain: `your-company.atlassian.net`
   - Email: Your Atlassian account email
   - API Token: The generated token

## 📚 API Endpoints

### Authentication Endpoints

#### Jira Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/auth/jira/oauth/start` | Start Jira OAuth flow |
| `POST` | `/auth/jira/oauth/callback` | Handle OAuth callback |
| `POST` | `/auth/jira/api-token` | Authenticate with API token |

#### Confluence Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/auth/confluence/oauth/start` | Start Confluence OAuth flow |
| `POST` | `/auth/confluence/oauth/callback` | Handle OAuth callback |
| `POST` | `/auth/confluence/api-token` | Authenticate with API token |

#### General Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/logout` | Logout user and clear session |

### Data Endpoints

#### Jira Data

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/jira/projects` | Get all accessible Jira projects |
| `GET` | `/jira/projects/{project_key}` | Get specific project details |
| `GET` | `/jira/connection/validate` | Validate Jira connection |

#### Confluence Data

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/confluence/spaces` | Get all accessible Confluence spaces |
| `GET` | `/confluence/spaces/{space_key}` | Get specific space details |
| `GET` | `/confluence/spaces/{space_key}/content` | Get content from a space |
| `GET` | `/confluence/connection/validate` | Validate Confluence connection |

### Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API health check |

## 🔍 API Documentation

- **Interactive Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **OpenAPI Spec:** [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

## 🏗️ Project Structure

```
backend/
├── src/
│   ├── api/
│   │   ├── main.py              # FastAPI app initialization
│   │   └── endpoints/
│   │       ├── jira.py          # Jira API endpoints
│   │       └── confluence.py    # Confluence API endpoints
│   ├── auth/
│   │   ├── routes.py            # Authentication routes
│   │   └── utils.py             # Auth utilities
│   ├── config/
│   │   └── settings.py          # Application settings
│   ├── middleware/
│   │   └── auth.py              # Authentication middleware
│   ├── models/
│   │   ├── api.py               # API response models
│   │   └── auth.py              # Authentication models
│   ├── services/
│   │   ├── jira_service.py      # Jira API client
│   │   └── confluence_service.py # Confluence API client
│   └── utils/
│       └── error_handler.py     # Error handling utilities
├── interfaces/
│   └── openapi.json             # Generated OpenAPI specification
├── requirements.txt             # Python dependencies
└── .env.example                 # Environment variables template
```

## 🚨 Troubleshooting

### Common Issues

#### OAuth Errors

**Error:** `Invalid OAuth state`
- **Solution:** Ensure redirect URIs in your Atlassian app match the ones in your `.env` file exactly

**Error:** `Failed to exchange code for token`
- **Solution:** Verify your `ATLASSIAN_CLIENT_ID` and `ATLASSIAN_CLIENT_SECRET` are correct

#### API Token Errors

**Error:** `Authentication failed - invalid or expired token`
- **Solution:** 
  1. Regenerate your API token at [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens)
  2. Ensure you're using the correct email address
  3. Verify the domain format: `your-company.atlassian.net` (no https://)

#### Connection Issues

**Error:** `Network error while fetching projects/spaces`
- **Solution:** 
  1. Check your internet connection
  2. Verify Atlassian services are accessible
  3. Ensure your domain is correct and accessible

#### Permission Errors

**Error:** `Access forbidden - insufficient permissions`
- **Solution:** 
  1. Check that your Atlassian account has access to the requested resources
  2. For OAuth: Verify the scopes in your Atlassian app configuration
  3. For API tokens: Ensure your account has appropriate permissions

### Development Issues

#### Import Errors
```bash
# Make sure you're in the virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

#### Port Already in Use
```bash
# Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9

# Or use a different port
uvicorn src.api.main:app --reload --port 8001
```

### Deployment Considerations

#### Production Environment Variables
- Use strong, unique `SECRET_KEY`
- Use HTTPS URLs for redirect URIs
- Consider using environment-specific Atlassian apps

#### Security
- Enable CORS restrictions for production
- Use HTTPS for all communication
- Implement rate limiting
- Consider using Redis for session storage in production

## 🔧 Development

### Running Tests
```bash
pytest
```

### Code Quality
```bash
# Linting
flake8 src/

# Type checking (if using mypy)
mypy src/
```

### Generating OpenAPI Spec
```bash
python src/api/generate_openapi.py
```

## 📞 Support

For issues related to:
- **Atlassian API:** [Atlassian Developer Documentation](https://developer.atlassian.com/)
- **FastAPI:** [FastAPI Documentation](https://fastapi.tiangolo.com/)
- **This application:** Check the troubleshooting section above

## 🤝 Contributing

1. Follow PEP 8 style guidelines
2. Add docstrings to all public functions
3. Include error handling for external API calls
4. Update this README for any new features
