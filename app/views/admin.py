from typing import Union

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
from sqlalchemy.orm import joinedload

from .. import db
from ..forms import (
    AdminUserForm,
    GroupForm,
    SiteSettingsForm,
    SubjectGroupForm,
)
from ..models import (
    Group,
    SiteSettings,
    Subject,
    SubjectGroup,
    User,
)
from ..services import UserManagementService, UserService
from ..utils.notifications import redirect_with_notification

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin/users", methods=["GET", "POST"])
@login_required
def admin_users():
    if not UserManagementService.is_effective_admin(current_user):
        return redirect_with_notification("main.index", "Доступ запрещён", "error")
    form = AdminUserForm()
    password_map = {}
    message = ""
    current_app.logger.info(f"Форма создана: {form}")
    current_app.logger.info(
        f"CSRF токен: {form.csrf_token.current_token if form.csrf_token else 'Нет токена'}"
    )
    current_app.logger.info(f"Метод запроса: {request.method}")
    current_app.logger.info(f"Данные формы: {request.form}")
    current_app.logger.info(f"Значение submit: {request.form.get('submit')}")
    if request.method == "POST":
        current_app.logger.info("POST запрос получен")
        if request.form.get("submit") == "Зарегистрироваться":
            current_app.logger.info("Найдена кнопка 'Зарегистрироваться'")
        else:
            current_app.logger.info(
                f"Кнопка не найдена. Доступные поля: {list(request.form.keys())}"
            )
    if request.method == "POST" and request.form.get("submit") == "Зарегистрироваться":
        if form.validate_on_submit():
            user, message_response = UserService.create_user(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data,
                is_admin=form.is_admin.data,
                is_moderator=form.is_moderator.data,
                group_id=form.group_id.data if form.group_id.data else None,
            )
            if user:
                password_map[user.id] = form.password.data
            message = message_response
    if request.method == "POST" and request.form.get("reset_user_id"):
        user_id = int(request.form.get("reset_user_id"))
        new_password, message = UserService.reset_user_password(user_id)
        if new_password:
            password_map[int(request.form.get("reset_user_id"))] = new_password
    if request.method == "POST" and request.form.get("delete_user_id"):
        user_id = int(request.form.get("delete_user_id"))
        success, message = UserService.delete_user(user_id, current_user.id)
        if success:
            return redirect_with_notification("admin.admin_users", message, "success")
        else:
            return redirect_with_notification("admin.admin_users", message, "error")
    if request.method == "POST" and request.form.get("toggle_admin_id"):
        user_id = int(request.form.get("toggle_admin_id"))
        success, message = UserService.toggle_admin_mode(user_id)
        if success:
            flash(message, "success")
        else:
            flash(message, "error")
    if request.method == "POST" and request.form.get("change_group_user_id"):
        user_id = int(request.form.get("change_group_user_id"))
        new_group_id = request.form.get("new_group_id")
        result, message = UserService.change_user_group(
            user_id=user_id,
            group_id=None,
            new_group_id=int(new_group_id) if new_group_id else None,
        )
        if result:
            flash(message, "success")
        else:
            flash(message, "error")
            return redirect(url_for("admin.admin_users"))
    if request.method == "POST" and request.form.get("change_status_user_id"):
        user_id = int(request.form.get("change_status_user_id"))
        new_role = request.form.get("new_role")
        admin_mode_enabled = request.form.get("admin_mode_enabled") == "on"
        success, message = UserService.change_user_status(
            user_id=user_id,
            current_user_id=current_user.id,
            new_role=new_role,
            admin_mode_enabled=admin_mode_enabled,
        )
        if success:
            flash(message, "success")
        else:
            flash(message, "error")
    if request.method == "POST" and request.form.get("action") == "mass_group":
        user_ids = request.form.getlist("user_ids")
        group_id = request.form.get("group_id")
        success, message = UserService.mass_change_group(
            user_ids=user_ids,
            group_id=int(group_id) if group_id else None,
            current_user_id=current_user.id,
        )
        if success:
            flash(message, "success")
        else:
            flash(message, "error")
            if "группа не найдена" in message.lower():
                return redirect(url_for("admin.admin_users"))
    if request.method == "POST" and request.form.get("action") == "mass_status":
        user_ids = request.form.getlist("user_ids")
        status = request.form.get("status")
        success, message = UserService.mass_change_status(
            user_ids=user_ids, new_role=status, current_user_id=current_user.id
        )
        if success:
            flash(message, "success")
        else:
            flash(message, "error")
    if request.method == "POST" and request.form.get("action") == "mass_delete":
        user_ids = request.form.getlist("user_ids")
        success, message = UserService.mass_delete_users(
            user_ids=user_ids, current_user_id=current_user.id
        )
        if success:
            flash(message, "success")
        else:
            flash(message, "error")
    if request.method == "POST" and request.form.get("edit_user_id"):
        user_id = int(request.form.get("edit_user_id"))
        new_username = request.form.get("new_username", "").strip()
        new_email = request.form.get("new_email", "").strip()
        success, message = UserService.update_user(
            user_id=user_id, username=new_username, email=new_email
        )
        if success:
            flash(message, "success")
        else:
            flash(message, "error")
            return redirect(url_for("admin.admin_users"))
    if request.method == "POST" and request.form.get("toggle_subscription_id"):
        user_id = int(request.form.get("toggle_subscription_id"))
        success, message = UserService.toggle_subscription(user_id)
        if success:
            flash(message, "success")
        else:
            flash(message, "error")
    try:
        users = User.query.all()
    except Exception as e:
        current_app.logger.error(f"Error loading users: {e}")
        users = []
        message = "Ошибка загрузки пользователей"
    if message and request.method == "POST":
        return redirect_with_notification(
            "admin.admin_users",
            message,
            (
                "info"
                if "успешно" in message.lower()
                or "назначен" in message.lower()
                or "удалён" in message.lower()
                or "сброшен" in message.lower()
                else "error"
            ),
        )
    return render_template(
        "admin/users.html",
        users=users,
        form=form,
        password_map=password_map,
        message=message,
        groups=Group.query.all(),
    )
    if not current_user.is_effective_admin():
        flash("Доступ запрещён")
        return redirect(url_for("main.index"))
    if request.method == "POST":
        current_app.logger.info(f"POST запрос в admin_groups: {request.form}")
        current_app.logger.info(
            f"CSRF токен в запросе: {request.form.get('csrf_token', 'НЕ НАЙДЕН')}"
        )
        if not request.form.get("csrf_token"):
            current_app.logger.error("CSRF токен отсутствует в запросе")
            flash("Ошибка безопасности: отсутствует CSRF токен", "error")
            return redirect(url_for("admin.admin_groups"))
    form = GroupForm()
    message = ""
    if request.method == "POST":
        if request.form.get("submit") == "Сохранить":
            form.process(request.form)
            if form.validate_on_submit():
                try:
                    existing_group = Group.query.filter_by(name=form.name.data).first()
                    if existing_group:
                        flash(
                            f'Группа с названием "{form.name.data}" уже существует',
                            "error",
                        )
                    else:
                        group = Group(
                            name=form.name.data,
                            description=form.description.data,
                            is_active=form.is_active.data,
                        )
                        db.session.add(group)
                        db.session.commit()
                        flash(f"Группа '{group.name}' успешно создана")
                        form.name.data = ""
                        form.description.data = ""
                        form.is_active.data = True
                except Exception as e:
                    current_app.logger.error(f"Ошибка создания группы: {str(e)}")
                    db.session.rollback()
                    flash("Ошибка при создании группы", "error")
        elif request.form.get("action") == "edit":
            try:
                current_app.logger.info(f"Редактирование группы: {request.form}")
                group_id = int(request.form.get("group_id"))
                group = Group.query.get(group_id)
                if group:
                    current_app.logger.info(f"Обновляем группу: {group.name} (ID: {group_id})")
                    current_app.logger.info(
                        f"Новые данные: name='{request.form.get('name')}', description='{request.form.get('description')}', is_active='{request.form.get('is_active')}'"
                    )
                    group.name = request.form.get("name")
                    group.description = request.form.get("description")
                    is_active_value = request.form.get("is_active")
                    if is_active_value is not None:
                        group.is_active = bool(int(is_active_value))
                        current_app.logger.info(f"Статус активности обновлен: {group.is_active}")
                    db.session.commit()
                    if request.headers.get("Accept") == "application/json":
                        return jsonify(
                            {
                                "success": True,
                                "message": f"Группа '{group.name}' успешно обновлена",
                            }
                        )
                    else:
                        flash(f"Группа '{group.name}' успешно обновлена")
                else:
                    if request.headers.get("Accept") == "application/json":
                        return (
                            jsonify(
                                {
                                    "success": False,
                                    "error": "Группа не найдена",
                                }
                            ),
                            404,
                        )
                    else:
                        flash("Группа не найдена", "error")
            except Exception as e:
                current_app.logger.error(f"Ошибка редактирования группы: {str(e)}")
                db.session.rollback()
                if request.headers.get("Accept") == "application/json":
                    return (
                        jsonify(
                            {
                                "success": False,
                                "error": f"Ошибка при редактировании группы: {str(e)}",
                            }
                        ),
                        500,
                    )
                else:
                    flash("Ошибка при редактировании группы", "error")
        elif request.form.get("action") == "delete":
            current_app.logger.info(f"Получен запрос на удаление группы: {request.form}")
            try:
                group_id = int(request.form.get("group_id"))
                current_app.logger.info(f"Попытка удаления группы с ID: {group_id}")
                group = Group.query.get(group_id)
                if group:
                    current_app.logger.info(f"Группа найдена: {group.name}")
                    if group.users:
                        current_app.logger.warning(
                            f"Попытка удаления группы '{group.name}' с пользователями: {len(group.users)}"
                        )
                        if request.headers.get("Accept") == "application/json":
                            return (
                                jsonify(
                                    {
                                        "success": False,
                                        "error": f"Нельзя удалить группу '{group.name}' - в ней есть пользователи",
                                    }
                                ),
                                400,
                            )
                        else:
                            flash(
                                f"Нельзя удалить группу '{group.name}' - в ней есть пользователи",
                                "error",
                            )
                    else:
                        current_app.logger.info(f"Удаляем группу '{group.name}' (ID: {group_id})")
                        db.session.delete(group)
                        db.session.commit()
                        current_app.logger.info(f"Группа '{group.name}' успешно удалена")
                        if request.headers.get("Accept") == "application/json":
                            return jsonify(
                                {
                                    "success": True,
                                    "message": f"Группа '{group.name}' успешно удалена",
                                }
                            )
                        else:
                            flash(f"Группа '{group.name}' успешно удалена")
                else:
                    current_app.logger.error(f"Группа с ID {group_id} не найдена")
                    if request.headers.get("Accept") == "application/json":
                        return (
                            jsonify(
                                {
                                    "success": False,
                                    "error": "Группа не найдена",
                                }
                            ),
                            404,
                        )
                    else:
                        flash("Группа не найдена", "error")
            except Exception as e:
                current_app.logger.error(f"Ошибка удаления группы: {str(e)}")
                current_app.logger.error(f"Traceback: {e.__traceback__}")
                db.session.rollback()
                if request.headers.get("Accept") == "application/json":
                    return (
                        jsonify(
                            {
                                "success": False,
                                "error": f"Ошибка при удалении группы: {str(e)}",
                            }
                        ),
                        500,
                    )
                else:
                    flash("Ошибка при удалении группы", "error")
        elif request.form.get("action") == "mass_delete":
            try:
                group_ids = request.form.getlist("group_ids")
                current_app.logger.info(f"Массовое удаление групп: {group_ids}")
                if not group_ids:
                    flash("Не выбраны группы", "error")
                else:
                    deleted_count = 0
                    skipped_count = 0
                    for group_id in group_ids:
                        group = Group.query.get(int(group_id))
                        if group:
                            if group.users:
                                current_app.logger.warning(
                                    f"Пропускаем группу '{group.name}' - в ней есть пользователи"
                                )
                                skipped_count += 1
                            else:
                                current_app.logger.info(
                                    f"Удаляем группу '{group.name}' (ID: {group_id})"
                                )
                                db.session.delete(group)
                                deleted_count += 1
                    db.session.commit()
                    if deleted_count > 0:
                        flash(f"Удалено {deleted_count} групп")
                    if skipped_count > 0:
                        flash(
                            f"Пропущено {skipped_count} групп (в них есть пользователи)",
                            "warning",
                        )
            except Exception as e:
                current_app.logger.error(f"Ошибка массового удаления групп: {str(e)}")
                db.session.rollback()
                flash("Ошибка при массовом удалении групп", "error")
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
    if not current_user.is_effective_admin():
        flash("Доступ запрещён")
        return redirect(url_for("main.index"))
    try:
        subjects = Subject.query.options(joinedload(Subject.groups)).order_by(Subject.title).all()
        groups = Group.query.filter_by(is_active=True).order_by(Group.name).all()
    except Exception as e:
        current_app.logger.error(f"Error loading subjects or groups: {e}")
        subjects = []
        groups = []
        flash("Ошибка загрузки предметов или групп.", "error")
    form = SubjectGroupForm()
    form.populate_choices(subjects, groups)
    message = ""
    if request.method == "POST":
        if request.form.get("submit") == "Сохранить":
            if form.validate_on_submit():
                try:
                    subject_id = form.subject_id.data
                    group_ids = form.group_ids.data
                    SubjectGroup.query.filter_by(subject_id=subject_id).delete()
                    for group_id in group_ids:
                        subject_group = SubjectGroup(subject_id=subject_id, group_id=group_id)
                        db.session.add(subject_group)
                    db.session.commit()
                    flash("Предмет успешно назначен группам")
                    form.subject_id.data = 0
                    form.group_ids.data = []
                except Exception as e:
                    current_app.logger.error(f"Ошибка назначения предмета группам: {str(e)}")
                    db.session.rollback()
                    flash("Ошибка при назначении предмета группам", "error")
        elif request.form.get("edit_subject_id"):
            try:
                subject_id = int(request.form.get("edit_subject_id"))
                group_ids = request.form.getlist("edit_group_ids")
                SubjectGroup.query.filter_by(subject_id=subject_id).delete()
                for group_id in group_ids:
                    if group_id:
                        subject_group = SubjectGroup(subject_id=subject_id, group_id=int(group_id))
                        db.session.add(subject_group)
                db.session.commit()
                flash("Группы предмета успешно обновлены")
            except Exception as e:
                current_app.logger.error(f"Ошибка обновления групп предмета: {str(e)}")
                db.session.rollback()
                flash("Ошибка при обновлении групп предмета", "error")
        elif request.form.get("action") == "mass_assign":
            try:
                subject_ids = request.form.getlist("subject_ids")
                group_ids = request.form.getlist("group_ids")
                if not subject_ids or not group_ids:
                    flash("Выберите предметы и группы", "error")
                else:
                    for subject_id in subject_ids:
                        subject_id = int(subject_id)
                        SubjectGroup.query.filter_by(subject_id=subject_id).delete()
                        for group_id in group_ids:
                            if group_id:
                                subject_group = SubjectGroup(
                                    subject_id=subject_id,
                                    group_id=int(group_id),
                                )
                                db.session.add(subject_group)
                    db.session.commit()
                    flash(f"Успешно назначено {len(subject_ids)} предметов группам")
            except Exception as e:
                current_app.logger.error(f"Ошибка массового назначения предметов группам: {str(e)}")
                db.session.rollback()
                flash("Ошибка при массовом назначении предметов группам", "error")
        elif request.form.get("action") == "mass_remove":
            try:
                subject_ids = request.form.getlist("subject_ids")
                if not subject_ids:
                    flash("Выберите предметы для удаления из групп", "error")
                else:
                    for subject_id in subject_ids:
                        subject_id = int(subject_id)
                        SubjectGroup.query.filter_by(subject_id=subject_id).delete()
                    db.session.commit()
                    flash(f"Успешно убрано {len(subject_ids)} предметов из всех групп")
            except Exception as e:
                current_app.logger.error(f"Ошибка массового удаления предметов из групп: {str(e)}")
                db.session.rollback()
                flash("Ошибка при массовом удалении предметов из групп", "error")
        elif request.form.get("action") == "mass_delete_subjects":
            try:
                subject_ids = request.form.getlist("subject_ids")
                if not subject_ids:
                    flash("Выберите предметы для удаления", "error")
                else:
                    deleted_count = 0
                    for subject_id in subject_ids:
                        subject_id = int(subject_id)
                        subject = Subject.query.get(subject_id)
                        if subject:
                            db.session.delete(subject)
                            deleted_count += 1
                    db.session.commit()
                    flash(f"Успешно удалено {deleted_count} предметов")
            except Exception as e:
                current_app.logger.error(f"Ошибка массового удаления предметов: {str(e)}")
                db.session.rollback()
                flash("Ошибка при массовом удалении предметов", "error")
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
    if not current_user.is_effective_admin():
        flash("Доступ запрещён")
        return redirect(url_for("main.index"))
    form = SiteSettingsForm()
    if request.method == "GET":
        form.maintenance_mode.data = SiteSettings.get_setting("maintenance_mode", False)
        form.trial_subscription_enabled.data = SiteSettings.get_setting(
            "trial_subscription_enabled", True
        )
        form.trial_subscription_days.data = SiteSettings.get_setting("trial_subscription_days", 14)
        form.pattern_generation_enabled.data = SiteSettings.get_setting(
            "pattern_generation_enabled", True
        )
        form.support_enabled.data = SiteSettings.get_setting("support_enabled", True)
        form.telegram_only_registration.data = SiteSettings.get_setting(
            "telegram_only_registration", False
        )
    if request.method == "POST" and form.validate_on_submit():
        try:
            SiteSettings.set_setting(
                "maintenance_mode",
                form.maintenance_mode.data,
                "Включить/выключить режим технических работ",
            )
            SiteSettings.set_setting(
                "trial_subscription_enabled",
                form.trial_subscription_enabled.data,
                "Включить/выключить пробную подписку для новых аккаунтов",
            )
            SiteSettings.set_setting(
                "trial_subscription_days",
                form.trial_subscription_days.data,
                "Количество дней пробной подписки",
            )
            SiteSettings.set_setting(
                "pattern_generation_enabled",
                form.pattern_generation_enabled.data,
                "Включить/выключить кнопку генерации паттернов",
            )
            SiteSettings.set_setting(
                "support_enabled",
                form.support_enabled.data,
                "Включить/выключить систему тикетов и поддержки",
            )
            SiteSettings.set_setting(
                "telegram_only_registration",
                form.telegram_only_registration.data,
                "Включить/выключить регистрацию только через Telegram",
            )
            flash("Настройки успешно сохранены", "success")
            return redirect(url_for("admin.admin_settings"))
        except Exception as e:
            current_app.logger.error(f"Ошибка сохранения настроек: {str(e)}")
            flash("Ошибка при сохранении настроек", "error")
    return render_template("admin/settings.html", form=form)
