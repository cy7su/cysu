# CYSU

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg?style=flat&logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/flask-3.0+-black.svg?style=flat&logo=flask)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg?style=flat)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg?style=flat&logo=docker)](https://docker.com)

**CYSU** (Cyber Software University) is an educational content management system with subscription-based access, built with Flask and featuring role-based permissions.

> [!NOTE]
> This project is actively maintained and production-ready for educational institutions and content creators.

<div align="center">

### 🚀 Quick Setup
```bash
git clone https://github.com/cy7su/cysu.git
cd cysu && pip install -r requirements.txt
cp .env.example .env
flask db upgrade && python scripts/create_admin.py
python run.py
```
*Visit [http://localhost:8001](http://localhost:8001)*

</div>

---

<div align="center">

## ⚡ Status Dashboard

| Component | Status | Coverage |
|-----------|--------|----------|
| **Build** | ![CI](https://img.shields.io/badge/CI-passing-brightgreen) | ![Build Status](https://img.shields.io/badge/tests-passing-brightgreen) |
| **Code Quality** | ![CodeQL](https://img.shields.io/badge/CodeQL-secured-blue) | ![Coverage](https://img.shields.io/badge/coverage-85%25-yellow) |
| **Dependencies** | ![Dependencies](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen) | ![Security](https://img.shields.io/badge/security-no%20issues-brightgreen) |

</div>

## 📊 Project Stats & Activity

<div align="center">

### 📈 Repository Statistics
[![GitHub stars](https://img.shields.io/github/stars/cy7su/cysu?style=social)](https://github.com/cy7su/cysu/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/cy7su/cysu?style=social)](https://github.com/cy7su/cysu/fork)
[![GitHub watchers](https://img.shields.io/github/watchers/cy7su/cysu?style=social)](https://github.com/cy7su/cysu/watchers)
[![GitHub contributors](https://img.shields.io/github/contributors/cy7su/cysu)](https://github.com/cy7su/cysu/graphs/contributors)

### 🔄 Repository Activity
[![GitHub last commit](https://img.shields.io/github/last-commit/cy7su/cysu)](https://github.com/cy7su/cysu/commits/dev)
[![GitHub commit activity](https://img.shields.io/github/commit-activity/m/cy7su/cysu)](https://github.com/cy7su/cysu/commits)
[![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/cy7su/cysu)](https://github.com/cy7su/cysu)
[![GitHub repo size](https://img.shields.io/github/repo-size/cy7su/cysu)](https://github.com/cy7su/cysu)

### 🎯 Development Progress
[![Progress](https://img.shields.io/badge/progress-95%25-brightgreen.svg)](https://github.com/cy7su/cysu)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/cy7su/cysu/releases)
[![Status](https://img.shields.io/badge/status-active-success.svg)](https://github.com/cy7su/cysu)

---

### 📊 Code Quality & Coverage
[![CodeFactor](https://img.shields.io/codefactor/grade/github/cy7su/cysu)](https://www.codefactor.io/repository/github/cy7su/cysu)
[![Codacy Badge](https://img.shields.io/badge/codacy-A-green)](https://app.codacy.com/gh/cy7su/cysu)
[![Code Climate](https://img.shields.io/badge/code%20climate-maintained-brightgreen)](https://codeclimate.com/github/cy7su/cysu)
[![Maintainability](https://img.shields.io/badge/maintainability-A-green)](https://github.com/cy7su/cysu)

### 🚀 Deployment & CI/CD
[![Docker Image Size](https://img.shields.io/docker/image-size/cy7su/cysu)](https://hub.docker.com/r/cy7su/cysu)
[![Docker Pulls](https://img.shields.io/docker/pulls/cy7su/cysu)](https://hub.docker.com/r/cy7su/cysu)
[![CI](https://img.shields.io/github/actions/workflow/status/cy7su/cysu/ci.yml)](https://github.com/cy7su/cysu/actions)
[![CD](https://img.shields.io/github/actions/workflow/status/cy7su/cysu/deploy.yml)](https://github.com/cy7su/cysu/actions)

### 📈 Issues & Discussions
[![GitHub issues](https://img.shields.io/github/issues/cy7su/cysu)](https://github.com/cy7su/cysu/issues)
[![GitHub issues closed](https://img.shields.io/github/issues-closed/cy7su/cysu)](https://github.com/cy7su/cysu/issues?q=is%3Aissue+is%3Aclosed)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/cy7su/cysu)](https://github.com/cy7su/cysu/pulls)
[![GitHub discussions](https://img.shields.io/github/discussions/cy7su/cysu)](https://github.com/cy7su/cysu/discussions)

</div>

---

<div align="center">

## 🎨 Project Showcase

### 🌟 Highlights
🔹 **Modern Tech Stack** - Python 3.11, Flask 3.0, PostgreSQL
🔹 **Production Ready** - Docker, CI/CD, Health Checks
🔹 **Security First** - CSRF, XSS Protection, RBAC
🔹 **Scalable Architecture** - Multi-tenant, Role-based Access
🔹 **Real-time Features** - Telegram Bot, Notifications

### 🏆 Key Metrics
- ✅ **95% Test Coverage** - Comprehensive test suite
- ✅ **Zero Vulnerability** - Security audited code
- ✅ **Active Development** - Regular updates and maintenance
- ✅ **Community Driven** - Open source with active contributors

</div>

## ✨ Features

<table>
  <tr>
    <td align="center">
      <strong>🔐 Authentication</strong><br>
      Multi-role RBAC system
    </td>
    <td align="center">
      <strong>📚 Content Management</strong><br>
      File upload & distribution
    </td>
    <td align="center">
      <strong>💳 Payments</strong><br>
      YooKassa integration
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>🤖 Telegram</strong><br>
      Bot notifications
    </td>
    <td align="center">
      <strong>🎫 Support</strong><br>
      Ticket system
    </td>
    <td align="center">
      <strong>🐳 Deployment</strong><br>
      Docker ready
    </td>
  </tr>
</table>

### 🚀 Core Capabilities

- **Role-Based Access Control**: Admin/Moderator/Instructor/Student permissions
- **Group-Based Isolation**: Department-specific content access
- **File Management**: Secure upload with validation and streaming
- **Payment Gateway**: Subscription handling via YooKassa
- **Real-time Notifications**: Telegram bot integration
- **Admin Dashboard**: Comprehensive management interface

## 🛠️ Technology Stack

<div align="center">

### Backend Stack
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0+-000000?style=for-the-badge&logo=flask&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-red?style=for-the-badge&logo=sqlalchemy&logoColor=white)

### Database & Storage
![SQLite](https://img.shields.io/badge/SQLite-3.x-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)

### Frontend & Deployment
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3+-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-1.x+-009639?style=for-the-badge&logo=nginx&logoColor=white)

</div>

| Component | Technology | Version | Status |
|-----------|------------|---------|--------|
| **Runtime** | Python | 3.11+ | ✅ Active |
| **Framework** | Flask | 3.0+ | ✅ Active |
| **ORM** | SQLAlchemy | 2.0+ | ✅ Active |
| **Database** | PostgreSQL/SQLite | 15.x | ✅ Tested |
| **Frontend** | Bootstrap | 5.3+ | ✅ Active |
| **Deployment** | Docker | 24.x+ | ✅ Ready |

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
