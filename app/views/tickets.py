"""
Модуль системы тикетов
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify, Response
from flask_login import login_required, current_user
from datetime import datetime
from typing import Union, Dict, Any

from ..models import Ticket, TicketFile, TicketMessage, Notification, User
from ..utils.file_storage import FileStorageManager
from ..utils.subdomain_url import get_subdomain_redirect
from .. import db

tickets_bp = Blueprint("tickets", __name__)


@tickets_bp.route("/tickets", methods=["GET", "POST"])
@login_required
def tickets() -> Union[str, Response]:
    """Страница списка тикетов"""
    if current_user.is_admin:
        # Для админов показываем все тикеты
                    tickets_list = (
                Ticket.query.join(User, Ticket.user_id == User.id)
                .order_by(Ticket.created_at.desc())
                .all()
            )
    else:
        # Для пользователей показываем только их тикеты
        tickets_list = (
            Ticket.query.filter_by(user_id=current_user.id)
            .order_by(Ticket.created_at.desc())
            .all()
        )

    return render_template("tickets/tickets.html", tickets=tickets_list)


@tickets_bp.route("/tickets/<int:ticket_id>")
@login_required
def ticket_detail(ticket_id: int) -> Union[str, Response]:
    """Детальная страница тикета"""
    ticket = Ticket.query.get_or_404(ticket_id)

    # Проверяем права доступа
    if not current_user.is_admin and ticket.user_id != current_user.id:
        flash("Доступ запрещен", "error")
        return get_subdomain_redirect("main.index")

    return render_template("tickets/ticket_detail.html", ticket=ticket)


@tickets_bp.route("/tickets/<int:ticket_id>/accept", methods=["POST"])
@login_required
def accept_ticket(ticket_id: int) -> Union[Response, Dict[str, Any]]:
    """Принятие тикета администратором"""
    if not current_user.is_admin:
        return jsonify({"success": False, "error": "Доступ запрещен"})

    ticket = Ticket.query.get_or_404(ticket_id)
    ticket.status = "accepted"
    ticket.admin_id = current_user.id
    ticket.updated_at = datetime.utcnow()

    db.session.commit()

    flash("Тикет принят", "success")
    return get_subdomain_redirect("tickets.ticket_detail", ticket_id=ticket_id)


@tickets_bp.route("/tickets/<int:ticket_id>/reject", methods=["POST"])
@login_required
def reject_ticket(ticket_id: int) -> Union[Response, Dict[str, Any]]:
    """Отклонение тикета администратором"""
    if not current_user.is_admin:
        return jsonify({"success": False, "error": "Доступ запрещен"})

    ticket = Ticket.query.get_or_404(ticket_id)
    ticket.status = "rejected"
    ticket.admin_id = current_user.id
    ticket.updated_at = datetime.utcnow()

    db.session.commit()

    flash("Тикет отклонен", "success")
    return get_subdomain_redirect("tickets.tickets")


@tickets_bp.route("/tickets/<int:ticket_id>/close", methods=["POST"])
@login_required
def close_ticket(ticket_id: int) -> Union[Response, Dict[str, Any]]:
    """Закрытие тикета администратором"""
    if not current_user.is_admin:
        return jsonify({"success": False, "error": "Доступ запрещен"})

    ticket = Ticket.query.get_or_404(ticket_id)
    ticket.status = "closed"
    ticket.admin_id = current_user.id
    ticket.updated_at = datetime.utcnow()

    db.session.commit()

    flash("Тикет закрыт", "success")
    return get_subdomain_redirect("tickets.tickets")


@tickets_bp.route("/api/ticket/create", methods=["POST"])
@login_required
def create_ticket() -> Dict[str, Any]:
    """API для создания нового тикета"""
    try:
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()
        
        if not subject or not message:
            return jsonify({"success": False, "error": "Тема и сообщение обязательны"})
        
        # Создаем тикет
        ticket = Ticket(
            subject=subject,
            message=message,
            user_id=current_user.id,
            status="pending",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.session.add(ticket)
        db.session.commit()
        
        # Обрабатываем файлы, если они есть
        if 'files' in request.files:
            files = request.files.getlist('files')
            for file in files:
                if file and file.filename:
                    # Здесь можно добавить логику сохранения файлов
                    pass
        
        return jsonify({"success": True, "message": "Тикет успешно создан", "ticket_id": ticket.id})
        
    except Exception as e:
        current_app.logger.error(f"Ошибка создания тикета: {str(e)}")
        db.session.rollback()
        return jsonify({"success": False, "error": "Внутренняя ошибка сервера"})





@tickets_bp.route("/tickets/<int:ticket_id>/upload_file", methods=["POST"])
@login_required
def upload_ticket_file(ticket_id: int) -> Dict[str, Any]:
    """Загрузка файла к тикету"""
    try:
        ticket = Ticket.query.get_or_404(ticket_id)

        # Проверяем права доступа
        if not current_user.is_admin and ticket.user_id != current_user.id:
            return jsonify({"success": False, "error": "Доступ запрещен"})

        # Проверяем статус тикета
        if ticket.status == "closed":
            return jsonify(
                {"success": False, "error": "Нельзя загружать файлы в закрытый тикет"}
            )

        file = request.files.get("file")
        if not file or not file.filename:
            return jsonify({"success": False, "error": "Файл не выбран"})

        # Проверяем размер файла
        if not FileStorageManager.validate_file_size(file):
            return jsonify(
                {"success": False, "error": "Файл слишком большой (максимум 200MB)"}
            )

        # Проверяем тип файла
        if not FileStorageManager.is_allowed_file(file.filename):
            return jsonify({"success": False, "error": "Неподдерживаемый тип файла"})

        # Получаем пути для сохранения
        full_path, relative_path = FileStorageManager.get_ticket_file_path(
            ticket_id, file.filename
        )

        # Сохраняем файл
        if FileStorageManager.save_file(file, full_path):
            # Создаем запись о файле
            ticket_file = TicketFile(
                ticket_id=ticket.id,
                file_path=relative_path,
                file_name=file.filename,
                file_size=FileStorageManager.get_file_size(file),
                file_type=FileStorageManager.get_file_type(file.filename),
            )

            db.session.add(ticket_file)
            db.session.commit()

            return jsonify(
                {
                    "success": True,
                    "message": "Файл успешно загружен",
                    "file": {
                        "id": ticket_file.id,
                        "name": ticket_file.file_name,
                        "size": FileStorageManager.format_file_size(
                            ticket_file.file_size
                        ),
                        "type": ticket_file.file_type,
                    },
                }
            )
        else:
            return jsonify({"success": False, "error": "Ошибка сохранения файла"})

    except Exception as e:
        current_app.logger.error(f"Ошибка загрузки файла тикета: {str(e)}")
        return jsonify({"success": False, "error": "Ошибка загрузки файла"})


@tickets_bp.route("/tickets/<int:ticket_id>/delete_file/<int:file_id>", methods=["POST"])
@login_required
def delete_ticket_file(ticket_id: int, file_id: int) -> Dict[str, Any]:
    """Удаление файла тикета"""
    try:
        ticket = Ticket.query.get_or_404(ticket_id)
        ticket_file = TicketFile.query.get_or_404(file_id)

        # Проверяем права доступа
        if not current_user.is_admin and ticket.user_id != current_user.id:
            return jsonify({"success": False, "error": "Доступ запрещен"})

        # Проверяем, что файл принадлежит тикету
        if ticket_file.ticket_id != ticket_id:
            return jsonify({"success": False, "error": "Файл не найден"})

        # Проверяем статус тикета
        if ticket.status == "closed":
            return jsonify(
                {"success": False, "error": "Нельзя удалять файлы из закрытого тикета"}
            )

        # Удаляем файл с диска
        if FileStorageManager.delete_file(ticket_file.file_path):
            # Удаляем запись из БД
            db.session.delete(ticket_file)
            db.session.commit()

            return jsonify({"success": True, "message": "Файл успешно удален"})
        else:
            return jsonify({"success": False, "error": "Ошибка удаления файла"})

    except Exception as e:
        current_app.logger.error(f"Ошибка удаления файла тикета: {str(e)}")
        return jsonify({"success": False, "error": "Ошибка удаления файла"})


@tickets_bp.route("/api/tickets/<int:ticket_id>/files")
@login_required
def get_ticket_files(ticket_id: int) -> Dict[str, Any]:
    """Получение списка файлов тикета"""
    try:
        ticket = Ticket.query.get_or_404(ticket_id)

        # Проверяем права доступа
        if not current_user.is_admin and ticket.user_id != current_user.id:
            return jsonify({"success": False, "error": "Доступ запрещен"})

        files_info = []
        for ticket_file in ticket.files:
            files_info.append(
                {
                    "id": ticket_file.id,
                    "name": ticket_file.file_name,
                    "size": FileStorageManager.format_file_size(ticket_file.file_size),
                    "type": ticket_file.file_type,
                    "uploaded_at": ticket_file.uploaded_at.strftime("%d.%m.%Y %H:%M"),
                    "path": ticket_file.file_path,
                }
            )

        return jsonify({"success": True, "files": files_info})

    except Exception as e:
        current_app.logger.error(f"Ошибка получения файлов тикета: {str(e)}")
        return jsonify({"success": False, "error": "Ошибка получения файлов"})





@tickets_bp.route("/api/ticket/response", methods=["POST"])
@login_required
def ticket_response() -> Dict[str, Any]:
    """API для ответа на тикет (для пользователей и админов)"""
    try:
        # Проверяем CSRF токен
        csrf_token = request.headers.get('X-CSRFToken')
        if not csrf_token:
            return jsonify({"success": False, "error": "Отсутствует CSRF токен"}), 400
        
        # Получаем данные из формы
        ticket_id = request.form.get("ticket_id")
        message = request.form.get("message", "").strip()
        files = request.files.getlist("files")
        
        current_app.logger.info(f"Ответ на тикет: ticket_id={ticket_id}, message_length={len(message)}, user={current_user.username}")

        # Валидация
        if not ticket_id:
            return jsonify({"success": False, "error": "ID тикета не указан"})
            
        if not message or len(message) < 1:
            return jsonify(
                {
                    "success": False,
                    "error": "Сообщение не может быть пустым",
                }
            )

        # Находим тикет
        ticket = Ticket.query.get_or_404(ticket_id)

        # Проверяем права доступа
        if not current_user.is_admin and ticket.user_id != current_user.id:
            return jsonify({"success": False, "error": "Доступ запрещен"})

        # Проверяем, что тикет не закрыт
        if ticket.status == "closed":
            return jsonify({"success": False, "error": "Тикет закрыт"})

        # Создаем новое сообщение
        is_admin_message = current_user.is_admin
        ticket_message = TicketMessage(
            ticket_id=ticket.id,
            user_id=current_user.id,
            message=message,
            is_admin=is_admin_message,
        )

        db.session.add(ticket_message)

        # Обновляем время последнего ответа
        if is_admin_message:
            ticket.admin_response_at = datetime.utcnow()
            ticket.admin_id = current_user.id
        else:
            ticket.user_response = message
            ticket.user_response_at = datetime.utcnow()
        
        ticket.updated_at = datetime.utcnow()

        # Создаем уведомление для противоположной стороны
        if is_admin_message:
            # Админ ответил - уведомляем пользователя
            notification = Notification(
                user_id=ticket.user_id,
                title="Ответ на тикет",
                message=f'Администратор ответил на ваш тикет "{ticket.subject}"',
                type="info",
                link=url_for("tickets.ticket_detail", ticket_id=ticket.id),
            )
            db.session.add(notification)

        # Обрабатываем файлы
        if files:
            for file in files:
                if file and file.filename and file.filename.strip():
                    # Проверяем размер файла (максимум 200MB)
                    file.seek(0, 2)
                    file_size = file.tell()
                    file.seek(0)

                    if file_size > 200 * 1024 * 1024:  # 200MB
                        continue

                    # Проверяем расширение файла
                    allowed_extensions = {
                        "png", "jpg", "jpeg", "gif", "pdf", 
                        "doc", "docx", "txt", "zip", "rar"
                    }
                    file_extension = (
                        file.filename.rsplit(".", 1)[1].lower()
                        if "." in file.filename else ""
                    )

                    if file_extension not in allowed_extensions:
                        continue

                    # Сохраняем файл через FileStorageManager
                    from werkzeug.utils import secure_filename
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    unique_filename = f"{ticket.id}_{'admin' if is_admin_message else 'user'}_response_{timestamp}_{filename}"

                    # Получаем пути для сохранения
                    full_path, relative_path = FileStorageManager.get_ticket_file_path(
                        ticket.id, unique_filename
                    )

                    # Сохраняем файл
                    if FileStorageManager.save_file(file, full_path):
                        # Определяем тип файла
                        file_type = FileStorageManager.get_file_type(filename)

                        # Создаем запись о файле
                        ticket_file = TicketFile(
                            ticket_id=ticket.id,
                            file_path=relative_path,
                            file_name=filename,
                            file_size=file_size,
                            file_type=file_type,
                        )
                        db.session.add(ticket_file)

        db.session.commit()

        return jsonify({"success": True, "message": "Ответ отправлен"})

    except Exception as e:
        current_app.logger.error(f"Ошибка отправки ответа: {str(e)}", exc_info=True)
        return jsonify({"success": False, "error": f"Ошибка отправки ответа: {str(e)}"})


@tickets_bp.route("/api/delete_all_closed_tickets", methods=["POST"])
@login_required
def delete_all_closed_tickets():
    """API для удаления всех закрытых и отклоненных тикетов (только для админов)"""
    try:
        # Проверяем права администратора
        if not current_user.is_admin or not current_user.admin_mode_enabled:
            return jsonify({"success": False, "error": "Недостаточно прав"})
        
        # Находим все закрытые и отклоненные тикеты
        closed_tickets = Ticket.query.filter(
            Ticket.status.in_(['closed', 'rejected'])
        ).all()
        
        deleted_count = 0
        
        for ticket in closed_tickets:
            # Удаляем связанные файлы
            for ticket_file in ticket.files:
                try:
                    file_storage = FileStorageManager()
                    file_storage.delete_file(ticket_file.file_path)
                except Exception as e:
                    current_app.logger.warning(f"Не удалось удалить файл {ticket_file.file_path}: {str(e)}")
            
            # Удаляем связанные сообщения
            TicketMessage.query.filter_by(ticket_id=ticket.id).delete()
            
            # Удаляем связанные уведомления (через link)
            ticket_link = url_for("tickets.ticket_detail", ticket_id=ticket.id)
            Notification.query.filter_by(link=ticket_link).delete()
            
            # Удаляем сам тикет
            db.session.delete(ticket)
            deleted_count += 1
        
        db.session.commit()
        
        current_app.logger.info(f"Администратор {current_user.username} удалил {deleted_count} закрытых тикетов")
        
        return jsonify({
            "success": True, 
            "deleted_count": deleted_count,
            "message": f"Удалено {deleted_count} тикетов"
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Ошибка удаления тикетов: {str(e)}")
        return jsonify({"success": False, "error": "Ошибка при удалении тикетов"})
