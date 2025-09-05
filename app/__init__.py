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
    app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # /root
    static_folder_path = os.path.join(app_root, 'app', 'static')  # /root/app/static
    
    app = Flask(__name__, 
                instance_path=None, 
                instance_relative_config=False,
                static_folder=static_folder_path,
                static_url_path='/static',
                subdomain_matching=True)
    
    
    # Middleware для замены URL на поддомене
    @app.after_request
    def replace_urls_for_subdomain(response):
        """Заменяет все URL на поддомен в HTML ответе"""
        try:
            if (hasattr(request, 'host') and request.host and '.' in request.host and 
                not request.host.startswith('www.') and request.host != 'cysu.ru'):
                
                subdomain = request.host.split('.')[0]
                if subdomain != 'cysu':  # Не основной домен
                    # Проверяем, что это HTML ответ
                    if response.content_type and 'text/html' in response.content_type:
                        # Получаем HTML контент
                        html = response.get_data(as_text=True)
                        
                        # Заменяем все ссылки на основной домен на поддомен
                        html = html.replace('https://cysu.ru', f'https://{request.host}')
                        html = html.replace('http://cysu.ru', f'https://{request.host}')
                        
                        # Заменяем относительные ссылки на абсолютные с поддоменом
                        import re
                        # Паттерн для href и src с относительными путями (исключаем уже обработанные)
                        html = re.sub(r'href="(/[^"]*)"', rf'href="https://{request.host}\1"', html)
                        html = re.sub(r'src="(/[^"]*)"', rf'src="https://{request.host}\1"', html)
                        html = re.sub(r'action="(/[^"]*)"', rf'action="https://{request.host}\1"', html)
                        # Заменяем data-url атрибуты
                        html = re.sub(r'data-url="(/[^"]*)"', rf'data-url="https://{request.host}\1"', html)
                        
                        # Устанавливаем новый контент
                        response.set_data(html)
        except Exception as e:
            # В случае ошибки просто пропускаем
            pass
        
        return response
    
    
    # Конфигурация из переменных окружения
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key-change-in-production')
    # Настройка для работы с поддоменами
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
    # Создаем абсолютные пути относительно корня приложения
    # __file__ = /root/cysu/app/__init__.py, поэтому app_root должен быть /root/cysu
    app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # /root/cysu
    # Создаем абсолютные пути
    upload_folder = os.getenv('UPLOAD_FOLDER', os.path.join(app_root, 'app', 'static', 'uploads'))
    ticket_folder = os.getenv('TICKET_FILES_FOLDER', os.path.join(app_root, 'app', 'static', 'ticket_files'))
    # Убеждаемся что пути абсолютные
    upload_folder = os.path.abspath(upload_folder)
    ticket_folder = os.path.abspath(ticket_folder)
    
    app.config['UPLOAD_FOLDER'] = upload_folder
    app.config['TICKET_FILES_FOLDER'] = ticket_folder
    
    # Логируем пути для отладки
    app.logger.info(f"STATIC_FOLDER: {static_folder_path}")
    app.logger.info(f"UPLOAD_FOLDER: {upload_folder}")
    app.logger.info(f"TICKET_FILES_FOLDER: {ticket_folder}")
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
    app.config['YOOKASSA_SECRET_KEY'] = os.getenv('YOOKASHA_SECRET_KEY', 'your-secret-key')
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
    from .views.subdomain import subdomain_bp
    from .views.telegram_auth import telegram_auth_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(tickets_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(telegram_auth_bp)
    
    # Регистрируем blueprint для поддомена q
    app.register_blueprint(subdomain_bp, subdomain='q')
    
    # Регистрируем фильтры шаблонов
    from .utils.template_filters import make_links_clickable, format_description, smart_truncate, format_user_contact, get_telegram_link
    app.jinja_env.filters['make_links_clickable'] = make_links_clickable
    app.jinja_env.filters['format_description'] = format_description
    app.jinja_env.filters['smart_truncate'] = smart_truncate
    app.jinja_env.filters['format_user_contact'] = format_user_contact
    app.jinja_env.filters['get_telegram_link'] = get_telegram_link
    
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
        return render_template("404.html"), 404
    
    # Настройка заголовков кеширования для статических файлов
    @app.after_request
    def add_cache_headers(response):
        if response.mimetype in ['image/png', 'image/x-icon', 'image/jpeg', 'image/gif', 'image/webp']:
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
    
    # Тестовый маршрут для проверки статических файлов
    @app.route('/test-static')
    def test_static():
        """Тестовый маршрут для проверки статических файлов"""
        import os
        static_path = os.path.join(os.path.dirname(__file__), 'static')
        js_path = os.path.join(static_path, 'js', 'svg-patterns.js')
        
        if os.path.exists(js_path):
            with open(js_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return f'<h1>Статический файл найден!</h1><pre>{content[:500]}...</pre>'
        else:
            return f'<h1>Файл не найден!</h1><p>Путь: {js_path}</p><p>Существует static: {os.path.exists(static_path)}</p>'
    
    return app 