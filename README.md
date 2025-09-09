# 🚀 cysu - Next-Gen Educational Platform

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?style=for-the-badge&logo=github&logoColor=white)](https://github.com/cy7su/cysu/actions)
[![Security](https://img.shields.io/badge/Security-Scanned-00D4AA?style=for-the-badge&logo=security&logoColor=white)](#security)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge&logo=opensourceinitiative&logoColor=white)](LICENSE)

**🔥 The most advanced educational platform with enterprise-grade security, automated CI/CD, and cutting-edge technology stack!**

[![Deploy](https://img.shields.io/badge/Deploy-Now-FF6B6B?style=for-the-badge&logo=rocket&logoColor=white)](#quick-start)
[![Demo](https://img.shields.io/badge/Live%20Demo-4ECDC4?style=for-the-badge&logo=play&logoColor=white)](https://cysu.ru)
[![Documentation](https://img.shields.io/badge/Docs-Read-9B59B6?style=for-the-badge&logo=book&logoColor=white)](#documentation)

</div>

---

## ✨ Why cysu is INSANE

### 🛡️ **Enterprise Security**
- **12+ Security Tools** - Bandit, Safety, Semgrep, pip-audit
- **Docker Security** - Hadolint scanning
- **Dependency Auditing** - Real-time vulnerability detection
- **CSRF Protection** - Flask-WTF integration
- **Secure Authentication** - Flask-Login with session management

### 🚀 **DevOps Excellence**
- **Automated CI/CD** - GitHub Actions with 12+ quality checks
- **Docker Ready** - Production-optimized containers
- **Auto Releases** - Version management with semantic versioning
- **Package Publishing** - GitHub Packages integration
- **Quality Gates** - Black, isort, mypy, radon, flake8

### 💎 **Modern Tech Stack**
- **Python 3.11+** - Latest language features
- **Flask 3.0** - Modern web framework
- **SQLAlchemy 2.0** - Advanced ORM
- **Bootstrap 5.3** - Responsive design
- **Material Design** - Beautiful UI/UX

### 🎯 **Production Ready**
- **Scalable Architecture** - Microservices ready
- **Database Migrations** - Flask-Migrate
- **Email Integration** - Flask-Mail
- **Payment Gateway** - YooKassa integration
- **Telegram Bot** - python-telegram-bot

## 🚀 Quick Start

### ⚡ **One-Command Deploy**
```bash
# Clone and run in 30 seconds!
git clone https://github.com/cy7su/cysu.git && cd cysu
pip install -r requirements.txt && python run.py
```

### 🐳 **Docker Deploy (Recommended)**
```bash
# Production-ready in seconds!
docker run -d -p 8001:8001 \
  -e SECRET_KEY=your-secret-key \
  -e DATABASE_URL=sqlite:///app.db \
  cy7su/cysu:latest
```

### 🔧 **Development Setup**
```bash
# Full development environment
git clone https://github.com/cy7su/cysu.git
cd cysu
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your settings
python run.py
```

## ⚙️ Configuration

### 🔐 **Environment Variables**
```bash
cp .env.example .env
# Edit .env with your settings
```

<details>
<summary>📋 <strong>Click to see all configuration options</strong></summary>

```env
# 🚀 CORE SETTINGS
SECRET_KEY=your-super-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=True

# 🗄️ DATABASE
DATABASE_URL=sqlite:///app.db
# For PostgreSQL: DATABASE_URL=postgresql://user:pass@localhost/cysu

# 📧 EMAIL CONFIGURATION
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# 💳 PAYMENT GATEWAY (YooKassa)
YOOKASSA_SHOP_ID=your-shop-id
YOOKASSA_SECRET_KEY=your-secret-key
YOOKASSA_TEST_MODE=True

# 💰 SUBSCRIPTION PRICING (RUB)
SUBSCRIPTION_PRICE_1=89.00
SUBSCRIPTION_PRICE_3=199.00
SUBSCRIPTION_PRICE_6=349.00
SUBSCRIPTION_PRICE_12=469.00

# 📁 FILE UPLOADS
UPLOAD_FOLDER=app/static/uploads
TICKET_FILES_FOLDER=app/static/ticket_files
MAX_CONTENT_LENGTH=209715200  # 200MB

# 📝 LOGGING
LOG_FILE=logs/app.log
LOG_LEVEL=INFO
```

</details>

### 🗄️ **Database Setup**
```bash
# Initialize database
mkdir -p logs
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 🚀 **Launch**
```bash
python run.py
# 🌐 Available at: http://localhost:8001
```

## 👤 Default Credentials

| Role | Username | Password | Email |
|------|----------|----------|-------|
| **Admin** | `admin` | `admin123` | `admin@cysu.ru` |

⚠️ **Security**: Change admin password after first login!

## 🛡️ Security Features

### 🔒 **Automated Security Scanning**
Our CI/CD pipeline includes **12+ security tools**:

| Tool | Purpose | Status |
|------|---------|--------|
| **Bandit** | Python security issues | ✅ Active |
| **Safety** | Dependency vulnerabilities | ✅ Active |
| **Semgrep** | Security patterns | ✅ Active |
| **pip-audit** | Package auditing | ✅ Active |
| **Hadolint** | Docker security | ✅ Active |

### 🚀 **Quality Assurance**
| Tool | Purpose | Status |
|------|---------|--------|
| **Black** | Code formatting | ✅ Active |
| **isort** | Import sorting | ✅ Active |
| **mypy** | Type checking | ✅ Active |
| **radon** | Complexity metrics | ✅ Active |
| **flake8** | Code quality | ✅ Active |
| **pip-check** | Dependency conflicts | ✅ Active |


## 🛠️ Technology Stack

### 🐍 **Backend (Python)**
| Technology | Version | Purpose |
|------------|---------|---------|
| **Flask** | 3.0.0 | Modern web framework |
| **SQLAlchemy** | 2.0.23 | Advanced ORM |
| **Flask-Migrate** | 4.0.5 | Database migrations |
| **Flask-Login** | 0.6.3 | Authentication |
| **Flask-WTF** | 1.2.1 | Forms & CSRF protection |
| **Flask-Mail** | 0.9.1 | Email integration |
| **Werkzeug** | 3.0.1 | WSGI utilities |

### 🎨 **Frontend**
| Technology | Version | Purpose |
|------------|---------|---------|
| **Bootstrap** | 5.3.2 | CSS framework |
| **Font Awesome** | 6.0.0 | Icons |
| **Vanilla JS** | ES6+ | Client logic |
| **SVG Patterns** | Dynamic | Backgrounds |
| **Material Design** | Latest | Design system |
| **Responsive** | Mobile-first | Adaptive design |

### 🗄️ **Database**
- **SQLite** (default) - Development
- **PostgreSQL** (production) - Scalable
- **Flask-Migrate** - Schema management

### 🐳 **DevOps & Deployment**
| Technology | Purpose |
|------------|---------|
| **Docker** | Containerization |
| **GitHub Actions** | CI/CD Pipeline |
| **GitHub Packages** | Package registry |
| **Semantic Versioning** | Release management |

## 🔧 Development

### 🚀 **Development Mode**
```bash
export FLASK_ENV=development
export FLASK_DEBUG=True
python run.py
```

### 🗄️ **Database Migrations**
```bash
# Create migration
flask db migrate -m "Description of changes"

# Apply migration
flask db upgrade

# Rollback migration
flask db downgrade
```

### 🧪 **Running Tests**
```bash
# Run all quality checks
flake8 app/ run.py
black --check app/ run.py
isort --check-only app/ run.py
mypy app/ run.py
bandit -r app/ run.py
```

### 🐳 **Docker Development**
```bash
# Build image
docker build -t cysu .

# Run container
docker run -p 8001:8001 cysu

# Run with environment
docker run -p 8001:8001 -e SECRET_KEY=dev-key cysu
```

## 📊 Project Stats

<div align="center">

![GitHub stars](https://img.shields.io/github/stars/cy7su/cysu?style=social)
![GitHub forks](https://img.shields.io/github/forks/cy7su/cysu?style=social)
![GitHub issues](https://img.shields.io/github/issues/cy7su/cysu)
![GitHub pull requests](https://img.shields.io/github/issues-pr/cy7su/cysu)
![GitHub last commit](https://img.shields.io/github/last-commit/cy7su/cysu)

</div>

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### 🎯 **Quick Contribution**
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Flask Team** - For the amazing web framework
- **Bootstrap Team** - For the responsive CSS framework
- **Font Awesome** - For the beautiful icons
- **All Contributors** - For making this project better

---

<div align="center">

**⭐ Star this repo if you found it helpful!**

[![GitHub](https://img.shields.io/badge/GitHub-cy7su%2Fcysu-181717?style=for-the-badge&logo=github)](https://github.com/cy7su/cysu)
[![Website](https://img.shields.io/badge/Website-cysu.ru-FF6B6B?style=for-the-badge&logo=firefox)](https://cysu.ru)
[![Email](https://img.shields.io/badge/Email-contact%40cysu.ru-4ECDC4?style=for-the-badge&logo=mail.ru)](mailto:contact@cysu.ru)

**Made with ❤️ by the cysu team**

</div>
