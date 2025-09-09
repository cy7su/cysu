# 🚀 cysu - Educational Platform

<div align="center">

<img src="https://img.shields.io/badge/Status-%20Active-B595FF?style=for-the-badge&logo=rocket" alt="Status">
<img src="https://img.shields.io/badge/Platform-Web%20App-B595FF?style=for-the-badge&logo=globe" alt="Platform">

</div>

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11+-B595FF?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-9A7FE6?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-B595FF?style=for-the-badge&logo=github&logoColor=white)](https://github.com/cy7su/cysu/actions)
[![License](https://img.shields.io/badge/License-MIT-9A7FE6?style=for-the-badge&logo=opensourceinitiative&logoColor=white)](LICENSE)

</div>

---


<div align="center">

<img src="https://img.shields.io/badge/Speed-%20Lightning%20Fast-B595FF?style=for-the-badge&logo=lightning" alt="Speed">

</div>

<div align="center">

```bash
git clone https://github.com/cy7su/cysu.git
cd cysu && pip install -r requirements.txt
python run.py
```

</div>

---


<div align="center">

<img src="https://img.shields.io/badge/Docker-%20Production%20Ready-9A7FE6?style=for-the-badge&logo=docker" alt="Docker">

</div>

<div align="center">

```bash
docker run -d -p 8001:8001 \
  -e SECRET_KEY=your-key \
  cy7su/cysu:latest
```

</div>

---



<div align="center">

<img src="https://img.shields.io/badge/Config-%20Environment%20Setup-9A7FE6?style=for-the-badge&logo=settings" alt="Config">

</div>


<div align="center">

```bash
cp .env.example .env
# Edit .env with your settings
```

</div>

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


<div align="center">

<img src="https://img.shields.io/badge/Launch-%20Start%20Server-B595FF?style=for-the-badge&logo=play" alt="Launch">

</div>

<div align="center">

```bash
python run.py
# 🌐 Available at: http://localhost:8001
```

</div>


<div align="center">

<img src="https://img.shields.io/badge/Credentials-%20Default%20Login-9A7FE6?style=for-the-badge&logo=user" alt="Credentials">

</div>

<div align="center">

| Role | Username | Password | Email |
|------|----------|----------|-------|
| **Admin** | `admin` | `admin123` | `admin@cysu.ru` |


<div align="center">

![GitHub stars](https://img.shields.io/github/stars/cy7su/cysu?style=social)
![GitHub forks](https://img.shields.io/github/forks/cy7su/cysu?style=social)
![GitHub issues](https://img.shields.io/github/issues/cy7su/cysu)
![GitHub pull requests](https://img.shields.io/github/issues-pr/cy7su/cysu)
![GitHub last commit](https://img.shields.io/github/last-commit/cy7su/cysu)

</div>

---

<div align="center">


<div align="center">

[![GitHub](https://img.shields.io/badge/GitHub-cy7su%2Fcysu-B595FF?style=for-the-badge&logo=github)](https://github.com/cy7su/cysu)
[![Website](https://img.shields.io/badge/Website-cysu.ru-9A7FE6?style=for-the-badge&logo=firefox)](https://cysu.ru)
[![Email](https://img.shields.io/badge/Email-contact%40cysu.ru-B595FF?style=for-the-badge&logo=mail.ru)](mailto:support@cysu.ru)

<div align="center">

<img src="https://img.shields.io/badge/License-%20MIT%20License-9A7FE6?style=for-the-badge&logo=opensourceinitiative" alt="License">

</div>

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Made with ❤️ by cysu**

</div>
