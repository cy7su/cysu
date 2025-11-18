# CYSU

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0+-000000?style=flat&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat&logo=docker&logoColor=white)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Educational content management system for online courses and digital materials. Supports role-based access control, subscription monetization, and automated content distribution.

Designed for educational institutions, training companies, and content creators who need secure, scalable platform for managing digital learning resources.

## Key Features

- **🔐 Access Control**: Multi-level roles (Admin/Moderator/Instructor/Student) with granular permissions
- **🏢 Group Management**: Isolated content for different departments or client groups
- **📁 File Handling**: Secure upload, storage, and distribution of course materials
- **💳 Monetization**: Integrated payment processing with YooKassa for subscription management
- **🎫 Support System**: Built-in ticket system for user support and issue tracking
- **🤖 Bot Integration**: Telegram bot for notifications and user management
- **📊 Administrative Panel**: Comprehensive dashboard for content and user management

## Architecture

```
Flask Application
├── API Layer (REST endpoints)
├── Service Layer (business logic)
├── Data Layer (SQLAlchemy ORM)
├── Template Engine (Jinja2)
└── Asset Pipeline (Bootstrap + JavaScript)
```

## Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend** | Python 3.11, Flask 3.0 | Web framework and runtime |
| **Database** | PostgreSQL/SQLite | Data persistence |
| **ORM** | SQLAlchemy 2.0 | Data modeling and queries |
| **Frontend** | Jinja2, Bootstrap 5 | Templates and styling |
| **Authentication** | Flask-Login, Werkzeug | Session management |
| **Payments** | YooKassa API | Payment processing |
| **Deployment** | Docker, Gunicorn, Nginx | Production infrastructure |

## Quick Start

### Local Development Setup

1. **Clone Repository**
   ```bash
   git clone https://github.com/cy7su/cysu.git
   cd cysu
   ```

2. **Setup Environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows

   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Configure Application**
   ```bash
   # Copy configuration template
   cp .env.example .env

   # Edit environment variables with your values
   nano .env
   ```

4. **Initialize Database**
   ```bash
   # Run database migrations
   flask db upgrade

   # Create administrator account
   python scripts/create_admin.py
   ```

5. **Start Development Server**
   ```bash
   python run.py
   ```

   Application will be available at `http://localhost:8001`

### Production Deployment

Using Docker for production deployment:

```bash
# Build optimized image
docker build -f deployment/Dockerfile -t cysu .

# Run with environment file
docker run -d \
  --name cysu-production \
  -p 8001:8001 \
  --env-file .env \
  --restart unless-stopped \
  cysu
```

## Configuration

### Essential Environment Variables

```env
# Application Security
SECRET_KEY=your-secure-random-key-here
FLASK_ENV=production

# Database
DATABASE_URL=postgresql://user:password@localhost/cysu
# Or for development: DATABASE_URL=sqlite:///app.db

# Email Service
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Payment Processing
YOOKASSA_SHOP_ID=your-shop-id
YOOKASSA_SECRET_KEY=your-secret-key
YOOKASSA_TEST_MODE=False

# File Storage
UPLOAD_FOLDER=app/static/uploads
MAX_CONTENT_LENGTH=209715200
```

### Advanced Configuration

For production deployments, consider these additional settings:

- **Database Connection Pooling**: Configure connection limits for high traffic
- **Session Storage**: Use Redis for session persistence across multiple instances
- **File Storage**: Configure cloud storage (S3, Azure Blob) for scalability
- **Caching**: Implement Redis caching for improved performance
- **Logging**: Setup structured logging with JSON format for monitoring

## Usage

### Basic Workflow

1. **Administrator Setup**: Create organization structure, user groups, and courses
2. **Content Upload**: Instructors upload materials and assign them to specific groups
3. **User Registration**: Students register and are assigned to appropriate groups
4. **Access Control**: Students can only view materials assigned to their groups
5. **Subscription Management**: Handle payments and subscription lifecycle

## API Documentation

CYSU provides comprehensive REST API for system integration and automation.

### Authentication

All API requests require authentication via session cookies or API tokens.

#### Session-Based Authentication
```bash
# Login to establish session
POST /login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=password&remember=true
```

### Core API Endpoints

#### Public Endpoints

##### GET /
**Description**: Retrieve homepage with accessible subjects and materials
**Authentication**: Optional
**Response**: HTML page with subjects list

##### GET /files/{subject_id}/{filename}
**Description**: Download file attachments
**Parameters**:
- `subject_id` (path): Subject identifier
- `filename` (path): File name
**Headers**:
- `Range`: For partial content requests (optional)
**Response**: File content with proper MIME type and headers

#### Authentication Endpoints

##### POST /login
**Description**: Authenticate user and establish session
**Request Body**:
```json
{
  "username": "string",
  "password": "string",
  "remember": true
}
```
**Response**: Redirect to profile or error message

##### POST /register
**Description**: Register new user account
**Request Body**: Form data with user details
**Response**: Account creation confirmation

##### GET /logout
**Description**: Terminate user session
**Response**: Redirect to homepage

#### Subject Management

##### GET /subject/{subject_id}
**Description**: View subject details and materials
**Authentication**: Required (subscription or access rights)
**Parameters**:
- `subject_id` (path): Subject identifier
**Response**: Subject page with lectures and assignments

##### POST /subject/{subject_id}/edit
**Description**: Update subject information
**Authentication**: Admin/Moderator required
**Request Body**: Form data with new title/description

##### POST /subject/{subject_id}/delete
**Description**: Remove subject and all associated materials
**Authentication**: Admin required
**Response**: Redirect with confirmation message

#### Material Management

##### GET /material/{material_id}
**Description**: View material details and download content
**Authentication**: Required (subscription/access rights)
**Parameters**:
- `material_id` (path): Material identifier
**Response**: Material page with file information

##### POST /material/{material_id}/edit
**Description**: Update material title and description
**Authentication**: Admin/Moderator required
**Request Body**: Form data with new content

##### POST /material/{material_id}/add_solution
**Description**: Upload reference solution file for assignments
**Authentication**: Admin/Moderator required
**Request Body**: Multipart form with solution file

##### POST /material/{material_id}/submit_solution
**Description**: Submit student assignment solution
**Authentication**: Student with active subscription
**Request Body**: Multipart form with solution file

##### POST /material/{material_id}/replace_file
**Description**: Replace material file with new version
**Authentication**: Admin/Moderator required
**Request Body**: Multipart form with new file

##### POST /material/{material_id}/delete
**Description**: Remove material and associated files
**Authentication**: Admin/Moderator required
**Response**: Redirect with confirmation

#### User Submissions

##### POST /submission/{submission_id}/delete
**Description**: Remove student's solution submission
**Authentication**: Student (own submission) or Admin
**Parameters**:
- `submission_id` (path): Submission identifier

##### GET /export-solutions
**Description**: Download archive of all user submissions
**Authentication**: Student (own solutions)
**Response**: ZIP file with organized submissions

#### Administrative Endpoints

##### POST /toggle-admin-mode
**Description**: Switch between user and admin interface modes
**Authentication**: Admin users only
**Response**: Mode toggle confirmation

##### GET /profile
**Description**: View user profile and subscription status
**Authentication**: Required
**Response**: Profile page with account information

### API Endpoints

#### Notifications

##### GET /api/notifications
**Description**: Retrieve unread notifications for current user
**Authentication**: Required
**Response**:
```json
{
  "success": true,
  "notifications": [
    {
      "id": 1,
      "title": "Material Updated",
      "message": "New assignment posted",
      "type": "info",
      "link": "/material/123",
      "created_at": "15.01.2024 10:30"
    }
  ]
}
```

##### POST /api/notifications/{notification_id}/read
**Description**: Mark notification as read
**Authentication**: Required
**Parameters**:
- `notification_id` (path): Notification identifier
**Response**:
```json
{
  "success": true
}
```

#### Subject Patterns

##### POST /api/subject/{subject_id}/pattern
**Description**: Update subject visual pattern (admin only)
**Authentication**: Admin required
**Headers**:
- `X-CSRFToken`: CSRF protection token
**Request Body**:
```json
{
  "pattern_svg": "<svg>...</svg>",
  "pattern_type": "custom"
}
```
**Response**:
```json
{
  "success": true
}
```

### File Operations

#### Public File Access

##### GET /files/{subject_id}/{filename}
**Description**: Download subject-related files
**Authentication**: Based on subject access rules
**Features**:
- Range request support for large files
- Content-type detection by extension
- Secure filename validation

**Supported Formats**:
- Documents: PDF, DOC, DOCX, TXT
- Images: JPG, JPEG, PNG
- Archives: ZIP
- Other: application/octet-stream

#### User Submissions

##### GET /files/{subject_id}/users/{user_id}/{filename}
**Description**: Download student solution files
**Authentication**: Admin/Moderator or assignment owner
**Security**: Path validation prevents directory traversal

### Share Links

##### GET /s/{code}
**Description**: Access materials via shortened share links
**Authentication**: None (public access for shared solutions)
**Features**:
- Click tracking
- Expiration support
- Access rules enforcement
**Response**: File download or access denied

### Payment Integration

#### Subscription Management

##### GET /payment/subscription
**Description**: Subscription selection and payment page
**Authentication**: Required
**Response**: Payment form with available plans

#### Webhook Processing

**Endpoint**: Webhook URL configured in YooKassa
**Format**: JSON payload from payment processor
**Processing**: Automatic subscription activation/deactivation

### Error Handling

All API endpoints return standardized error responses:

#### HTTP Status Codes
- `200`: Success
- `400`: Bad Request (validation errors)
- `401`: Unauthorized (login required)
- `403`: Forbidden (insufficient permissions)
- `404`: Not Found
- `405`: Method Not Allowed
- `413`: Payload Too Large
- `429`: Too Many Requests
- `500`: Internal Server Error

#### Error Response Format
```json
{
  "success": false,
  "error": "Readable error message",
  "details": "Additional technical information" // optional
}
```

### Rate Limiting

API requests are rate limited to prevent abuse:

- **Unauthenticated**: 100 requests/hour
- **Authenticated users**: 1000 requests/hour
- **Admin users**: No limit

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1634567890
```

### Security Features

- **CSRF Protection**: Required for state-changing operations
- **XSS Prevention**: Input sanitization and safe template rendering
- **Secure Headers**: CSP, HSTS, X-Frame-Options
- **File Validation**: Extension and content scanning
- **Session Security**: Secure cookie settings and timeout
- **Input Validation**: Type checking and sanitization

### API Versioning

Current API version: v1

All endpoints are prefixed with their version when needed for future compatibility.

### SDK and Libraries

Official client libraries are available for:
- **Python**: `pip install cysu-api-client`
- **JavaScript**: `npm install cysu-api-client`

### Postman Collection

Download the complete API collection: [CYSU-API.postman_collection.json](docs/api/CYSU-API.postman_collection.json)

### Testing

Run API tests with included test suite:

```bash
# Run all API tests
pytest tests/api/

# Test specific endpoint
pytest tests/api/test_subjects.py -v

# Integration tests
pytest tests/integration/test_file_uploads.py
