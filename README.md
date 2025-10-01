# Unified Jira & Confluence Dashboard

A modern web application that allows users to connect their Atlassian Jira and Confluence accounts, authenticate via OAuth2 and API tokens, fetch relevant data, and display it in a unified, minimalistic dashboard interface.

## 🌟 Features

### Authentication Options
- **OAuth 2.0 (3LO):** Secure browser-based authentication with Atlassian
- **API Token:** Direct credential-based authentication for personal use

### Supported Services
- **Jira:** Project management and issue tracking
  - View all accessible projects
  - Project details and metadata
  - Connection validation
- **Confluence:** Documentation and knowledge management
  - View all accessible spaces
  - Space details and content
  - Connection validation

### Modern UI/UX
- **Ocean Professional** theme with classic styling
- Responsive design (mobile-first)
- Sidebar navigation with dynamic content
- Clean, professional interface

## 🏗️ Architecture

The application consists of two main components:

### Backend (FastAPI)
- **Location:** `unified-jira-confluence-dashboard-170950-170959/backend/`
- **Framework:** FastAPI with Python 3.8+
- **Purpose:** Handles authentication, API communication, session management
- **Port:** 8000 (development)

### Frontend (Next.js)
- **Location:** `unified-jira-confluence-dashboard-170950-170960/frontend/`
- **Framework:** Next.js 15 with React 19, TypeScript, Tailwind CSS
- **Purpose:** User interface and user experience
- **Port:** 3000 (development)

## 🚀 Quick Start

### Prerequisites
- **Backend:** Python 3.8+, pip
- **Frontend:** Node.js 18+, npm/yarn/pnpm
- **Atlassian Developer Account** (for OAuth setup)

### 1. Backend Setup

```bash
# Navigate to backend directory
cd unified-jira-confluence-dashboard-170950-170959/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Atlassian OAuth credentials

# Start backend server
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd unified-jira-confluence-dashboard-170950-170960/frontend

# Install dependencies
npm install

# Configure environment
cp .env.local.example .env.local
# Edit .env.local with backend URL

# Start frontend server
npm run dev
```

### 3. Access the Application

- **Frontend:** http://localhost:3000
- **Backend API Docs:** http://localhost:8000/docs
- **OpenAPI Spec:** http://localhost:8000/openapi.json

## 🔐 OAuth Configuration

### Setting up Atlassian OAuth App

1. **Visit Atlassian Developer Console:**
   - Go to [https://developer.atlassian.com/console/myapps/](https://developer.atlassian.com/console/myapps/)

2. **Create OAuth 2.0 (3LO) App:**
   - App name: "Unified Dashboard"
   - Callback URLs:
     - `http://localhost:3000/auth/jira/callback`
     - `http://localhost:3000/auth/confluence/callback`

3. **Configure Permissions:**
   - **Jira:** `read:jira-user`, `read:jira-work`
   - **Confluence:** `read:confluence-user`, `read:confluence-content.summary`

4. **Get Credentials:**
   - Copy Client ID and Client Secret to backend `.env` file

## 📋 Environment Variables

### Backend (.env)
```bash
# Required OAuth Configuration
ATLASSIAN_CLIENT_ID=your_client_id
ATLASSIAN_CLIENT_SECRET=your_client_secret
JIRA_REDIRECT_URI=http://localhost:3000/auth/jira/callback
CONFLUENCE_REDIRECT_URI=http://localhost:3000/auth/confluence/callback

# Application Security
SECRET_KEY=your-secure-secret-key
```

### Frontend (.env.local)
```bash
# Backend API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_SITE_URL=http://localhost:3000
```

## 📚 API Documentation

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/auth/jira/oauth/start` | Start Jira OAuth flow |
| `POST` | `/auth/jira/oauth/callback` | Handle Jira OAuth callback |
| `POST` | `/auth/jira/api-token` | Authenticate with Jira API token |
| `GET` | `/auth/confluence/oauth/start` | Start Confluence OAuth flow |
| `POST` | `/auth/confluence/oauth/callback` | Handle Confluence OAuth callback |
| `POST` | `/auth/confluence/api-token` | Authenticate with Confluence API token |
| `POST` | `/auth/logout` | Logout user |

### Data Endpoints

#### Jira
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/jira/projects` | Get all accessible projects |
| `GET` | `/jira/projects/{project_key}` | Get project details |
| `GET` | `/jira/connection/validate` | Validate connection |

#### Confluence
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/confluence/spaces` | Get all accessible spaces |
| `GET` | `/confluence/spaces/{space_key}` | Get space details |
| `GET` | `/confluence/spaces/{space_key}/content` | Get space content |
| `GET` | `/confluence/connection/validate` | Validate connection |

## 🎨 UI/UX Design

### Theme: Ocean Professional
- **Primary Color:** #1E3A8A (Blue 900)
- **Secondary Color:** #F59E0B (Amber 500)
- **Background:** #F3F4F6 (Gray 100)
- **Surface:** #FFFFFF (White)

### Layout Structure
1. **Sidebar Navigation:** Fixed left sidebar with connector options
2. **Main Content Area:** Dynamic content based on selected connector
3. **Responsive Design:** Mobile-friendly with collapsible sidebar

### User Flow
1. Select service (Jira/Confluence) from sidebar
2. Choose authentication method (OAuth or API Token)
3. Complete authentication process
4. View and interact with data (projects/spaces)

## 🚨 Troubleshooting

### Common Issues

#### OAuth Issues
- **Redirect URI mismatch:** Ensure URIs in Atlassian app match environment variables
- **Invalid client credentials:** Verify Client ID and Secret in `.env`

#### API Connection Issues
- **CORS errors:** Check backend CORS configuration
- **Network errors:** Verify backend is running and accessible

#### Authentication Issues
- **Session expired:** Re-authenticate through the UI
- **Invalid API token:** Generate new token in Atlassian account settings

### Development Issues

#### Backend
```bash
# Port already in use
lsof -ti:8000 | xargs kill -9

# Missing dependencies
pip install -r requirements.txt

# Database/session issues
# Sessions are stored in memory - restart backend to clear
```

#### Frontend
```bash
# Port conflicts
npm run dev -- -p 3001

# Build issues
rm -rf .next && npm run dev

# Dependencies
rm -rf node_modules package-lock.json && npm install
```

## 🚀 Deployment

### Production Considerations

#### Backend
- Use production-grade WSGI server (Gunicorn + Uvicorn)
- Implement persistent session storage (Redis/Database)
- Enable HTTPS and proper CORS configuration
- Use environment-specific OAuth apps

#### Frontend
- Build optimized static assets
- Configure production environment variables
- Enable CDN for static assets
- Implement proper error boundaries

### Deployment Platforms
- **Backend:** AWS, Google Cloud, Heroku, DigitalOcean
- **Frontend:** Vercel, Netlify, AWS Amplify

## 🔒 Security

- OAuth 2.0 implementation following Atlassian guidelines
- Secure session management with HTTP-only cookies
- CORS protection and CSP headers
- Input validation and sanitization
- Regular dependency updates

## 📞 Support & Documentation

- **Backend README:** `backend/README.md`
- **Frontend README:** `frontend/README.md`
- **API Documentation:** http://localhost:8000/docs
- **Atlassian Developer Docs:** https://developer.atlassian.com/

## 🤝 Contributing

1. Follow established coding standards
2. Add comprehensive documentation
3. Include error handling
4. Test thoroughly
5. Update relevant README files

## 📄 License

This project is for demonstration purposes. Please ensure compliance with Atlassian's API terms of service and your organization's policies when using in production.
