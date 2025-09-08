from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
import logging
import os

# Загружаем переменные окружения
load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()

def create_app():
    # Определяем правильный путь к статическим файлам
    app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # /root/cysu
    static_folder_path = os.path.join(app_root, 'app', 'static')  # /root/cysu/app/static
    
    app = Flask(__name__, 
                instance_path=None, 
                instance_relative_config=False,
                static_folder=static_folder_path,
                static_url_path='/static')
    
    
    
    # Конфигурация из переменных окружения
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key-change-in-production')
    # Настройка сервера
    app.config['SERVER_NAME'] = os.getenv('SERVER_NAME', 'cysu.ru')
    # Конфигурация базы данных - создаем в корне проекта
    db_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app.db'))
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    
    # Создаем директорию для базы данных если её нет
    db_dir = os.path.dirname(db_path)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    

    
    # Конфигурация загрузки файлов
    # Используем уже определенный app_root
    
    # Сначала пробуем найти правильный путь
    possible_upload_paths = [
        os.path.join(app_root, 'app', 'static', 'uploads'),
        '/root/cysu/app/static/uploads'
    ]
    
    upload_folder = None
    for path in possible_upload_paths:
        if os.path.exists(path):
            upload_folder = path
            break
    
    # Если не нашли, используем переменную окружения или создаем по умолчанию
    if not upload_folder:
        upload_folder = os.getenv('UPLOAD_FOLDER', os.path.join(app_root, 'app', 'static', 'uploads'))
    
    # Аналогично для ticket_folder
    possible_ticket_paths = [
        os.path.join(app_root, 'app', 'static', 'ticket_files'),
        '/root/cysu/app/static/ticket_files'
    ]
    
    ticket_folder = None
    for path in possible_ticket_paths:
        if os.path.exists(path):
            ticket_folder = path
            break
    
    if not ticket_folder:
        ticket_folder = os.getenv('TICKET_FILES_FOLDER', os.path.join(app_root, 'app', 'static', 'ticket_files'))
    # Убеждаемся что пути абсолютные
    upload_folder = os.path.abspath(upload_folder)
    ticket_folder = os.path.abspath(ticket_folder)
    
    app.config['UPLOAD_FOLDER'] = upload_folder
    app.config['TICKET_FILES_FOLDER'] = ticket_folder
    
    # Логируем пути для отладки
    app.logger.info(f"APP_ROOT: {app_root}")
    app.logger.info(f"STATIC_FOLDER: {static_folder_path}")
    app.logger.info(f"UPLOAD_FOLDER: {upload_folder}")
    app.logger.info(f"TICKET_FILES_FOLDER: {ticket_folder}")
    app.logger.info(f"UPLOAD_FOLDER exists: {os.path.exists(upload_folder)}")
    if os.path.exists(upload_folder):
        app.logger.info(f"UPLOAD_FOLDER contents: {os.listdir(upload_folder)}")
    max_content_length = int(os.getenv('MAX_CONTENT_LENGTH', 200 * 1024 * 1024))
    app.config['MAX_CONTENT_LENGTH'] = max_content_length
    app.logger.info(f"MAX_CONTENT_LENGTH установлен: {max_content_length} байт ({max_content_length / (1024*1024):.1f} MB)")
    
    # Создаем необходимые директории для загрузки файлов
    for folder in [app.config['UPLOAD_FOLDER']]:
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
    
    # Конфигурация почты
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'False').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'your-email@gmail.com')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'your-app-password')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'your-email@gmail.com')
    
    # Конфигурация платежей
    app.config['YOOKASSA_SHOP_ID'] = os.getenv('YOOKASSA_SHOP_ID', 'your-shop-id')
    app.config['YOOKASSA_SECRET_KEY'] = os.getenv('YOOKASSA_SECRET_KEY', 'your-secret-key')
    app.config['YOOKASSA_TEST_MODE'] = os.getenv('YOOKASSA_TEST_MODE', 'True').lower() == 'true'
    
    # Цены подписки
    app.config['SUBSCRIPTION_PRICES'] = {
        '1': float(os.getenv('SUBSCRIPTION_PRICE_1', 89.00)),
        '3': float(os.getenv('SUBSCRIPTION_PRICE_3', 199.00)),
        '6': float(os.getenv('SUBSCRIPTION_PRICE_6', 349.00)),
        '12': float(os.getenv('SUBSCRIPTION_PRICE_12', 469.00))
    }
    app.config['SUBSCRIPTION_CURRENCY'] = os.getenv('SUBSCRIPTION_CURRENCY', 'RUB')
    
    # Настройки логирования
    app.config['LOG_FILE'] = os.getenv('LOG_FILE', 'logs/app.log')
    app.config['LOG_LEVEL'] = os.getenv('LOG_LEVEL', 'INFO')
    
    # Настройка логирования
    # Создаем директорию для логов если её нет
    log_dir = os.path.dirname(app.config['LOG_FILE'])
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Настраиваем файловый обработчик
    file_handler = logging.FileHandler(app.config['LOG_FILE'])
    file_handler.setLevel(getattr(logging, app.config['LOG_LEVEL']))
    
    # Настраиваем формат логов
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    file_handler.setFormatter(formatter)
    
    # Добавляем обработчик к логгеру приложения
    app.logger.addHandler(file_handler)
    app.logger.setLevel(getattr(logging, app.config['LOG_LEVEL']))
    
    app.logger.info('Приложение запущено')
    
    # Настройка кэширования: только SVG кэшируется
    @app.after_request
    def add_cache_headers(response):
        if request.endpoint == 'static':
            filename = request.path.split('/')[-1]
            if filename.endswith('.svg'):
                # SVG файлы кэшируются на 1 год
                response.cache_control.max_age = 31536000
                response.cache_control.public = True
            else:
                # Все остальное не кэшируется
                response.cache_control.no_cache = True
                response.cache_control.no_store = True
                response.cache_control.must_revalidate = True
        return response
    
    db.init_app(app)
    
    # Проверка подключения к базе данных и создание таблиц
    try:
        with app.app_context():
            # Проверяем подключение
            db.engine.connect()
            app.logger.info('Database connection successful')
            
            # Принудительно создаем все таблицы
            try:
                db.create_all()
                app.logger.info('All tables created successfully')
            except Exception as e:
                app.logger.error(f'Error creating tables: {e}')
                # Если не удалось создать таблицы, логируем ошибку но не прерываем работу
                app.logger.error(f'create_all failed: {e}')
    except Exception as e:
        app.logger.error(f'Database connection failed: {e}')
        if not app.debug and not app.testing:
            raise
    
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    
    # Отключаем CSRF для Telegram авторизации
    from .views.telegram_auth import telegram_login
    csrf.exempt(telegram_login)
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Пожалуйста, войдите в систему для доступа к этой странице.'
    
    # Регистрируем все blueprint'ы
    from .views import (
        main_bp, auth_bp, payment_bp, 
        tickets_bp, admin_bp, api_bp
    )
    from .views.telegram_auth import telegram_auth_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(tickets_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(telegram_auth_bp)
    
    
    # Регистрируем фильтры шаблонов
    from .utils.template_filters import make_links_clickable, format_description, smart_truncate, format_user_contact, get_telegram_link, extract_filename, get_cdn_url, get_cdn_url_production
    app.jinja_env.filters['make_links_clickable'] = make_links_clickable
    app.jinja_env.filters['format_description'] = format_description
    app.jinja_env.filters['smart_truncate'] = smart_truncate
    app.jinja_env.filters['get_cdn_url'] = get_cdn_url
    app.jinja_env.filters['get_cdn_url_production'] = get_cdn_url_production
    app.jinja_env.filters['format_user_contact'] = format_user_contact
    app.jinja_env.filters['get_telegram_link'] = get_telegram_link
    app.jinja_env.filters['extract_filename'] = extract_filename
    
    # Context processor для проверки технических работ
    @app.context_processor
    def inject_maintenance_mode():
        """Добавляет информацию о режиме технических работ в шаблоны"""
        try:
            from .models import SiteSettings
            maintenance_mode = SiteSettings.get_setting('maintenance_mode', False)
            return dict(maintenance_mode=maintenance_mode)
        except Exception as e:
            app.logger.error(f'Error in inject_maintenance_mode: {e}')
            return dict(maintenance_mode=False)
    
    # Middleware для проверки технических работ
    @app.before_request
    def check_maintenance_mode():
        """Проверяет режим технических работ"""
        # Пропускаем только статические файлы
        if request.endpoint == 'static':
            return

            # Логируем информацию о файлах
            for key, file in request.files.items():
                if file and file.filename:
                    app.logger.info(f"Файл {key}: {file.filename}")
                    file_size = getattr(file, 'content_length', None)
                    if file_size:
                        app.logger.info(f"Размер файла {key}: {file_size} байт ({file_size / (1024*1024):.2f} MB)")
                    else:
                        app.logger.info(f"Размер файла {key}: неизвестен")
        
        try:
            # Импортируем здесь, чтобы избежать циклических импортов
            from .models import SiteSettings
            from flask_login import current_user
            
            # Проверяем, включен ли режим технических работ
            maintenance_mode = SiteSettings.get_setting('maintenance_mode', False)
            # Преобразуем строковое значение в булево
            if isinstance(maintenance_mode, str):
                maintenance_mode = maintenance_mode.lower() in ['true', '1', 'yes', 'on']
            
            # Логируем для отладки
            app.logger.info(f'Maintenance mode: {maintenance_mode}, Endpoint: {request.endpoint}')
            
            if maintenance_mode:
                # Если технические работы включены
                if request.endpoint == 'main.maintenance':
                    # Разрешаем доступ к странице технических работ
                    return
                elif request.endpoint in ['auth.login', 'auth.logout']:
                    # Разрешаем доступ к авторизации
                    return
                else:
                    # Если пользователь не админ, перенаправляем на страницу технических работ
                    if not current_user.is_authenticated or not current_user.is_admin:
                        return redirect(url_for('main.maintenance'))
            else:
                # Если технические работы отключены
                if request.endpoint == 'main.maintenance':
                    # Перенаправляем на главную страницу
                    app.logger.info('Redirecting from maintenance to main page')
                    return redirect(url_for('main.index'))
        except Exception as e:
            app.logger.error(f'Error checking maintenance mode: {e}')
    
    # Обработчик ошибки 404 на уровне приложения
    @app.errorhandler(404)
    def not_found(error):
        """Обработчик ошибки 404 Not Found"""
        app.logger.warning(f"404 ошибка: {request.url}")
        app.logger.warning(f"Endpoint: {request.endpoint}")
        app.logger.warning(f"Method: {request.method}")
        app.logger.warning(f"Path: {request.path}")
        return render_template("404.html"), 404
    
    # Настройка заголовков кеширования для статических файлов
    @app.after_request
    def add_cache_headers(response):
        if request.endpoint == 'static' or request.endpoint == 'main.serve_file':
            filename = request.path.split('/')[-1]
            
            # Специальная обработка PDF файлов
            if filename.lower().endswith('.pdf'):
                # Для PDF файлов заголовки уже установлены в serve_file
                if request.endpoint == 'static':
                    response.headers['Content-Type'] = 'application/pdf'
                    response.headers['Content-Disposition'] = 'attachment'
                    response.cache_control.max_age = 3600  # 1 час
                    response.cache_control.public = True
                    # Отключаем сжатие для PDF
                    response.headers['Content-Encoding'] = 'identity'
            elif response.mimetype in ['image/png', 'image/x-icon', 'image/jpeg', 'image/gif', 'image/webp']:
                # Для иконок и изображений - короткий кеш
                response.cache_control.max_age = 300  # 5 минут
                response.cache_control.public = True
            elif response.mimetype in ['text/css', 'application/javascript']:
                # Для CSS и JS - средний кеш
                response.cache_control.max_age = 3600  # 1 час
                response.cache_control.public = True
            else:
                # Для остальных файлов - стандартный кеш
                response.cache_control.max_age = 86400  # 24 часа
                response.cache_control.public = True
        return response
    

    # Дублирующий маршрут serve_pdf удален - используется основной serve_file

    # Тестовый маршрут для проверки PDF файлов
    @app.route('/test-pdf')
    def test_pdf():
        """Тестовый маршрут для проверки PDF файлов"""
        import os
        from flask import jsonify
        
        upload_folder = app.config.get('UPLOAD_FOLDER', 'app/static/uploads')
        pdf_files = []
        
        # Ищем PDF файлы в папке uploads
        for root, dirs, files in os.walk(upload_folder):
            for file in files:
                if file.lower().endswith('.pdf'):
                    relative_path = os.path.relpath(os.path.join(root, file), upload_folder)
                    pdf_files.append({
                        'filename': file,
                        'path': relative_path,
                        'url': f'/static/uploads/{relative_path}',
                        'size': os.path.getsize(os.path.join(root, file))
                    })
        
        return jsonify({
            'pdf_files': pdf_files,
            'total_count': len(pdf_files)
        })
    
    
    return app 