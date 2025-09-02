"""
Модуль админских функций
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify, Response
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta
import random
import string
from typing import Union, Dict, Any

from ..models import (
    User, Material, Subject, Payment, ChatMessage, EmailVerification, 
    Ticket, TicketFile, TicketMessage, Notification, 
    Group, SubjectGroup, SiteSettings
)
from ..forms import (
    AdminUserForm, MaterialForm, SubjectForm, GroupForm, 
    SubjectGroupForm, SiteSettingsForm
)
from ..utils.file_storage import FileStorageManager
# Сервис коротких ссылок удален
from .. import db

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin/users", methods=["GET", "POST"])
@login_required
def admin_users() -> Union[str, Response]:
    """Админка для управления пользователями"""
    if not current_user.is_admin:
        flash("Доступ запрещён")
        return redirect(url_for("main.index"))

    form = AdminUserForm()
    password_map = {}
    message = ""

    # Диагностика формы
    current_app.logger.info(f"Форма создана: {form}")
    current_app.logger.info(
        f"CSRF токен: {form.csrf_token.current_token if form.csrf_token else 'Нет токена'}"
    )

    # Создание нового пользователя
    current_app.logger.info(f"Метод запроса: {request.method}")
    current_app.logger.info(f"Данные формы: {request.form}")
    current_app.logger.info(f"Значение submit: {request.form.get('submit')}")

    # Проверяем все возможные условия
    if request.method == "POST":
        current_app.logger.info("POST запрос получен")
        if request.form.get("submit") == "Зарегистрироваться":
            current_app.logger.info("Найдена кнопка 'Зарегистрироваться'")
        else:
            current_app.logger.info(
                f"Кнопка не найдена. Доступные поля: {list(request.form.keys())}"
            )

    if request.method == "POST" and request.form.get("submit") == "Зарегистрироваться":
        current_app.logger.info("Обрабатываем форму создания пользователя")
        current_app.logger.info("Проверяем валидацию формы")
        current_app.logger.info(f"Ошибки формы: {form.errors}")

        if form.validate_on_submit():
            current_app.logger.info(
                f"Админка - создание пользователя: {form.username.data}, {form.email.data}"
            )
            try:
                # Проверяем, что пользователь с таким username или email не существует
                existing_user = User.query.filter(
                    (User.username == form.username.data)
                    | (User.email == form.email.data)
                ).first()

                if existing_user:
                    if existing_user.username == form.username.data:
                        current_app.logger.warning(
                            f"Пользователь с именем {form.username.data} уже существует"
                        )
                        flash(
                            f'Пользователь с именем "{form.username.data}" уже существует',
                            "error",
                        )
                    else:
                        current_app.logger.warning(
                            f"Пользователь с email {form.email.data} уже существует"
                        )
                        flash(
                            f'Пользователь с email "{form.email.data}" уже существует',
                            "error",
                        )
                else:
                    current_app.logger.info(
                        f"Создаем нового пользователя: {form.username.data}"
                    )
                    user = User(
                        username=form.username.data,
                        email=form.email.data,
                        password=generate_password_hash(form.password.data),
                        is_admin=False,
                        is_subscribed=False,
                        group_id=form.group_id.data if form.group_id.data else None,
                    )
                    db.session.add(user)
                    db.session.commit()
                    current_app.logger.info(
                        f"Пользователь успешно создан с ID: {user.id}"
                    )
                    password_map[user.id] = form.password.data
                    flash(f"Пользователь {user.username} успешно создан")

            except Exception as e:
                current_app.logger.error(f"Ошибка создания пользователя: {str(e)}")
                import traceback

                current_app.logger.error(f"Traceback: {traceback.format_exc()}")
                db.session.rollback()
                flash("Ошибка при создании пользователя", "error")
        else:
            current_app.logger.warning(f"Форма админки не валидна: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    current_app.logger.warning(f"Ошибка в поле {field}: {error}")

    # Сброс пароля пользователя
    if request.method == "POST" and request.form.get("reset_user_id"):
        try:
            user_id = int(request.form.get("reset_user_id"))
            user = User.query.get(user_id)
            if user:
                new_password = "".join(
                    random.choices(
                        string.ascii_letters + string.digits + "!@#$%^&*", k=10
                    )
                )
                user.password = generate_password_hash(new_password)
                db.session.commit()
                password_map[user.id] = new_password
                flash(f"Пароль для пользователя {user.username} сброшен")
            else:
                flash("Пользователь не найден", "error")
        except Exception as e:
            current_app.logger.error(f"Ошибка сброса пароля: {str(e)}")
            db.session.rollback()  # Откатываем транзакцию при ошибке
            flash("Ошибка при сбросе пароля", "error")

    # Удаление пользователя
    if request.method == "POST" and request.form.get("delete_user_id"):
        try:
            user_id = int(request.form.get("delete_user_id"))
            current_app.logger.info(f"Попытка удаления пользователя с ID: {user_id}")
            user = User.query.get(user_id)
            if user:
                current_app.logger.info(
                    f"Найден пользователь для удаления: {user.username} (ID: {user.id})"
                )
                if user.id == current_user.id:
                    flash("Нельзя удалить самого себя", "error")
                elif user.is_admin:
                    flash("Нельзя удалить администратора", "error")
                else:
                    username = user.username
                    current_app.logger.info(
                        f"Начинаем удаление пользователя {username} (ID: {user.id})"
                    )

                    # Удаляем все связанные данные пользователя
                    try:
                        # Удаляем уведомления
                        notifications_count = Notification.query.filter_by(
                            user_id=user.id
                        ).count()
                        Notification.query.filter_by(user_id=user.id).delete()
                        current_app.logger.info(
                            f"Удалено уведомлений: {notifications_count}"
                        )

                        # Удаляем сообщения тикетов
                        ticket_messages_count = TicketMessage.query.filter_by(
                            user_id=user.id
                        ).count()
                        TicketMessage.query.filter_by(user_id=user.id).delete()
                        current_app.logger.info(
                            f"Удалено сообщений тикетов: {ticket_messages_count}"
                        )

                        # Удаляем тикеты пользователя
                        tickets_count = Ticket.query.filter_by(user_id=user.id).count()
                        Ticket.query.filter_by(user_id=user.id).delete()
                        current_app.logger.info(f"Удалено тикетов: {tickets_count}")

                        # Удаляем коды подтверждения email
                        email_verifications_count = EmailVerification.query.filter_by(
                            user_id=user.id
                        ).count()
                        EmailVerification.query.filter_by(user_id=user.id).delete()
                        current_app.logger.info(
                            f"Удалено кодов подтверждения email: {email_verifications_count}"
                        )

                        # Удаляем платежи
                        payments_count = Payment.query.filter_by(
                            user_id=user.id
                        ).count()
                        Payment.query.filter_by(user_id=user.id).delete()
                        current_app.logger.info(f"Удалено платежей: {payments_count}")

                        # Удаляем решения
                        submissions_count = db.session.query(db.Submission).filter_by(
                            user_id=user.id
                        ).count()
                        db.session.query(db.Submission).filter_by(user_id=user.id).delete()
                        current_app.logger.info(f"Удалено решений: {submissions_count}")

                        # Удаляем сообщения чата
                        chat_messages_count = ChatMessage.query.filter_by(
                            user_id=user.id
                        ).count()
                        ChatMessage.query.filter_by(user_id=user.id).delete()
                        current_app.logger.info(
                            f"Удалено сообщений чата: {chat_messages_count}"
                        )

                        # Удаляем файлы пользователя с использованием FileStorageManager
                        if FileStorageManager.delete_user_files(user.id):
                            current_app.logger.info(
                                f"Файлы пользователя {user.id} успешно удалены"
                            )
                        else:
                            current_app.logger.warning(
                                f"Ошибка при удалении файлов пользователя {user.id}"
                            )

                        # Удаляем файлы тикетов
                        for ticket in Ticket.query.filter_by(user_id=user.id).all():
                            if FileStorageManager.delete_ticket_files(ticket.id):
                                current_app.logger.info(
                                    f"Файлы тикета {ticket.id} успешно удалены"
                                )
                            else:
                                current_app.logger.warning(
                                    f"Ошибка при удалении файлов тикета {ticket.id}"
                                )

                        # Удаляем самого пользователя
                        db.session.delete(user)
                        db.session.commit()
                        current_app.logger.info(
                            f"Пользователь {username} успешно удален"
                        )
                        flash(f"Пользователь {username} удалён")

                    except Exception as e:
                        current_app.logger.error(
                            f"Ошибка при удалении связанных данных пользователя {username}: {str(e)}"
                        )
                        import traceback

                        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
                        db.session.rollback()
                        flash(f"Ошибка при удалении пользователя {username}", "error")
                        return redirect(url_for("admin.admin_users"))
            else:
                flash("Пользователь не найден", "error")
        except Exception as e:
            current_app.logger.error(f"Ошибка удаления пользователя: {str(e)}")
            db.session.rollback()  # Откатываем транзакцию при ошибке
            flash("Ошибка при удалении пользователя", "error")

    # Изменение статуса администратора
    if request.method == "POST" and request.form.get("toggle_admin_id"):
        try:
            user_id = int(request.form.get("toggle_admin_id"))
            user = User.query.get(user_id)
            if user:
                if user.id == current_user.id:
                    flash(
                        "Нельзя изменить статус администратора для самого себя", "error"
                    )
                else:
                    user.is_admin = not user.is_admin
                    status = (
                        "назначен администратором"
                        if user.is_admin
                        else "снят с администратора"
                    )
                    db.session.commit()
                    flash(f"Пользователь {user.username} {status}")
            else:
                flash("Пользователь не найден", "error")
        except Exception as e:
            current_app.logger.error(
                f"Ошибка изменения статуса администратора: {str(e)}"
            )
            db.session.rollback()  # Откатываем транзакцию при ошибке
            flash("Ошибка при изменении статуса администратора", "error")

    # Изменение группы пользователя
    if request.method == "POST" and request.form.get("change_group_user_id"):
        try:
            user_id = int(request.form.get("change_group_user_id"))
            new_group_id = request.form.get("new_group_id")
            user = User.query.get(user_id)
            
            if user:
                if new_group_id:
                    group = Group.query.get(int(new_group_id))
                    if group:
                        user.group_id = group.id
                        flash(f"Пользователь {user.username} перемещен в группу '{group.name}'")
                    else:
                        flash("Группа не найдена", "error")
                        return redirect(url_for("admin.admin_users"))
                else:
                    user.group_id = None
                    flash(f"Пользователь {user.username} убран из группы")
                
                db.session.commit()
            else:
                flash("Пользователь не найден", "error")
        except Exception as e:
            current_app.logger.error(f"Ошибка изменения группы пользователя: {str(e)}")
            db.session.rollback()
            flash("Ошибка при изменении группы пользователя", "error")

    # Выдача/отзыв подписки
    if request.method == "POST" and request.form.get("toggle_subscription_id"):
        try:
            user_id = int(request.form.get("toggle_subscription_id"))
            current_app.logger.info(
                f"Обрабатываем изменение подписки для пользователя ID: {user_id}"
            )
            user = User.query.get(user_id)
            if user:
                current_app.logger.info(
                    f"Пользователь найден: {user.username}, текущий статус подписки: {user.is_subscribed}"
                )
                if user.is_subscribed:
                    # Отзываем подписку
                    current_app.logger.info(
                        f"Отзываем подписку у пользователя {user.username}"
                    )
                    user.is_subscribed = False
                    user.subscription_expires = None
                    user.is_manual_subscription = (
                        False  # Сбрасываем флаг ручной подписки
                    )
                    status = "отозвана"
                else:
                    # Выдаем подписку на 30 дней
                    current_app.logger.info(
                        f"Выдаем подписку пользователю {user.username} на 30 дней"
                    )
                    user.is_subscribed = True
                    user.subscription_expires = datetime.utcnow() + timedelta(days=30)
                    user.is_manual_subscription = (
                        True  # Устанавливаем флаг ручной подписки
                    )
                    status = "выдана на 30 дней"

                db.session.commit()
                current_app.logger.info(
                    f"Подписка успешно изменена: {user.username} - {status}"
                )
                flash(f"Подписка для пользователя {user.username} {status}")
            else:
                current_app.logger.error(f"Пользователь с ID {user_id} не найден")
                flash("Пользователь не найден", "error")
        except Exception as e:
            current_app.logger.error(f"Ошибка изменения подписки: {str(e)}")
            import traceback

            current_app.logger.error(f"Traceback: {traceback.format_exc()}")
            db.session.rollback()  # Откатываем транзакцию при ошибке
            flash("Ошибка при изменении подписки", "error")

    # Функционал коротких ссылок удален

    # Получаем всех пользователей с информацией о подписке
    try:
        users = User.query.all()
    except Exception as e:
        current_app.logger.error(f"Error loading users: {e}")
        users = []
        flash("Ошибка загрузки пользователей.", "error")

    return render_template(
        "admin/users.html",
        users=users,
        form=form,
        password_map=password_map,
        message=message,
        groups=Group.query.all(),  # Добавляем группы для модальных окон
    )


@admin_bp.route("/admin/groups", methods=["GET", "POST"])
@login_required
def admin_groups() -> Union[str, Response]:
    """Админка для управления группами"""
    if not current_user.is_admin:
        flash("Доступ запрещён")
        return redirect(url_for("main.index"))

    # Проверяем CSRF токен для POST запросов
    if request.method == "POST":
        current_app.logger.info(f"POST запрос в admin_groups: {request.form}")
        current_app.logger.info(f"CSRF токен в запросе: {request.form.get('csrf_token', 'НЕ НАЙДЕН')}")
        
        # Проверяем, что CSRF токен присутствует
        if not request.form.get('csrf_token'):
            current_app.logger.error("CSRF токен отсутствует в запросе")
            flash("Ошибка безопасности: отсутствует CSRF токен", "error")
            return redirect(url_for("admin.admin_groups"))

    form = GroupForm()
    message = ""

    if request.method == "POST":
        # Создание новой группы
        if request.form.get("submit") == "Сохранить":
            if form.validate_on_submit():
                try:
                    # Проверяем уникальность названия группы
                    existing_group = Group.query.filter_by(name=form.name.data).first()
                    if existing_group:
                        flash(f'Группа с названием "{form.name.data}" уже существует', "error")
                    else:
                        group = Group(
                            name=form.name.data,
                            description=form.description.data,
                            is_active=form.is_active.data
                        )
                        db.session.add(group)
                        db.session.commit()
                        flash(f"Группа '{group.name}' успешно создана")
                        # Очищаем форму
                        form.name.data = ""
                        form.description.data = ""
                        form.is_active.data = True
                except Exception as e:
                    current_app.logger.error(f"Ошибка создания группы: {str(e)}")
                    db.session.rollback()
                    flash("Ошибка при создании группы", "error")

        # Редактирование группы (inline)
        elif request.form.get("action") == "edit":
            try:
                current_app.logger.info(f"Редактирование группы: {request.form}")
                group_id = int(request.form.get("group_id"))
                group = Group.query.get(group_id)
                if group:
                    current_app.logger.info(f"Обновляем группу: {group.name} (ID: {group_id})")
                    current_app.logger.info(f"Новые данные: name='{request.form.get('name')}', description='{request.form.get('description')}', is_active='{request.form.get('is_active')}'")
                    
                    group.name = request.form.get("name")
                    group.description = request.form.get("description")
                    
                    # Обновляем статус активности группы
                    is_active_value = request.form.get("is_active")
                    if is_active_value is not None:
                        group.is_active = bool(int(is_active_value))
                        current_app.logger.info(f"Статус активности обновлен: {group.is_active}")
                    
                    db.session.commit()
                    
                    # Возвращаем JSON ответ для AJAX
                    if request.headers.get('Accept') == 'application/json':
                        return jsonify({
                            'success': True,
                            'message': f"Группа '{group.name}' успешно обновлена"
                        })
                    else:
                        flash(f"Группа '{group.name}' успешно обновлена")
                else:
                    if request.headers.get('Accept') == 'application/json':
                        return jsonify({
                            'success': False,
                            'error': 'Группа не найдена'
                        }), 404
                    else:
                        flash("Группа не найдена", "error")
            except Exception as e:
                current_app.logger.error(f"Ошибка редактирования группы: {str(e)}")
                db.session.rollback()
                if request.headers.get('Accept') == 'application/json':
                    return jsonify({
                        'success': False,
                        'error': f'Ошибка при редактировании группы: {str(e)}'
                    }), 500
                else:
                    flash("Ошибка при редактировании группы", "error")

        # Удаление группы (inline)
        elif request.form.get("action") == "delete":
            current_app.logger.info(f"Получен запрос на удаление группы: {request.form}")
            try:
                group_id = int(request.form.get("group_id"))
                current_app.logger.info(f"Попытка удаления группы с ID: {group_id}")
                
                group = Group.query.get(group_id)
                if group:
                    current_app.logger.info(f"Группа найдена: {group.name}")
                    if group.users:
                        current_app.logger.warning(f"Попытка удаления группы '{group.name}' с пользователями: {len(group.users)}")
                        if request.headers.get('Accept') == 'application/json':
                            return jsonify({
                                'success': False,
                                'error': f"Нельзя удалить группу '{group.name}' - в ней есть пользователи"
                            }), 400
                        else:
                            flash(f"Нельзя удалить группу '{group.name}' - в ней есть пользователи", "error")
                    else:
                        current_app.logger.info(f"Удаляем группу '{group.name}' (ID: {group_id})")
                        db.session.delete(group)
                        db.session.commit()
                        current_app.logger.info(f"Группа '{group.name}' успешно удалена")
                        if request.headers.get('Accept') == 'application/json':
                            return jsonify({
                                'success': True,
                                'message': f"Группа '{group.name}' успешно удалена"
                            })
                        else:
                            flash(f"Группа '{group.name}' успешно удалена")
                else:
                    current_app.logger.error(f"Группа с ID {group_id} не найдена")
                    if request.headers.get('Accept') == 'application/json':
                        return jsonify({
                            'success': False,
                            'error': 'Группа не найдена'
                        }), 404
                    else:
                        flash("Группа не найдена", "error")
            except Exception as e:
                current_app.logger.error(f"Ошибка удаления группы: {str(e)}")
                current_app.logger.error(f"Traceback: {e.__traceback__}")
                db.session.rollback()
                if request.headers.get('Accept') == 'application/json':
                    return jsonify({
                        'success': False,
                        'error': f'Ошибка при удалении группы: {str(e)}'
                    }), 500
                else:
                    flash("Ошибка при удалении группы", "error")

    # Получаем все группы
    try:
        groups = Group.query.order_by(Group.name).all()
    except Exception as e:
        current_app.logger.error(f"Error loading groups: {e}")
        groups = []
        flash("Ошибка загрузки групп.", "error")

    return render_template(
        "admin/groups.html",
        groups=groups,
        form=form,
        message=message,
    )


@admin_bp.route("/admin/subject-groups", methods=["GET", "POST"])
@login_required
def admin_subject_groups() -> Union[str, Response]:
    """Админка для управления предметами по группам"""
    if not current_user.is_admin:
        flash("Доступ запрещён")
        return redirect(url_for("main.index"))

    # Получаем все предметы с их группами
    try:
        subjects = Subject.query.options(joinedload(Subject.groups)).order_by(Subject.title).all()
        groups = Group.query.filter_by(is_active=True).order_by(Group.name).all()
    except Exception as e:
        current_app.logger.error(f"Error loading subjects or groups: {e}")
        subjects = []
        groups = []
        flash("Ошибка загрузки предметов или групп.", "error")

    # Создаем форму после получения данных
    form = SubjectGroupForm()
    # Заполняем форму актуальными данными
    form.populate_choices(subjects, groups)
    message = ""

    if request.method == "POST":
        # Назначение предмета группам
        if request.form.get("submit") == "Сохранить":
            if form.validate_on_submit():
                try:
                    subject_id = form.subject_id.data
                    group_ids = form.group_ids.data
                    
                    # Удаляем существующие связи для этого предмета
                    SubjectGroup.query.filter_by(subject_id=subject_id).delete()
                    
                    # Создаем новые связи
                    for group_id in group_ids:
                        subject_group = SubjectGroup(
                            subject_id=subject_id,
                            group_id=group_id
                        )
                        db.session.add(subject_group)
                    
                    db.session.commit()
                    flash(f"Предмет успешно назначен группам")
                    
                    # Очищаем форму
                    form.subject_id.data = 0
                    form.group_ids.data = []
                except Exception as e:
                    current_app.logger.error(f"Ошибка назначения предмета группам: {str(e)}")
                    db.session.rollback()
                    flash("Ошибка при назначении предмета группам", "error")

        # Редактирование групп предмета
        elif request.form.get("edit_subject_id"):
            try:
                subject_id = int(request.form.get("edit_subject_id"))
                group_ids = request.form.getlist("edit_group_ids")
                
                # Удаляем существующие связи для этого предмета
                SubjectGroup.query.filter_by(subject_id=subject_id).delete()
                
                # Создаем новые связи
                for group_id in group_ids:
                    if group_id:  # Проверяем, что group_id не пустой
                        subject_group = SubjectGroup(
                            subject_id=subject_id,
                            group_id=int(group_id)
                        )
                        db.session.add(subject_group)
                
                db.session.commit()
                flash(f"Группы предмета успешно обновлены")
            except Exception as e:
                current_app.logger.error(f"Ошибка обновления групп предмета: {str(e)}")
                db.session.rollback()
                flash("Ошибка при обновлении групп предмета", "error")

        # Удаление всех связей предмета с группами
        elif request.form.get("remove_all_groups"):
            try:
                subject_id = int(request.form.get("remove_all_groups"))
                subject = Subject.query.get(subject_id)
                if subject:
                    SubjectGroup.query.filter_by(subject_id=subject_id).delete()
                    db.session.commit()
                    flash(f"Предмет '{subject.title}' убран из всех групп")
                else:
                    flash("Предмет не найден", "error")
            except Exception as e:
                current_app.logger.error(f"Ошибка удаления связей предмета с группами: {str(e)}")
                db.session.rollback()
                flash("Ошибка при удалении связей предмета с группами", "error")

    return render_template(
        "admin/subject_groups.html",
        subjects=subjects,
        groups=groups,
        form=form,
        message=message,
    )


@admin_bp.route("/admin/settings", methods=["GET", "POST"])
@login_required
def admin_settings() -> Union[str, Response]:
    """Админка для управления настройками сайта"""
    if not current_user.is_admin:
        flash("Доступ запрещён")
        return redirect(url_for("main.index"))

    form = SiteSettingsForm()
    
    # Загружаем текущие настройки
    if request.method == "GET":
        form.maintenance_mode.data = SiteSettings.get_setting('maintenance_mode', False)
        form.trial_subscription_enabled.data = SiteSettings.get_setting('trial_subscription_enabled', True)
    
    if request.method == "POST" and form.validate_on_submit():
        try:
            # Сохраняем настройки
            SiteSettings.set_setting('maintenance_mode', form.maintenance_mode.data, 'Включить/выключить режим технических работ')
            SiteSettings.set_setting('trial_subscription_enabled', form.trial_subscription_enabled.data, 'Включить/выключить пробную подписку для новых аккаунтов')
            
            flash('Настройки успешно сохранены', 'success')
            return redirect(url_for('admin.admin_settings'))
        except Exception as e:
            current_app.logger.error(f"Ошибка сохранения настроек: {str(e)}")
            flash('Ошибка при сохранении настроек', 'error')
    
    return render_template("admin/settings.html", form=form)
