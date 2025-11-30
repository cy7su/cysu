import os
import pytest
import tempfile
from app import create_app
from app.models import db as database


@pytest.fixture(scope="function")
def app():
    """Создание тестового Flask приложения с чистой базой данных."""

    db_fd, db_path = tempfile.mkstemp()

    try:
        os.close(db_fd)
        if os.path.exists(db_path):
            os.unlink(db_path)
    except:
        pass

    original_env = {}
    test_env = {
        "SECRET_KEY": "test_secret_key",
        "UPLOAD_FOLDER": tempfile.mkdtemp(),
        "TICKET_FILES_FOLDER": tempfile.mkdtemp(),
        "TESTING": "True",
        "MAIL_USERNAME": "test@gmail.com",
        "MAIL_PASSWORD": "test_password",
        "MAIL_DEFAULT_SENDER": "test@gmail.com",
        "SKIP_EMAIL_VERIFICATION": "True",
        "LOG_FILE": "/dev/null",
        "SERVER_NAME": "localhost",
    }

    for key in test_env:
        original_env[key] = os.environ.get(key)

    for key, value in test_env.items():
        os.environ[key] = value

    try:
        app = create_app()
        app.config["TESTING"] = True
        app.config["SECRET_KEY"] = "test_secret_key"
        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

        with app.app_context():

            database.create_all()

        yield app
    finally:

        for key, value in original_env.items():
            if value is not None:
                os.environ[key] = value
            else:
                os.environ.pop(key, None)

        try:
            with app.app_context():
                database.session.remove()
                database.drop_all()

        except:
            pass

        cleanup_paths = [
            db_path,
            test_env["UPLOAD_FOLDER"],
            test_env["TICKET_FILES_FOLDER"],
        ]
        for path in cleanup_paths:
            try:
                if os.path.exists(path):
                    if os.path.isfile(path):
                        os.unlink(path)
                    else:
                        import shutil

                        shutil.rmtree(path)
            except Exception as e:
                print(f"Warning: Failed to cleanup {path}: {e}")


@pytest.fixture(scope="function")
def client(app):
    """Тестовый клиент Flask."""
    return app.test_client()


@pytest.fixture(scope="function")
def runner(app):
    """Командная строка Flask для тестов."""
    return app.test_cli_runner()


@pytest.fixture(scope="function")
def db_session(app):
    """База данных для тестов."""
    with app.app_context():
        yield database.session
        database.session.rollback()


@pytest.fixture(scope="function")
def db(app):
    """База данных для тестов."""
    with app.app_context():
        yield database
        database.session.rollback()
