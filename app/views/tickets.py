from datetime import datetime
from typing import Any, Dict, Union

from flask import (
    Blueprint,
    Response,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required

from .. import db
from ..models import Notification, Ticket, TicketFile, TicketMessage, User
from ..services import TicketService
from ..utils.file_storage import FileStorageManager

tickets_bp = Blueprint("tickets", __name__)


@tickets_bp.route("/tickets", methods=["GET", "POST"])
@login_required
def tickets() -> Union[str, Response]:
    if current_user.is_admin:
        tickets_list = (
            Ticket.query.join(User, Ticket.user_id == User.id)
            .order_by(Ticket.created_at.desc())
            .all()
        )
    else:
        tickets_list = (
            Ticket.query.filter_by(user_id=current_user.id).order_by(Ticket.created_at.desc()).all()
        )
    return render_template("tickets/tickets.html", tickets=tickets_list)


@tickets_bp.route("/tickets/<int:ticket_id>")
@login_required
def ticket_detail(ticket_id: int) -> Union[str, Response]:
    ticket = Ticket.query.get_or_404(ticket_id)
    if not current_user.is_admin and ticket.user_id != current_user.id:
        flash("Доступ запрещен", "error")
        return redirect(url_for("main.index"))
    return render_template("tickets/ticket_detail.html", ticket=ticket)


@tickets_bp.route("/tickets/<int:ticket_id>/accept", methods=["POST"])
@login_required
def accept_ticket(ticket_id: int) -> Union[Response, Dict[str, Any]]:
    if not current_user.is_admin:
        return jsonify({"success": False, "error": "Доступ запрещен"})
    success, message = TicketService.change_ticket_status(
        ticket_id=ticket_id, new_status="accepted", admin_id=current_user.id
    )
    if success:
        flash(message, "success")
        return redirect(url_for("tickets.ticket_detail", ticket_id=ticket_id))
    else:
        flash(message, "error")
        return redirect(url_for("tickets.tickets"))


@tickets_bp.route("/tickets/<int:ticket_id>/reject", methods=["POST"])
@login_required
def reject_ticket(ticket_id: int) -> Union[Response, Dict[str, Any]]:
    if not current_user.is_admin:
        return jsonify({"success": False, "error": "Доступ запрещен"})
    success, message = TicketService.change_ticket_status(
        ticket_id=ticket_id, new_status="rejected", admin_id=current_user.id
    )
    if success:
        flash(message, "success")
    else:
        flash(message, "error")
    return redirect(url_for("tickets.tickets"))


@tickets_bp.route("/tickets/<int:ticket_id>/close", methods=["POST"])
@login_required
def close_ticket(ticket_id: int) -> Union[Response, Dict[str, Any]]:
    if not current_user.is_admin:
        return jsonify({"success": False, "error": "Доступ запрещен"})
    success, message = TicketService.change_ticket_status(
        ticket_id=ticket_id, new_status="closed", admin_id=current_user.id
    )
    if success:
        flash(message, "success")
    else:
        flash(message, "error")
    return redirect(url_for("tickets.tickets"))


@tickets_bp.route("/api/ticket/create", methods=["POST"])
@login_required
def create_ticket() -> Dict[str, Any]:
    subject = request.form.get("subject", "").strip()
    message = request.form.get("message", "").strip()
    files = None
    if "files" in request.files:
        files = request.files.getlist("files")
    ticket, error_message = TicketService.create_ticket(
        user_id=current_user.id, subject=subject, message=message, files=files
    )
    if ticket:
        return jsonify(
            {
                "success": True,
                "message": "Тикет успешно создан",
                "ticket_id": ticket.id,
            }
        )
    else:
        return jsonify({"success": False, "error": error_message})


@tickets_bp.route("/tickets/<int:ticket_id>/upload_file", methods=["POST"])
@login_required
def upload_ticket_file(ticket_id: int) -> Dict[str, Any]:
    try:
        ticket = Ticket.query.get_or_404(ticket_id)
        if not current_user.is_admin and ticket.user_id != current_user.id:
            return jsonify({"success": False, "error": "Доступ запрещен"})
        if ticket.status == "closed":
            return jsonify(
                {
                    "success": False,
                    "error": "Нельзя загружать файлы в закрытый тикет",
                }
            )
        file = request.files.get("file")
        if not file or not file.filename:
            return jsonify({"success": False, "error": "Файл не выбран"})
        if not FileStorageManager.validate_file_size(file):
            return jsonify(
                {
                    "success": False,
                    "error": "Файл слишком большой (максимум 200MB)",
                }
            )
        if not FileStorageManager.is_allowed_file(file.filename):
            return jsonify({"success": False, "error": "Неподдерживаемый тип файла"})
        full_path, relative_path = FileStorageManager.get_ticket_file_path(ticket_id, file.filename)
        if FileStorageManager.save_file(file, full_path):
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
                        "size": FileStorageManager.format_file_size(ticket_file.file_size),
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
    try:
        ticket = Ticket.query.get_or_404(ticket_id)
        ticket_file = TicketFile.query.get_or_404(file_id)
        if not current_user.is_admin and ticket.user_id != current_user.id:
            return jsonify({"success": False, "error": "Доступ запрещен"})
        if ticket_file.ticket_id != ticket_id:
            return jsonify({"success": False, "error": "Файл не найден"})
        if ticket.status == "closed":
            return jsonify(
                {
                    "success": False,
                    "error": "Нельзя удалять файлы из закрытого тикета",
                }
            )
        if FileStorageManager.delete_file(ticket_file.file_path):
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
    try:
        ticket = Ticket.query.get_or_404(ticket_id)
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
    try:
        csrf_token = request.headers.get("X-CSRFToken")
        if not csrf_token:
            return (
                jsonify({"success": False, "error": "Отсутствует CSRF токен"}),
                400,
            )
        ticket_id = request.form.get("ticket_id")
        message = request.form.get("message", "").strip()
        files = request.files.getlist("files")
        current_app.logger.info(
            f"Ответ на тикет: ticket_id={ticket_id}, message_length={len(message)}, user={current_user.username}"
        )
        if not ticket_id:
            return jsonify({"success": False, "error": "ID тикета не указан"})
        if not message or len(message) < 1:
            return jsonify(
                {
                    "success": False,
                    "error": "Сообщение не может быть пустым",
                }
            )
        ticket = Ticket.query.get_or_404(ticket_id)
        if not current_user.is_admin and ticket.user_id != current_user.id:
            return jsonify({"success": False, "error": "Доступ запрещен"})
        if ticket.status == "closed":
            return jsonify({"success": False, "error": "Тикет закрыт"})
        is_admin_message = current_user.is_admin
        ticket_message = TicketMessage(
            ticket_id=ticket.id,
            user_id=current_user.id,
            message=message,
            is_admin=is_admin_message,
        )
        db.session.add(ticket_message)
        if is_admin_message:
            ticket.admin_response_at = datetime.utcnow()
            ticket.admin_id = current_user.id
        else:
            ticket.user_response = message
            ticket.user_response_at = datetime.utcnow()
        ticket.updated_at = datetime.utcnow()
        if is_admin_message:
            notification = Notification(
                user_id=ticket.user_id,
                title="Ответ на тикет",
                message=f'Администратор ответил на ваш тикет "{ticket.subject}"',
                type="info",
                link=url_for("tickets.ticket_detail", ticket_id=ticket.id),
            )
            db.session.add(notification)
        if files:
            for file in files:
                if file and file.filename and file.filename.strip():
                    file.seek(0, 2)
                    file_size = file.tell()
                    file.seek(0)
                    if file_size > 200 * 1024 * 1024:
                        continue
                    allowed_extensions = {
                        "png",
                        "jpg",
                        "jpeg",
                        "gif",
                        "pdf",
                        "doc",
                        "docx",
                        "txt",
                        "zip",
                        "rar",
                    }
                    file_extension = (
                        file.filename.rsplit(".", 1)[1].lower() if "." in file.filename else ""
                    )
                    if file_extension not in allowed_extensions:
                        continue
                    from werkzeug.utils import secure_filename

                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    unique_filename = f"{ticket.id}_{'admin' if is_admin_message else 'user'}_response_{timestamp}_{filename}"
                    full_path, relative_path = FileStorageManager.get_ticket_file_path(
                        ticket.id, unique_filename
                    )
                    if FileStorageManager.save_file(file, full_path):
                        file_type = FileStorageManager.get_file_type(filename)
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
    try:
        if not current_user.is_admin or not current_user.admin_mode_enabled:
            return jsonify({"success": False, "error": "Недостаточно прав"})
        closed_tickets = Ticket.query.filter(Ticket.status.in_(["closed", "rejected"])).all()
        deleted_count = 0
        for ticket in closed_tickets:
            for ticket_file in ticket.files:
                try:
                    file_storage = FileStorageManager()
                    file_storage.delete_file(ticket_file.file_path)
                except Exception as e:
                    current_app.logger.warning(
                        f"Не удалось удалить файл {ticket_file.file_path}: {str(e)}"
                    )
            TicketMessage.query.filter_by(ticket_id=ticket.id).delete()
            ticket_link = url_for("tickets.ticket_detail", ticket_id=ticket.id)
            Notification.query.filter_by(link=ticket_link).delete()
            db.session.delete(ticket)
            deleted_count += 1
        db.session.commit()
        current_app.logger.info(
            f"Администратор {current_user.username} удалил {deleted_count} закрытых тикетов"
        )
        return jsonify(
            {
                "success": True,
                "deleted_count": deleted_count,
                "message": f"Удалено {deleted_count} тикетов",
            }
        )
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Ошибка удаления тикетов: {str(e)}")
        return jsonify({"success": False, "error": "Ошибка при удалении тикетов"})
