# Note Taking App Technical Write-up

## Project Overview

A full-stack note-taking application built with Flask and MongoDB, featuring LLM-powered note metadata generation and deployed on Vercel's serverless platform. The app demonstrates modern web application architecture with API-first design, cloud database integration, and AI enhancement capabilities.

## System Architecture

### Backend Components

1. **API Layer (`src/routes/`)**
   - `note.py`: Note CRUD operations and LLM-powered metadata generation
   - `user.py`: User management endpoints
   - RESTful design with proper error handling and status codes

2. **Data Layer (`src/models/`)**
   - MongoDB integration using PyMongo
   - Separate models for users and notes
   - Clean separation of database operations from route logic

3. **LLM Integration (`src/llm.py`)**
   - OpenAI API integration for generating note metadata
   - Graceful fallback to local heuristics when LLM is unavailable
   - Error handling for missing credentials or API failures

### Key Features

1. **Note Management**
   - Create, read, update, delete operations
   - Automatic metadata generation using AI
   - Full-text search capabilities
   - Tag-based organization

2. **AI-Enhanced Experience**
   - Automatic title generation from content
   - Smart tag suggestions
   - Fallback to rule-based generation when AI unavailable

3. **Error Handling & Reliability**
   - Graceful degradation when services unavailable
   - Clear error messages for API consumers
   - Consistent error response format

## Technical Decisions

### 1. MongoDB Selection
- **Why**: Flexible schema for varied note content, good scaling characteristics
- **Implementation**: PyMongo with connection pooling
- **Benefits**: Native JSON support, rich query capabilities

### 2. LLM Integration Architecture
- **Primary**: GitHub-hosted LLM via models.github.ai
- **Fallback**: Local heuristic-based title/tag generation
- **Error Handling**: Graceful degradation to maintain service

### 3. Serverless Deployment
- **Platform**: Vercel
- **Architecture**: Flask app wrapped in serverless function
- **Benefits**: 
  - Auto-scaling
  - Zero cold-start database initialization
  - Global edge deployment

## Deployment Architecture

### Vercel Configuration
```json
{
  "version": 2,
  "builds": [
    { "src": "api/*.py", "use": "@vercel/python" },
    { "src": "src/static/**", "use": "@vercel/static" }
  ],
  "routes": [
    { "src": "/api/(.*)", "dest": "/api/index.py" },
    { "src": "/(.*)", "dest": "/api/index.py" }
  ]
}
```

### Environment Configuration
Required environment variables:
- `MONGODB_URI`: MongoDB connection string
- `MONGODB_DB`: Database name (defaults to note_app_db)
- `GITHUB_TOKEN`: For LLM API access (optional, falls back to local generation)

## API Documentation

### Notes Endpoints

#### POST /api/notes/generate
Generate a note with AI-powered metadata
```json
Request:
{
  "content": "Note content here"
}

Response:
{
  "id": "note_id",
  "title": "AI Generated Title",
  "content": "Note content here",
  "tags": ["suggested", "tags", "here"],
  "created_at": "2025-10-11T10:00:00Z",
  "updated_at": "2025-10-11T10:00:00Z"
}
```

#### GET /api/notes
Retrieve all notes
```json
Response:
[
  {
    "id": "note_id",
    "title": "Note Title",
    "content": "Content",
    "tags": ["tag1", "tag2"],
    "created_at": "2025-10-11T10:00:00Z",
    "updated_at": "2025-10-11T10:00:00Z"
  }
]
```

### Error Handling

The API uses consistent error response format:
```json
{
  "error": "Error message",
  "details": "Optional detailed explanation"
}
```

HTTP status codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 404: Not Found
- 500: Server Error (with helpful message)

## Future Improvements

1. **Performance Optimizations**
   - Implement caching layer
   - Add database indexing for search
   - Optimize LLM response caching

2. **Feature Enhancements**
   - Rich text editing
   - Collaborative editing
   - Version history
   - Export functionality

3. **Technical Debt & Infrastructure**
   - Add comprehensive test suite
   - Implement CI/CD pipeline
   - Add monitoring and logging
   - Database backup strategy

## Deployment Instructions

1. **Prerequisites**
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Environment Setup**
   ```bash
   # Required
   MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net
   MONGODB_DB=note_app_db
   
   # Optional (for AI features)
   GITHUB_TOKEN=github_pat_...
   ```

3. **Local Development**
   ```bash
   python src/main.py
   ```

4. **Vercel Deployment**
   ```bash
   vercel --prod
   ```

## Testing & Validation

The application includes several layers of validation:

1. **Data Validation**
   - Input sanitization
   - Schema validation
   - Type checking

2. **Error Handling**
   - Database connection errors
   - LLM service failures
   - Invalid input data

3. **Fallback Mechanisms**
   - Local title generation when LLM unavailable
   - Default tags when parsing fails
   - Static file serving when API unavailable

## Security Considerations

1. **Environment Variables**
   - Sensitive credentials stored in environment
   - No hardcoded secrets
   - Separate dev/prod configurations

2. **API Security**
   - Input validation
   - Error message sanitization
   - No sensitive data in responses

3. **Database Security**
   - Connection string with authentication
   - Minimal required permissions
   - Secure connection (SSL/TLS)

## Monitoring & Maintenance

1. **Health Checks**
   - Database connectivity
   - LLM service availability
   - API endpoint status

2. **Performance Monitoring**
   - Response times
   - Error rates
   - Resource utilization

3. **Updates & Maintenance**
   - Dependency updates
   - Security patches
   - Feature deployments