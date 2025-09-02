"""
Модуль API endpoints
"""

from flask import Blueprint, request, current_app, jsonify
from flask_login import login_required, current_user
from typing import Dict, Any

from ..models import Notification

api_bp = Blueprint("api", __name__)


@api_bp.route("/api/notifications")
@login_required
def get_notifications() -> Dict[str, Any]:
    """API для получения уведомлений пользователя"""
    # Получаем все непрочитанные уведомления пользователя
    notifications = (
        Notification.query.filter_by(user_id=current_user.id, is_read=False)
        .order_by(Notification.created_at.desc())
        .all()
    )

    return jsonify(
        {
            "success": True,
            "notifications": [
                {
                    "id": n.id,
                    "title": n.title,
                    "message": n.message,
                    "type": n.type,
                    "link": n.link,
                    "created_at": n.created_at.strftime("%d.%m.%Y в %H:%M"),
                }
                for n in notifications
            ],
        }
    )


@api_bp.route("/api/notifications/<int:notification_id>/read", methods=["POST"])
@login_required
def mark_notification_read(notification_id: int) -> Dict[str, Any]:
    """API для отметки уведомления как прочитанного"""
    from .. import db
    
    notification = Notification.query.get_or_404(notification_id)

    # Проверяем, что уведомление принадлежит текущему пользователю
    if notification.user_id != current_user.id:
        return jsonify({"success": False, "error": "Доступ запрещен"})

    notification.is_read = True
    db.session.commit()

    return jsonify({"success": True})


@api_bp.errorhandler(400)
def bad_request(error) -> Dict[str, Any]:
    """Обработчик ошибки 400 Bad Request"""
    current_app.logger.error("=== ОШИБКА 400 BAD REQUEST ===")
    current_app.logger.error(f"Ошибка: {error}")
    current_app.logger.error(f"Запрос: {request}")
    current_app.logger.error(f"Данные формы: {request.form}")
    current_app.logger.error(f"Файлы: {request.files}")
    current_app.logger.error(f"Заголовки: {dict(request.headers)}")
    return jsonify({"success": False, "error": "Некорректный запрос"}), 400
