# CYSU

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/flask-3.0+-black.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![.github/workflows/build.yml](https://github.com/cy7su/cysu/actions/workflows/build.yml/badge.svg)](https://github.com/cy7su/cysu/actions/workflows/build.yml)

Educational content management system with subscription-based access.

## Features

- Role-based access control (Admin/Moderator/Instructor/Student)
- Group-based content isolation
- File upload and distribution
- Subscription management with YooKassa payments
- Ticket support system
- Telegram bot integration

## Tech Stack

- Backend: Python 3.11, Flask 3.0, SQLAlchemy 2.0
- Database: SQLite (development), PostgreSQL (production)
- Frontend: Jinja2, Bootstrap 5, JavaScript
- Deployment: Docker, Gunicorn, Nginx

## Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose (recommended)
- Git

### Local Development

```bash
git clone https://github.com/cy7su/cysu.git
cd cysu

# Setup virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Initialize database
flask db upgrade

# Create admin user
python scripts/create_admin.py

# Start application
python run.py
```

Visit `http://localhost:8001`

### Docker Production

```bash
# Build and run
docker build -f deployment/Dockerfile -t cysu .
docker run -d -p 8001:8001 --env-file .env cysu

# Or use docker-compose
docker-compose up -d
```

## Configuration

Key environment variables (see `.env.example`):

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///app.db
MAIL_SERVER=smtp.gmail.com
MAIL_USERNAME=user@gmail.com
MAIL_PASSWORD=your-app-password
YOOKASSA_SHOP_ID=your-shop-id
YOOKASSA_SECRET_KEY=your-secret-key
UPLOAD_FOLDER=app/static/uploads
```

## Project Structure

```
cysu/
├── app/                    # Main application
│   ├── __init__.py        # Flask app factory
│   ├── models.py          # SQLAlchemy models
│   ├── forms.py           # WTForms
│   ├── views/             # Route handlers
│   ├── services/          # Business logic
│   ├── templates/         # Jinja2 templates
│   └── utils/             # Helper functions
├── deployment/            # Docker configs
├── docs/                  # Documentation
├── scripts/               # Utility scripts
└── run.py                # Application entry point
```

## API

### Authentication
- `POST /login` - User login
- `POST /register` - User registration
- `GET /logout` - User logout

### Content Management
- `GET /` - Homepage with subjects
- `GET /subject/<id>` - Subject details
- `GET /material/<id>` - Material details
- `POST /material/<id>/submit_solution` - Submit assignment

### File Operations
- `GET /files/<subject_id>/<filename>` - Download files
- `POST /material/<id>/add_solution` - Upload solution files

### Administrative
- `POST /subject/<id>/edit` - Edit subject
- `POST /material/<id>/edit` - Edit material
- `POST /toggle-admin-mode` - Switch admin interface

### JSON API
- `GET /api/notifications` - User notifications
- `POST /api/subject/<id>/pattern` - Update subject patterns

## Security Features

- CSRF protection on forms
- Secure session management
- File upload validation
- SQL injection prevention via SQLAlchemy
- XSS protection in templates
- Role-based access control

## Development

### Code Quality
```bash
# Run tests
pytest

# Code formatting
ruff format .

# Type checking
mypy app/
```

### Database Migrations
```bash
# Create migration
flask db migrate -m "Add new table"

# Apply migrations
flask db upgrade

# Rollback
flask db downgrade
```

## License

MIT License
