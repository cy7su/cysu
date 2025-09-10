
from .admin import admin_bp
from .api import api_bp
from .auth import auth_bp
from .main import main_bp
from .payment import payment_bp
from .tickets import tickets_bp

__all__ = [
    'main_bp',
    'auth_bp',
    'payment_bp',
    'tickets_bp',
    'admin_bp',
    'api_bp'
]
