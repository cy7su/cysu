# CYSU

Educational content management system with subscription-based access.

## Features

- Role-based access control (Admin/Moderator/Instructor/Student)
- Group-based content isolation
- File upload and distribution
- Subscription management with YooKassa payments
- Ticket support system
- Telegram bot integration

## Tech Stack

- **Backend**: Python 3.11, Flask, SQLAlchemy
- **Frontend**: Jinja2, Bootstrap, JavaScript
- **Database**: SQLite/PostgreSQL
- **Deployment**: Docker, Gunicorn, Nginx

## Quick Start

### Local Development

```bash
git clone https://github.com/cy7su/cysu.git
cd cysu
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
flask db upgrade
python scripts/create_admin.py
python run.py
```

### Docker Production

```bash
docker build -f deployment/Dockerfile -t cysu .
docker run -d -p 8001:8001 --env-file .env cysu
```

## Configuration

Key environment variables:

```env
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///app.db
MAIL_SERVER=smtp.gmail.com
MAIL_USERNAME=your-email
MAIL_PASSWORD=app-password
YOOKASSA_SHOP_ID=shop-id
YOOKASSA_SECRET_KEY=secret-key
UPLOAD_FOLDER=app/static/uploads
```

## License

MIT License
