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

### API Documentation

REST API endpoints are available for integration:

- `GET /api/v1/subjects` - List accessible subjects
- `POST /api/v1/auth/login` - User authentication
- `GET /api/v1/materials/{id}` - Retrieve material details
- `POST /api/v1/materials/{id}/submit` - Submit assignment

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.

## Support

- **Documentation**: [docs/](docs/) directory
- **Issues**: [GitHub Issues](https://github.com/cy7su/cysu/issues)
- **Email**: support@project-domain.com
