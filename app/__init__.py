import logging
import os
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, url_for
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()


def create_app():
    app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    static_folder_path = os.path.join(app_root, "app", "static")

    app = Flask(
        __name__,
        instance_path=None,
        instance_relative_config=False,
        static_folder=static_folder_path,
        static_url_path="/static",
    )

    app.config["SECRET_KEY"] = os.getenv(
        "SECRET_KEY", "default-secret-key-change-in-production"
    )
    app.config["SERVER_NAME"] = os.getenv("SERVER_NAME", "cysu.ru")
    db_path = os.path.abspath(
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "app.db")
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"

    db_dir = os.path.dirname(db_path)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    possible_upload_paths = [
        os.path.join(app_root, "app", "static", "uploads"),
        "/root/cysu/app/static/uploads",
    ]

    upload_folder = None
    for path in possible_upload_paths:
        if os.path.exists(path):
            upload_folder = path
            break

    if not upload_folder:
        upload_folder = os.getenv(
            "UPLOAD_FOLDER", os.path.join(app_root, "app", "static", "uploads")
        )

    possible_ticket_paths = [
        os.path.join(app_root, "app", "static", "ticket_files"),
        "/root/cysu/app/static/ticket_files",
    ]

    ticket_folder = None
    for path in possible_ticket_paths:
        if os.path.exists(path):
            ticket_folder = path
            break

    if not ticket_folder:
        ticket_folder = os.getenv(
            "TICKET_FILES_FOLDER",
            os.path.join(app_root, "app", "static", "ticket_files"),
        )
    upload_folder = os.path.abspath(upload_folder)
    ticket_folder = os.path.abspath(ticket_folder)

    app.config["UPLOAD_FOLDER"] = upload_folder
    app.config["TICKET_FILES_FOLDER"] = ticket_folder

    app.logger.info(f"APP_ROOT: {app_root}")
    app.logger.info(f"STATIC_FOLDER: {static_folder_path}")
    app.logger.info(f"UPLOAD_FOLDER: {upload_folder}")
    app.logger.info(f"TICKET_FILES_FOLDER: {ticket_folder}")
    app.logger.info(f"UPLOAD_FOLDER exists: {os.path.exists(upload_folder)}")
    if os.path.exists(upload_folder):
        app.logger.info(f"UPLOAD_FOLDER contents: {os.listdir(upload_folder)}")
    # 500MB по умолчанию
    max_content_length = int(
        os.getenv("MAX_CONTENT_LENGTH", 500 * 1024 * 1024)
    )
    app.config["MAX_CONTENT_LENGTH"] = max_content_length
    app.logger.info(
        f"MAX_CONTENT_LENGTH установлен: {max_content_length} байт "
        f"({max_content_length / (1024*1024):.1f} MB)"
    )

    for folder in [app.config["UPLOAD_FOLDER"]]:
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)

    app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
    app.config["MAIL_USE_TLS"] = (
        os.getenv("MAIL_USE_TLS", "True").lower() == "true"
    )
    app.config["MAIL_USE_SSL"] = (
        os.getenv("MAIL_USE_SSL", "False").lower() == "true"
    )
    app.config["MAIL_USERNAME"] = os.getenv(
        "MAIL_USERNAME", "your-email@gmail.com"
    )
    app.config["MAIL_PASSWORD"] = os.getenv(
        "MAIL_PASSWORD", "your-app-password"
    )
    app.config["MAIL_DEFAULT_SENDER"] = os.getenv(
        "MAIL_DEFAULT_SENDER", "your-email@gmail.com"
    )
    app.config["MAIL_TIMEOUT"] = 10  # Таймаут 10 секунд
    app.config["MAIL_CONNECT_TIMEOUT"] = 5  # Таймаут подключения 5 секунд
    app.config["SKIP_EMAIL_VERIFICATION"] = (
        os.getenv("SKIP_EMAIL_VERIFICATION", "False").lower() == "true"
    )

    app.config["YOOKASSA_SHOP_ID"] = os.getenv(
        "YOOKASSA_SHOP_ID", "your-shop-id"
    )
    app.config["YOOKASSA_SECRET_KEY"] = os.getenv(
        "YOOKASSA_SECRET_KEY", "your-secret-key"
    )
    app.config["YOOKASSA_TEST_MODE"] = (
        os.getenv("YOOKASSA_TEST_MODE", "True").lower() == "true"
    )

    app.config["SUBSCRIPTION_PRICES"] = {
        "1": float(os.getenv("SUBSCRIPTION_PRICE_1", 89.00)),
        "3": float(os.getenv("SUBSCRIPTION_PRICE_3", 199.00)),
        "6": float(os.getenv("SUBSCRIPTION_PRICE_6", 349.00)),
        "12": float(os.getenv("SUBSCRIPTION_PRICE_12", 469.00)),
    }
    app.config["SUBSCRIPTION_CURRENCY"] = os.getenv(
        "SUBSCRIPTION_CURRENCY", "RUB"
    )

    app.config["LOG_FILE"] = os.getenv("LOG_FILE", "logs/app.log")
    app.config["LOG_LEVEL"] = os.getenv("LOG_LEVEL", "INFO")

    log_dir = os.path.dirname(app.config["LOG_FILE"])
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    file_handler = logging.FileHandler(app.config["LOG_FILE"])
    file_handler.setLevel(getattr(logging, app.config["LOG_LEVEL"]))

    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    )
    file_handler.setFormatter(formatter)

    app.logger.addHandler(file_handler)
    app.logger.setLevel(getattr(logging, app.config["LOG_LEVEL"]))

    app.logger.info("Приложение запущено")

    @app.after_request
    def add_cache_headers(response):
        if request.endpoint == "static":
            filename = request.path.split("/")[-1]
            if filename.endswith(".svg"):
                response.cache_control.max_age = 31536000
                response.cache_control.public = True
            else:
                response.cache_control.no_cache = True
                response.cache_control.no_store = True
                response.cache_control.must_revalidate = True
        return response

    db.init_app(app)

    try:
        with app.app_context():
            db.engine.connect()
            app.logger.info("Database connection successful")

            try:
                db.create_all()
                app.logger.info("All tables created successfully")
            except Exception as e:
                app.logger.error(f"Error creating tables: {e}")
                app.logger.error(f"create_all failed: {e}")
    except Exception as e:
        app.logger.error(f"Database connection failed: {e}")
        if not app.debug and not app.testing:
            raise

    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)

    from .views.telegram_auth import telegram_login

    csrf.exempt(telegram_login)

    login_manager.login_view = "auth.login"
    login_manager.login_message = (
        "Пожалуйста, войдите в систему для доступа к этой странице."
    )

    from .views import (
        admin_bp,
        api_bp,
        auth_bp,
        main_bp,
        payment_bp,
        tickets_bp,
    )
    from .views.telegram_auth import telegram_auth_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(tickets_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(telegram_auth_bp)

    from .utils.template_filters import (
        extract_filename,
        extract_user_id_from_path,
        format_description,
        format_user_contact,
        get_cdn_url,
        get_cdn_url_production,
        get_telegram_link,
        make_links_clickable,
        smart_truncate,
    )

    app.jinja_env.filters["make_links_clickable"] = make_links_clickable
    app.jinja_env.filters["format_description"] = format_description
    app.jinja_env.filters["smart_truncate"] = smart_truncate
    app.jinja_env.filters["get_cdn_url"] = get_cdn_url
    app.jinja_env.filters["get_cdn_url_production"] = get_cdn_url_production
    app.jinja_env.filters["format_user_contact"] = format_user_contact
    app.jinja_env.filters["get_telegram_link"] = get_telegram_link
    app.jinja_env.filters["extract_filename"] = extract_filename
    app.jinja_env.filters["extract_user_id_from_path"] = extract_user_id_from_path

    @app.context_processor
    def inject_maintenance_mode():
        try:
            from .models import SiteSettings

            maintenance_mode = SiteSettings.get_setting(
                "maintenance_mode", False
            )
            return dict(maintenance_mode=maintenance_mode)
        except Exception as e:
            app.logger.error(f"Error in inject_maintenance_mode: {e}")
            return dict(maintenance_mode=False)

    @app.before_request
    def check_maintenance_mode():
        if request.endpoint == "static":
            return

            for key, file in request.files.items():
                if file and file.filename:
                    app.logger.info(f"Файл {key}: {file.filename}")
                    file_size = getattr(file, "content_length", None)
                    if file_size:
                        app.logger.info(
                            f"Размер файла {key}: {file_size} байт ({file_size / (1024*1024):.2f} MB)"
                        )
                    else:
                        app.logger.info(f"Размер файла {key}: неизвестен")

        try:
            from flask_login import current_user

            from .models import SiteSettings

            maintenance_mode = SiteSettings.get_setting(
                "maintenance_mode", False
            )
            if isinstance(maintenance_mode, str):
                maintenance_mode = maintenance_mode.lower() in [
                    "true",
                    "1",
                    "yes",
                    "on",
                ]

            app.logger.info(
                f"Maintenance mode: {maintenance_mode}, Endpoint: {request.endpoint}"
            )

            if maintenance_mode:
                if request.endpoint == "main.maintenance":
                    return
                elif request.endpoint in ["auth.login", "auth.logout"]:
                    return
                else:
                    if (
                        not current_user.is_authenticated
                        or not current_user.is_admin
                    ):
                        return redirect(url_for("main.maintenance"))
            else:
                if request.endpoint == "main.maintenance":
                    app.logger.info(
                        "Redirecting from maintenance to main page"
                    )
                    return redirect(url_for("main.index"))
        except Exception as e:
            app.logger.error(f"Error checking maintenance mode: {e}")

    @app.errorhandler(404)
    def not_found(error):
        app.logger.warning(f"404 ошибка: {request.url}")
        app.logger.warning(f"Endpoint: {request.endpoint}")
        app.logger.warning(f"Method: {request.method}")
        app.logger.warning(f"Path: {request.path}")
        return (
            render_template(
                "error.html",
                error_code=404,
                error_title="Страница не найдена",
                error_description="К сожалению, запрашиваемая страница не существует или была перемещена.",
                error_time=datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
                error_traceback=None,
            ),
            404,
        )

    return app
