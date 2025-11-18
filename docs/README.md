# cysu

## Overview

CYSU (Cyber Software University) is an enterprise-grade educational platform designed for managing digital learning materials, student subscriptions, and comprehensive administrative workflows. The platform supports multi-tenant organization through group-based access control, integrated payment processing, and automated file distribution systems.

## Table of Contents

- [Core Features](#core-features)
- [System Architecture](#system-architecture)
- [Technical Stack](#technical-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Security](#security)
- [Deployment](#deployment)
- [Monitoring](#monitoring)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)
- [Support](#support)

## Core Features

### User Management
- **Role-Based Access Control (RBAC)**: Administrators, Moderators, Instructors, Students
- **Group-Based Organization**: Hierarchical user groups with isolated content access
- **Authentication & Authorization**: Secure session management with Flask-Login

### Content Management
- **Document Repository**: Centralized storage for lectures and assignments
- **File Distribution**: Optimized serving with range request support
- **Content Access Control**: Granular permissions based on user roles and group membership

### Subscription System
- **Flexible Pricing Models**: Monthly, quarterly, semi-annual pricing tiers
- **Payment Integration**: YooKassa payment gateway with webhook processing
- **Access Management**: Automated entitlement based on subscription status

### Administrative Panel
- **Real-time Analytics**: User engagement and content utilization metrics
- **Bulk Operations**: Mass user management and content distribution
- **Audit Logging**: Comprehensive action tracking for compliance

### Support Infrastructure
- **Ticket System**: Integrated customer service with file attachments
- **Automated Workflows**: Escalation and notification procedures
- **Communication Channels**: Multi-channel user interaction

## System Architecture

### Application Layers

```
Presentation Layer (Flask/Jinja2/Bootstrap)
├── Service Layer (Business Logic)
│   ├── Data Access Layer (SQLAlchemy)
│   │   └── Persistence Layer (SQLite/PostgreSQL)
└── Infrastructure Services
    ├── Payment Gateway (YooKassa)
    ├── Email Service (SMTP)
    ├── File Storage (Local/Cloud)
    └── External APIs (Telegram Bot)
```

### Component Architecture

- **Web Layer**: Flask-based REST API with JSON responses and template rendering
- **Business Logic**: Modular service layer with separation of concerns
- **Data Layer**: ORM-based data models with migration support
- **Infrastructure**: External service integrations and system utilities

## Technical Stack

### Backend
- **Python 3.11+**: Core runtime environment
- **Flask 3.0**: Web application framework
- **SQLAlchemy 2.0**: Object-relational mapping
- **Flask-Migrate**: Database schema management
- **Flask-Login**: Session-based authentication
- **Flask-WTF**: Form validation and CSRF protection

### Database & Storage
- **SQLite**: Development and small-scale deployments
- **PostgreSQL**: Production database with advanced features
- **Local File System**: Document storage with optimization layer
- **Cloud Storage**: Ready for S3/Azure Blob Storage integration

### Frontend
- **Jinja2**: Template engine for dynamic content
- **Bootstrap 5**: CSS framework for responsive design
- **Vanilla JavaScript**: Browser-side interactivity
- **Custom UI Components**: Modular interface elements

### DevOps & Infrastructure
- **Docker**: Containerized deployment
- **Multi-stage Builds**: Optimized production images
- **GitHub Actions**: CI/CD pipeline
- **Health Checks**: Automated monitoring
- **Structured Logging**: JSON-formatted audit trails

## Installation

### Prerequisites
- Python 3.11 or higher
- Docker & Docker Compose (recommended for production)
- Git

### Local Installation

1. **Clone Repository**
   ```bash
   git clone https://github.com/cy7su/cysu.git
   cd cysu
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # venv\Scripts\activate   # Windows
   ```

3. **Install Dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize Database**
   ```bash
   flask db upgrade
   ```

6. **Create Administrator Account**
   ```bash
   python scripts/create_admin.py
   ```

7. **Start Application**
   ```bash
   python run.py
   ```

   Application will be available at `http://localhost:8001`

### Docker Installation

```bash
# Build image
docker build -f deployment/Dockerfile -t cysu .

# Run container
docker run -d -p 8001:8001 \
  --env-file .env \
  --name cysu-app \
  cysu
```

### Docker Compose (Production)

```yaml
version: '3.8'
services:
  cysu:
    build:
      context: .
      dockerfile: deployment/Dockerfile
    ports:
      - "8001:8001"
    environment:
      - FLASK_ENV=production
    env_file:
      - .env
    volumes:
      - uploads_data:/app/app/static/uploads
      - logs_data:/app/logs
    healthcheck:
      test: ["CMD", "python", "-c", "import app; app.create_app()"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

volumes:
  uploads_data:
  logs_data:
```

## Configuration

### Environment Variables

Create `.env` file based on `.env.example`:

```env
# Application Settings
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=True
SERVER_NAME=localhost:8001

# Database Configuration
DATABASE_URL=sqlite:///app.db
# DATABASE_URL=postgresql://user:password@host:5432/cysu

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=user@gmail.com
MAIL_PASSWORD=app-password
MAIL_DEFAULT_SENDER=user@gmail.com
MAIL_MAX_EMAILS=None
MAIL_ASCII_ATTACHMENTS=False

# Payment Gateway (YooKassa)
YOOKASSA_SHOP_ID=your-shop-id
YOOKASSA_SECRET_KEY=your-secret-key
YOOKASSA_TEST_MODE=True
YOOKASSA_RETURN_URL=https://cysu.ru/payment/success
YOOKASSA_CANCEL_URL=https://cysu.ru/payment/cancel

# Subscription Pricing (RUB)
SUBSCRIPTION_PRICE_1=89.00
SUBSCRIPTION_PRICE_3=199.00
SUBSCRIPTION_PRICE_6=349.00
SUBSCRIPTION_PRICE_12=469.00
SUBSCRIPTION_CURRENCY=RUB

# File Storage
UPLOAD_FOLDER=app/static/uploads
TICKET_FILES_FOLDER=app/static/ticket_files
MAX_CONTENT_LENGTH=209715200

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
LOG_FORMAT=json

# Telegram Integration
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_WEBHOOK_URL=https://cysu.ru/telegram/webhook
# Security
SESSION_COOKIE_SECURE=False
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
PERMANENT_SESSION_LIFETIME=86400

# Rate Limiting
RATE_LIMIT_DEFAULT="100/hour"
RATE_LIMIT_STORAGE_URL="memory://"
```

## API Reference

### Authentication Endpoints

#### POST /api/v1/auth/login
Authenticate user credentials and establish session.

**Request Body:**
```json
{
  "username": "string",
  "password": "string",
  "remember": true
}
```

**Response:**
```json
{
  "success": true,
  "user": {
    "id": 1,
    "username": "string",
    "email": "string",
    "role": "student|instructor|admin"
  }
}
```

#### POST /api/v1/auth/logout
Terminate user session.

#### GET /api/v1/auth/status
Retrieve current authentication status.

### Content Management

#### GET /api/v1/subjects
Retrieve list of accessible subjects.

**Query Parameters:**
- `group_id`: Filter by user group
- `limit`: Maximum number of results (default: 50)
- `offset`: Pagination offset

**Response:**
```json
{
  "subjects": [
    {
      "id": 1,
      "title": "Advanced Algorithms",
      "description": "Computer science fundamentals",
      "materials_count": 25,
      "created_at": "2024-01-15T10:00:00Z"
    }
  ],
  "total": 1
}
```

#### GET /api/v1/materials/{material_id}
Retrieve material details and content.

#### POST /api/v1/materials/{material_id}/submit
Submit assignment solution.

**Request Body (multipart/form-data):**
- `file`: Solution file
- `text`: Optional text submission

### Administrative Endpoints

#### GET /api/v1/admin/users
User management operations (admin only).

#### POST /api/v1/admin/subjects
Create new subject (admin only).

#### GET /api/v1/admin/analytics
System analytics and reporting.

## Security

### Authentication & Authorization

The platform implements comprehensive security measures:

- **JWT-based Authentication**: Secure token management for API access
- **Role-Based Access Control**: Hierarchical permission system
- **Session Management**: Secure cookie-based sessions with CSRF protection
- **Multi-factor Authentication**: Ready for 2FA implementation

### Data Protection

- **Encryption**: Sensitive data encrypted using AES-256
- **File Security**: All uploads scanned for malware
- **Secure Headers**: CSP, HSTS, X-Frame-Options properly configured
- **Rate Limiting**: DDoS protection with configurable thresholds

### Compliance

- **GDPR Compliance**: User data handling and consent management
- **Audit Trails**: Comprehensive logging of user actions
- **Data Minimization**: Only necessary data collected and retained
- **Right to Deletion**: User data removal capabilities

### Network Security

- **TLS Encryption**: All external communications encrypted
- **API Security**: Request signing and throttling
- **Input Validation**: Strict parameter validation and sanitization
- **SQL Injection Protection**: Prepared statements and ORM safeguards

## Deployment

### Production Architecture

```
Internet → Load Balancer → API Gateway → Application Servers
                                ↓
                        Database Cluster + File Storage
```

### Infrastructure Requirements

#### Minimum Specifications
- **CPU**: 2 cores (Intel/AMD x64)
- **Memory**: 4GB RAM
- **Storage**: 50GB SSD
- **Network**: 100Mbps bandwidth

#### Recommended Specifications
- **CPU**: 4+ cores
- **Memory**: 8GB+ RAM
- **Storage**: 200GB+ SSD with RAID
- **Network**: 1Gbps+ bandwidth

### Docker Deployment

```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d

# Scaling
docker-compose up -d --scale cysu=3
```

### Traditional Deployment

#### Gunicorn Configuration

```python
# gunicorn.conf.py
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2

bind = "0.0.0.0:8001"
pidfile = "/var/run/gunicorn.pid"
user = "cysu"
group = "cysu"
tmp_upload_dir = "/tmp"
```

#### Nginx Configuration

```nginx
upstream cysu_app {
    server localhost:8001;
    server localhost:8002;
    server localhost:8003;
}

server {
    listen 443 ssl http2;
    server_name cysu.ru;

    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/cysu.ru/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/cysu.ru/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self'" always;

    location / {
        proxy_pass http://cysu_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # File upload configuration
        client_max_body_size 200M;
    }

    location /static/ {
        alias /path/to/cysu/app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### Database Setup

#### PostgreSQL Production Configuration

```sql
-- Create database
CREATE DATABASE cysu_production ENCODING 'UTF8';

-- Create user with appropriate privileges
CREATE USER cysu_user WITH ENCRYPTED PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE cysu_production TO cysu_user;

-- Performance optimizations
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET max_wal_size = '1GB';
ALTER SYSTEM SET min_wal_size = '80MB';
```

## Monitoring

### Application Metrics

The platform exports comprehensive metrics for monitoring:

#### Performance Metrics
- **Response Times**: API endpoint latency distribution
- **Throughput**: Requests per second by endpoint
- **Error Rates**: 4xx and 5xx error percentages
- **Resource Usage**: CPU, memory, disk I/O

#### Business Metrics
- **User Engagement**: Active users, session duration
- **Content Metrics**: Materials accessed, submissions processed
- **Subscription KPIs**: Conversion rates, revenue tracking

### Logging & Alerting

#### Structured Logging

All application logs follow structured JSON format:

```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "level": "INFO",
  "logger": "cysu.api.subjects",
  "user_id": 123,
  "action": "subject_access",
  "subject_id": 456,
  "ip": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "duration_ms": 150,
  "status_code": 200
}
```

#### Alert Conditions
- **High Error Rate**: >5% 5xx errors in 5 minutes
- **Degraded Performance**: Response time >2 seconds for 10 minutes
- **Resource Exhaustion**: >90% CPU or memory usage sustained
- **Security Events**: Failed authentication attempts spike

### Health Checks

#### Application Health
```bash
# Health check endpoint
curl -f http://localhost:8001/health
```

#### Container Health
```bash
# Docker health check
docker ps --filter health=unhealthy

# Container logs
docker logs --since 1h cysu-app
```

## Development

### Development Environment Setup

```bash
# Clone and setup
git clone https://github.com/cy7su/cysu.git
cd cysu

# Create development environment
python -m venv venv-dev
source venv-dev/bin/activate

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Database setup
export FLASK_ENV=development
flask db upgrade

# Run development server
flask run --debug
```

### Code Quality

The project maintains high code quality standards:

#### Linting & Formatting
```bash
# Code formatting
ruff format .

# Import sorting
ruff check --select F401 --fix .

# Type checking
mypy app/ --ignore-missing-imports
```

#### Testing
```bash
# Unit tests
python -m pytest tests/unit/

# Integration tests
python -m pytest tests/integration/

# End-to-end tests
python -m pytest tests/e2e/

# Coverage report
coverage run --source=app -m pytest
coverage report
coverage html
```

### Git Workflow

#### Branch Naming Convention
```bash
# Feature branches
feature/user-management
feature/payment-integration

# Bug fixes
fix/login-validation
fix/file-upload-429

# Hot fixes
hotfix/security-patch
```

#### Commit Message Format
```
type(scope): description

[optional body]

[optional footer]
```

#### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Testing
- `chore`: Maintenance

## Contributing

### Contribution Guidelines

1. **Fork** the repository
2. Create a **feature branch** from `main`
3. Make changes following the established patterns
4. **Test thoroughly** - unit tests and integration tests required
5. **Update documentation** if necessary
6. Submit a **pull request** with clear description

### Code Review Process

All contributions undergo peer review:

1. **Automated Checks**: CI pipeline validation
2. **Peer Review**: At least one maintainer review required
3. **QA Validation**: Functional testing before merge
4. **Release Notes**: Feature additions documented

### Release Process

The project follows semantic versioning:

- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

Release process:
```bash
# Create release branch
git checkout -b release/v1.2.3

# Update version
echo "1.2.3" > VERSION

# Merge to main
git checkout main
git merge release/v1.2.3

# Create GitHub release
git tag -a v1.2.3 -m "Release v1.2.3"
git push origin main --tags
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Support

### Documentation
- [API Documentation](docs/api.md)
- [Deployment Guide](docs/deployment.md)
- [Troubleshooting](docs/troubleshooting.md)

### Community Support
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and community discussion
- **Documentation Wiki**: Community-maintained guides

### Professional Support
For enterprise support, commercial licensing, or consulting services:

- **Email**: enterprise@cysu.ru
- **Website**: [cysu.ru/enterprise](https://cysu.ru/enterprise)

### Security Issues
**Do not report security vulnerabilities through public GitHub issues.**

Please email security@cysu.ru with full details. We will respond within 48 hours and work with you to resolve the issue responsibly.
