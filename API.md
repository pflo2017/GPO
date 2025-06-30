# GPO API Documentation

This document outlines the conceptual API structure for future integration with LSP Translation Management Systems (TMS) and Enterprise Resource Planning (ERP) systems.

## 🔐 Authentication

### API Key Authentication
```http
Authorization: Bearer YOUR_API_KEY
```

### OAuth 2.0 (Future Implementation)
```http
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## 📋 Base URL
```
https://api.gpo-product.com/v1
```

## 🎯 Core Endpoints

### Projects

#### Get All Projects
```http
GET /api/projects
```

**Query Parameters:**
- `status` (optional): Filter by project status
- `risk_level` (optional): Filter by risk level
- `client` (optional): Filter by client name
- `page` (optional): Page number for pagination
- `limit` (optional): Number of items per page

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "client_name": "MedCorp Inc.",
      "project_name": "Medical Manual Translation",
      "language_pair": "English-Spanish",
      "content_type": "Medical Documentation",
      "start_date": "2024-01-15",
      "due_date": "2024-02-15",
      "initial_word_count": 15000,
      "translated_words": 8000,
      "status": "In Progress",
      "gpo_risk_status": "Medium Risk",
      "gpo_risk_reason": "Behind schedule: 8000 of 15000 words translated",
      "gpo_recommendation": "Allocate additional linguist resources",
      "assigned_linguist_id": 5,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "pages": 8
  }
}
```

#### Get Project by ID
```http
GET /api/projects/{project_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "client_name": "MedCorp Inc.",
    "project_name": "Medical Manual Translation",
    "language_pair": "English-Spanish",
    "content_type": "Medical Documentation",
    "start_date": "2024-01-15",
    "due_date": "2024-02-15",
    "initial_word_count": 15000,
    "translated_words": 8000,
    "status": "In Progress",
    "gpo_risk_status": "Medium Risk",
    "gpo_risk_reason": "Behind schedule: 8000 of 15000 words translated",
    "gpo_recommendation": "Allocate additional linguist resources",
    "assigned_linguist_id": 5,
    "assigned_linguist": {
      "id": 5,
      "name": "Dr. Maria Rodriguez",
      "languages": "English-Spanish",
      "specialties": "Medical",
      "speed_score": 85,
      "quality_score": 92,
      "current_load": "Medium"
    },
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

#### Create New Project
```http
POST /api/projects
```

**Request Body:**
```json
{
  "client_name": "New Client Inc.",
  "project_name": "Technical Manual Translation",
  "language_pair": "English-German",
  "content_type": "Technical Manuals",
  "due_date": "2024-03-15",
  "initial_word_count": 25000,
  "source_document": "base64_encoded_file_content"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 156,
    "client_name": "New Client Inc.",
    "project_name": "Technical Manual Translation",
    "language_pair": "English-German",
    "content_type": "Technical Manuals",
    "start_date": "2024-01-20",
    "due_date": "2024-03-15",
    "initial_word_count": 25000,
    "translated_words": 0,
    "status": "Pending Assignment",
    "gpo_risk_status": "Low Risk",
    "gpo_risk_reason": "Project is proceeding as expected",
    "gpo_recommendation": "Continue monitoring",
    "created_at": "2024-01-20T14:30:00Z"
  }
}
```

#### Update Project
```http
PUT /api/projects/{project_id}
```

**Request Body:**
```json
{
  "translated_words": 12000,
  "status": "In Progress"
}
```

#### Delete Project
```http
DELETE /api/projects/{project_id}
```

### AI Analysis

#### Run GPO Analysis
```http
POST /api/projects/{project_id}/analyze
```

**Response:**
```json
{
  "success": true,
  "data": {
    "gpo_risk_status": "High Risk",
    "gpo_risk_reason": "Complex technical content assigned to linguist without technical specialty",
    "gpo_recommendation": "Re-assign to technical specialist or provide specialized training",
    "analysis_timestamp": "2024-01-20T15:45:00Z"
  }
}
```

#### Get Document Analysis
```http
GET /api/projects/{project_id}/document-analysis
```

**Response:**
```json
{
  "success": true,
  "data": {
    "complexity_score": "High",
    "complexity_reason": "Document contains technical terminology and complex sentence structures",
    "sensitive_data_flag": false,
    "sensitive_data_type": null,
    "terminology_flag": true,
    "terminology_details": ["API", "SDK", "integration", "deployment", "configuration"],
    "summary": "Technical manual for software integration with detailed API documentation"
  }
}
```

### Linguists

#### Get All Linguists
```http
GET /api/linguists
```

**Query Parameters:**
- `specialty` (optional): Filter by specialty
- `language_pair` (optional): Filter by language pair
- `availability` (optional): Filter by current load

#### Get Linguist by ID
```http
GET /api/linguists/{linguist_id}
```

#### Create Linguist
```http
POST /api/linguists
```

**Request Body:**
```json
{
  "name": "Dr. Anna Schmidt",
  "languages": "English-German",
  "specialties": "Medical, Technical",
  "speed_score": 88,
  "quality_score": 95,
  "current_load": "Low"
}
```

### Analytics

#### Get Risk Analytics
```http
GET /api/analytics/risks
```

**Query Parameters:**
- `period` (optional): Time period (week, month, quarter)
- `client` (optional): Filter by client

**Response:**
```json
{
  "success": true,
  "data": {
    "total_projects": 150,
    "risk_distribution": {
      "critical_risk": 5,
      "high_risk": 12,
      "medium_risk": 25,
      "low_risk": 45,
      "on_track": 63
    },
    "risk_trends": {
      "critical_risk_trend": "decreasing",
      "high_risk_trend": "stable",
      "medium_risk_trend": "increasing"
    },
    "top_risk_factors": [
      "Deadline pressure",
      "Complex content",
      "Resource constraints"
    ]
  }
}
```

#### Get Performance Metrics
```http
GET /api/analytics/performance
```

## 🔄 Webhooks

### Configure Webhook
```http
POST /api/webhooks
```

**Request Body:**
```json
{
  "url": "https://your-tms.com/webhooks/gpo",
  "events": ["project.created", "risk.updated", "analysis.completed"],
  "secret": "your_webhook_secret"
}
```

### Webhook Events

#### Project Created
```json
{
  "event": "project.created",
  "timestamp": "2024-01-20T14:30:00Z",
  "data": {
    "project_id": 156,
    "client_name": "New Client Inc.",
    "project_name": "Technical Manual Translation",
    "gpo_risk_status": "Low Risk"
  }
}
```

#### Risk Updated
```json
{
  "event": "risk.updated",
  "timestamp": "2024-01-20T15:45:00Z",
  "data": {
    "project_id": 156,
    "previous_risk": "Low Risk",
    "new_risk": "High Risk",
    "reason": "Complex technical content detected"
  }
}
```

## 📊 Rate Limiting

- **Standard Plan**: 1000 requests per hour
- **Professional Plan**: 10000 requests per hour
- **Enterprise Plan**: Custom limits

Rate limit headers:
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642683600
```

## 🚨 Error Handling

### Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid project data provided",
    "details": {
      "client_name": "Client name is required",
      "due_date": "Due date must be in the future"
    }
  }
}
```

### Common Error Codes
- `AUTHENTICATION_ERROR`: Invalid API key
- `AUTHORIZATION_ERROR`: Insufficient permissions
- `VALIDATION_ERROR`: Invalid request data
- `RESOURCE_NOT_FOUND`: Project or resource not found
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `INTERNAL_ERROR`: Server error

## 🔧 SDKs and Libraries

### Python SDK (Future)
```python
from gpo_sdk import GPOClient

client = GPOClient(api_key="your_api_key")

# Create project
project = client.projects.create({
    "client_name": "New Client",
    "project_name": "Translation Project",
    "language_pair": "English-Spanish"
})

# Run analysis
analysis = client.projects.analyze(project.id)
```

### JavaScript SDK (Future)
```javascript
const GPOClient = require('gpo-sdk');

const client = new GPOClient('your_api_key');

// Create project
const project = await client.projects.create({
    client_name: 'New Client',
    project_name: 'Translation Project',
    language_pair: 'English-Spanish'
});

// Run analysis
const analysis = await client.projects.analyze(project.id);
```

## 📈 Future Enhancements

### Planned Endpoints
- **Batch Operations**: Create/update multiple projects
- **Advanced Filtering**: Complex query filters
- **Real-time Updates**: WebSocket connections
- **Custom Analytics**: User-defined metrics
- **Integration Templates**: Pre-built TMS integrations

### Integration Examples
- **memoQ Integration**: Direct project synchronization
- **SDL Trados Integration**: Workflow automation
- **XTM Integration**: Real-time risk monitoring
- **Lokalise Integration**: Localization workflow

---

**Note**: This API documentation represents the conceptual structure for future implementation. The current GPO application focuses on the web interface and core AI functionality. API endpoints will be implemented based on customer requirements and integration needs. 