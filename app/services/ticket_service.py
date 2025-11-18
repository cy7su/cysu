from datetime import datetime
from typing import Dict, List, Optional, Tuple

from .. import db
from ..models import Notification, Ticket, TicketFile, TicketMessage
from ..utils.file_storage import FileStorageManager


class TicketService:
    """Сервис для управления тикетами поддержки"""

    @staticmethod
    def change_ticket_status(
        ticket_id: int, new_status: str, admin_id: int, create_notification: bool = True
    ) -> Tuple[bool, str]:
        """Изменить статус тикета"""
        try:
            ticket = Ticket.query.get(ticket_id)
            if not ticket:
                return False, "Тикет не найден"
            valid_statuses = [
                "pending",
                "accepted",
                "in_progress",
                "rejected",
                "closed",
            ]
            if new_status not in valid_statuses:
                return False, f"Неверный статус: {new_status}"
            old_status = ticket.status
            ticket.status = new_status
            ticket.admin_id = admin_id
            ticket.updated_at = datetime.utcnow()
            if create_notification and old_status != new_status:
                notification = Notification(
                    user_id=ticket.user_id,
                    title="Изменен статус тикета",
                    message=f'Статус вашего тикета "{ticket.subject}" изменен на "{new_status}"',
                    type="info",
                    link=f"/tickets/{ticket.id}",
                )
                db.session.add(notification)
            db.session.commit()
            status_messages = {
                "accepted": "Тикет принят",
                "rejected": "Тикет отклонен",
                "closed": "Тикет закрыт",
            }
            message = status_messages.get(new_status, f"Статус изменен на {new_status}")
            return True, message
        except Exception as e:
            db.session.rollback()
            return False, f"Ошибка изменения статуса: {str(e)}"

    @staticmethod
    def create_ticket(
        user_id: int, subject: str, message: str, files=None
    ) -> Tuple[Optional[Ticket], str]:
        """Создать новый тикет"""
        try:
            subject = subject.strip()
            message = message.strip()
            if not subject or not message:
                return None, "Тема и сообщение обязательны"
            if len(subject) > 200:
                return None, "Тема слишком длинная (максимум 200 символов)"
            if len(message) > 5000:
                return None, "Сообщение слишком длинное (максимум 5000 символов)"
            ticket = Ticket(
                subject=subject,
                message=message,
                user_id=user_id,
                status="pending",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.session.add(ticket)
            db.session.flush()
            if files:
                file_errors = []
                for file in files:
                    if file and file.filename:
                        try:
                            success, error_msg = TicketService._upload_ticket_file(
                                ticket.id, file
                            )
                            if not success:
                                file_errors.append(f"{file.filename}: {error_msg}")
                        except Exception as e:
                            file_errors.append(f"{file.filename}: {str(e)}")
                if file_errors:
                    from flask import current_app

                    current_app.logger.warning(
                        f"Ошибки загрузки файлов тикета {ticket.id}: {file_errors}"
                    )
            db.session.commit()
            from ..models import User

            admins = User.query.filter_by(is_admin=True).all()
            for admin in admins:
                notification = Notification(
                    user_id=admin.id,
                    title="Новый тикет",
                    message=f'Создан новый тикет: "{subject}"',
                    type="info",
                    link=f"/tickets/{ticket.id}",
                )
                db.session.add(notification)
            db.session.commit()
            return ticket, "Тикет успешно создан"
        except Exception as e:
            db.session.rollback()
            return None, f"Ошибка создания тикета: {str(e)}"

    @staticmethod
    def add_ticket_response(
        ticket_id: int, user_id: int, message: str, files=None
    ) -> Tuple[bool, str]:
        """Добавить ответ на тикет"""
        try:
            message = message.strip()
            if not message:
                return False, "Сообщение не может быть пустым"
            if len(message) > 5000:
                return False, "Сообщение слишком длинное (максимум 5000 символов)"
            ticket = Ticket.query.get(ticket_id)
            if not ticket:
                return False, "Тикет не найден"
            if ticket.status == "closed":
                return False, "Нельзя отвечать в закрытый тикет"
            from ..models import User

            user = User.query.get(user_id)
            is_admin_message = user.is_admin if user else False
            ticket_message = TicketMessage(
                ticket_id=ticket.id,
                user_id=user_id,
                message=message,
                is_admin=is_admin_message,
                created_at=datetime.utcnow(),
            )
            db.session.add(ticket_message)
            if is_admin_message:
                ticket.admin_response_at = datetime.utcnow()
                ticket.admin_id = user_id
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
                    link=f"/tickets/{ticket.id}",
                )
                db.session.add(notification)
            if files:
                file_errors = []
                for file in files:
                    if file and file.filename:
                        try:
                            success, error_msg = TicketService._upload_ticket_file(
                                ticket_id, file
                            )
                            if not success:
                                file_errors.append(f"{file.filename}: {error_msg}")
                        except Exception as e:
                            file_errors.append(f"{file.filename}: {str(e)}")
                if file_errors:
                    from flask import current_app

                    current_app.logger.warning(
                        f"Ошибки загрузки файлов в ответе тикета {ticket_id}: {file_errors}"
                    )
            db.session.commit()
            return True, "Ответ отправлен"
        except Exception as e:
            db.session.rollback()
            return False, f"Ошибка отправки ответа: {str(e)}"

    @staticmethod
    def _upload_ticket_file(ticket_id: int, file) -> Tuple[bool, str]:
        """Загрузить файл тикета"""
        try:
            if not file or not file.filename:
                return False, "Файл не выбран"
            if not FileStorageManager.validate_file_size(file):
                return False, "Файл слишком большой (максимум 200MB)"
            if not FileStorageManager.is_allowed_file(file.filename):
                return False, "Неподдерживаемый тип файла"
            full_path, relative_path = FileStorageManager.get_ticket_file_path(
                ticket_id, file.filename
            )
            if not FileStorageManager.save_file(file, full_path):
                return False, "Ошибка сохранения файла"
            ticket_file = TicketFile(
                ticket_id=ticket_id,
                file_path=relative_path,
                file_name=file.filename,
                file_size=FileStorageManager.get_file_size(file),
                file_type=FileStorageManager.get_file_type(file.filename),
                uploaded_at=datetime.utcnow(),
            )
            db.session.add(ticket_file)
            return True, "Файл успешно загружен"
        except Exception as e:
            return False, f"Ошибка загрузки файла: {str(e)}"

    @staticmethod
    def delete_ticket_file(
        ticket_id: int, file_id: int, user_id: int
    ) -> Tuple[bool, str]:
        """Удалить файл тикета"""
        try:
            ticket = Ticket.query.get(ticket_id)
            if not ticket:
                return False, "Тикет не найден"
            ticket_file = TicketFile.query.get(file_id)
            if not ticket_file or ticket_file.ticket_id != ticket_id:
                return False, "Файл не найден"
            if ticket.status == "closed":
                return False, "Нельзя удалять файлы из закрытого тикета"
            from ..models import User

            user = User.query.get(user_id)
            if not (user.is_admin if user else False) and ticket.user_id != user_id:
                return False, "Доступ запрещен"
            if FileStorageManager.delete_file(ticket_file.file_path):
                db.session.delete(ticket_file)
                db.session.commit()
                return True, "Файл успешно удален"
            else:
                return False, "Ошибка удаления файла"
        except Exception as e:
            db.session.rollback()
            return False, f"Ошибка удаления файла: {str(e)}"

    @staticmethod
    def delete_all_closed_tickets(admin_id: int) -> Tuple[bool, str]:
        """Удалить все закрытые тикеты"""
        try:
            from ..models import User

            admin = User.query.get(admin_id)
            if not (admin and admin.is_admin and admin.admin_mode_enabled):
                return False, "Недостаточно прав"
            closed_tickets = Ticket.query.filter(
                Ticket.status.in_(["closed", "rejected"])
            ).all()
            deleted_count = 0
            for ticket in closed_tickets:
                for ticket_file in ticket.files:
                    try:
                        FileStorageManager.delete_file(ticket_file.file_path)
                    except Exception as e:
                        from flask import current_app

                        current_app.logger.warning(
                            f"Не удалось удалить файл {ticket_file.file_path}: {str(e)}"
                        )
                TicketMessage.query.filter_by(ticket_id=ticket.id).delete()
                ticket_link = f"/tickets/{ticket.id}"
                Notification.query.filter_by(link=ticket_link).delete()
                db.session.delete(ticket)
                deleted_count += 1
            db.session.commit()
            return True, f"Удалено {deleted_count} тикетов"
        except Exception as e:
            db.session.rollback()
            return False, f"Ошибка удаления тикетов: {str(e)}"

    @staticmethod
    def get_ticket_files_info(ticket_id: int) -> List[Dict]:
        """Получить информацию о файлах тикета"""
        try:
            ticket = Ticket.query.get(ticket_id)
            if not ticket:
                return []
            files_info = []
            for ticket_file in ticket.files:
                files_info.append(
                    {
                        "id": ticket_file.id,
                        "name": ticket_file.file_name,
                        "size": FileStorageManager.format_file_size(
                            ticket_file.file_size
                        ),
                        "type": ticket_file.file_type,
                        "uploaded_at": ticket_file.uploaded_at.strftime(
                            "%d.%m.%Y %H:%M"
                        ),
                        "path": ticket_file.file_path,
                    }
                )
            return files_info
        except Exception:
            return []

    @staticmethod
    def set_ticket_priority(ticket_id: int, priority: str) -> bool:
        """Установить приоритет тикета."""
        try:
            ticket = Ticket.query.get(ticket_id)
            if not ticket:
                return False

            valid_priorities = ["low", "normal", "high", "urgent"]
            if priority not in valid_priorities:
                return False

            ticket.priority = priority
            ticket.updated_at = datetime.utcnow()
            db.session.commit()

            return True
        except Exception as e:
            from flask import current_app

            current_app.logger.error(f"Error setting ticket priority: {e}")
            db.session.rollback()
            return False

    @staticmethod
    def mass_update_status(ticket_ids: List[int], new_status: str) -> int:
        """Массово обновить статус тикетов."""
        try:
            valid_statuses = ["open", "closed", "pending", "in_progress"]
            if new_status not in valid_statuses:
                return 0

            updated_count = 0
            for ticket_id in ticket_ids:
                ticket = Ticket.query.get(ticket_id)
                if ticket:
                    ticket.status = new_status
                    ticket.updated_at = datetime.utcnow()
                    updated_count += 1

            db.session.commit()
            return updated_count
        except Exception as e:
            from flask import current_app

            current_app.logger.error(f"Error mass updating tickets status: {e}")
            db.session.rollback()
            return 0
