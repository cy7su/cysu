import os
import shutil
from typing import Union

from flask import (
    Blueprint,
    Response,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)
from flask_login import current_user, login_required
from markupsafe import escape
from sqlalchemy.orm import joinedload
from werkzeug.utils import secure_filename

from ..forms import MaterialForm
from ..models import Material, SiteSettings, Subject, SubjectGroup, db
from ..services import (
    ExportService,
    MaterialService,
    SubjectService,
    UserManagementService,
)
from ..utils.file_storage import FileStorageManager
from ..utils.notifications import redirect_with_notification
from ..utils.payment_service import YooKassaService
from ..utils.transliteration import get_safe_filename
from .context_processors import (
    inject_admin_users,
    inject_json_parser,
    inject_moment,
    inject_subscription_status,
    inject_timestamp,
)

main_bp = Blueprint("main", __name__)
main_bp.app_context_processor(inject_json_parser)
main_bp.app_context_processor(inject_timestamp)
main_bp.app_context_processor(inject_moment)
main_bp.app_context_processor(inject_admin_users)
main_bp.app_context_processor(inject_subscription_status)


@main_bp.route("/", methods=["GET", "POST"])
def index() -> Union[str, Response]:
    is_subscribed = False
    if current_user.is_authenticated:
        try:
            payment_service = YooKassaService()
            is_subscribed = payment_service.check_user_subscription(current_user)
        except Exception as e:
            current_app.logger.error(f"Error checking subscription in index: {e}")
            is_subscribed = False
        if (
            current_user.is_admin
            and request.method == "POST"
            and request.form.get("title")
        ):
            try:
                pattern_type = request.form.get("pattern_type", "dots")
                pattern_svg = request.form.get("pattern_svg", "")
                if not pattern_svg:
                    pattern_svg = "default_dots"
                SubjectService.create_subject(
                    title=request.form.get("title"),
                    description=request.form.get("description", ""),
                    pattern_type=pattern_type,
                    pattern_svg=pattern_svg,
                    created_by=current_user.id,
                    upload_path=current_app.config.get(
                        "UPLOAD_FOLDER", "app/static/uploads"
                    ),
                )
                return redirect_with_notification(
                    "main.index", "Предмет добавлен", "success"
                )
            except Exception as e:
                current_app.logger.error(f"Error creating subject: {e}")
                return redirect_with_notification(
                    "main.index", "Ошибка при создании предмета", "error"
                )
    try:
        if current_user.is_authenticated:
            accessible_subjects = UserManagementService.get_accessible_subjects(
                current_user
            )
            current_app.logger.info(
                f"User {current_user.username} has access to {len(accessible_subjects)} subjects"
            )
            if accessible_subjects:
                subject_ids = [s.id for s in accessible_subjects]
                subjects = (
                    Subject.query.options(
                        joinedload(Subject.materials), joinedload(Subject.groups)
                    )
                    .filter(Subject.id.in_(subject_ids))
                    .all()
                )
                current_app.logger.info(
                    f"Loaded {len(subjects)} subjects for authenticated user"
                )
            else:
                subjects = []
                current_app.logger.warning(
                    f"No accessible subjects found for user {current_user.username} (group_id: {current_user.group_id})"
                )
        else:
            subjects = Subject.query.options(
                joinedload(Subject.materials), joinedload(Subject.groups)
            ).all()
            current_app.logger.info(
                f"Loaded {len(subjects)} subjects for unauthenticated user"
            )
    except Exception as e:
        current_app.logger.error(f"Error querying subjects: {e}")
        subjects = []
    pattern_generation_enabled = SiteSettings.get_setting(
        "pattern_generation_enabled", True
    )
    return render_template(
        "index.html",
        subjects=subjects,
        is_subscribed=is_subscribed,
        pattern_generation_enabled=pattern_generation_enabled,
    )


@main_bp.route("/profile")
@login_required
def profile() -> str:
    try:
        payment_service = YooKassaService()
        is_subscribed = payment_service.check_user_subscription(current_user)
        subscription_type = "none"
        subscription_expires = None
        if current_user.is_trial_subscription:
            subscription_type = "trial"
            subscription_expires = current_user.trial_subscription_expires
        elif current_user.is_subscribed:
            subscription_type = "active"
            subscription_expires = current_user.subscription_expires
    except Exception as e:
        current_app.logger.error(f"Error checking subscription in profile: {e}")
        is_subscribed = False
        subscription_type = "none"
        subscription_expires = None
        flash("Ошибка проверки подписки.", "error")
    return render_template(
        "profile.html",
        user=current_user,
        is_subscribed=is_subscribed,
        subscription_type=subscription_type,
        subscription_expires=subscription_expires,
    )


@main_bp.route("/subject/<int:subject_id>", methods=["GET", "POST"])
def subject_detail(subject_id: int) -> Union[str, Response]:
    if request.method == "POST":
        pass
    try:
        subject = Subject.query.get_or_404(subject_id)
    except Exception as e:
        current_app.logger.error(f"Error loading subject {subject_id}: {e}")
        return redirect_with_notification(
            "main.index", "Ошибка загрузки предмета", "error"
        )
    if current_user.is_authenticated:
        accessible_subjects = UserManagementService.get_accessible_subjects(
            current_user
        )
        if subject not in accessible_subjects:
            return redirect_with_notification(
                "main.index", "У вас нет доступа к этому предмету", "error"
            )
    if current_user.is_authenticated:
        try:
            payment_service = YooKassaService()
            if not payment_service.check_user_subscription(current_user):
                return redirect_with_notification(
                    "payment.subscription",
                    "Для доступа к предметам необходима активная подписка",
                    "warning",
                )
            if not UserManagementService.is_effective_admin(current_user):
                if current_user.group:
                    subject_group = SubjectGroup.query.filter_by(
                        subject_id=subject.id, group_id=current_user.group.id
                    ).first()
                    if not subject_group:
                        return redirect_with_notification(
                            "main.index", "У вас нет доступа к этому предмету", "error"
                        )
                else:
                    return redirect_with_notification(
                        "main.index",
                        "У вас не назначена группа. Обратитесь к администратору",
                        "error",
                    )
        except Exception as e:
            current_app.logger.error(
                f"Error checking subscription in subject_detail: {e}"
            )
            return redirect_with_notification(
                "main.index", "Ошибка проверки подписки", "error"
            )
    lectures, assignments = MaterialService.get_subject_materials(subject.id)
    form = None
    user_submissions = {}
    if current_user.is_authenticated:
        try:
            for material in assignments:
                for sub in material.submissions:
                    if str(sub.user_id) == str(current_user.id) and sub.file:
                        user_submissions[material.id] = sub
                        break
        except Exception as e:
            current_app.logger.error(f"Error loading user submissions: {e}")
            user_submissions = {}
    form = None
    if (
        current_user.is_authenticated
        and UserManagementService.can_add_materials_to_subject(current_user, subject)
    ):
        form = MaterialForm()
        form.subject_id.choices = [(subject.id, subject.title)]
        form.subject_id.data = subject.id
        if form and form.validate_on_submit():
            material = MaterialService.create_material(
                subject_id=subject_id,
                title=form.title.data,
                description=form.description.data,
                material_type=form.type.data,
                file_data=form.file.data,
                solution_file_data=(
                    form.solution_file.data if form.type.data == "assignment" else None
                ),
                created_by=current_user.id,
            )
            flash("Материал добавлен")
            return redirect(url_for("main.subject_detail", subject_id=subject_id))
    can_add_materials = False
    can_manage_materials = False
    if current_user.is_authenticated:
        can_add_materials = UserManagementService.can_add_materials_to_subject(
            current_user, subject
        )
        can_manage_materials = UserManagementService.can_manage_subject_materials(
            current_user, subject
        )
    assignments_completion_percent = 0
    if current_user.is_authenticated and assignments:
        completed_count = len(user_submissions)
        total_count = len(assignments)
        assignments_completion_percent = (
            round((completed_count / total_count) * 100) if total_count > 0 else 0
        )
    upload_limit_message = FileStorageManager.get_user_limit_message(
        current_user if current_user.is_authenticated else None
    )
    upload_max_size_bytes = FileStorageManager.get_user_max_file_size_bytes(
        current_user if current_user.is_authenticated else None
    )
    return render_template(
        "subjects/subject_detail.html",
        subject=subject,
        lectures=lectures,
        assignments=assignments,
        form=form if can_add_materials else None,
        user_submissions=user_submissions,
        can_add_materials=can_add_materials,
        can_manage_materials=can_manage_materials,
        assignments_completion_percent=assignments_completion_percent,
        upload_limit_message=upload_limit_message,
        upload_max_size_bytes=upload_max_size_bytes,
    )


@main_bp.route("/subject/<int:subject_id>/edit", methods=["POST"])
@login_required
def edit_subject(subject_id: int) -> Response:
    if not UserManagementService.is_effective_admin(current_user):
        flash("Доступ запрещён")
        return redirect(url_for("main.index"))
    new_title = request.form.get("title", "").strip()
    new_description = request.form.get("description", "").strip()
    if SubjectService.update_subject(subject_id, new_title, new_description):
        flash("Предмет успешно обновлён")
    else:
        flash("Ошибка при обновлении предмета", "error")
    return redirect(url_for("main.subject_detail", subject_id=subject_id))


@main_bp.route("/subject/<int:subject_id>/delete", methods=["POST"])
@login_required
def delete_subject(subject_id: int) -> Response:
    if not UserManagementService.is_effective_admin(current_user):
        flash("Доступ запрещён")
        return redirect(url_for("main.index"))
    subject = Subject.query.get_or_404(subject_id)
    try:
        upload_base = current_app.config.get("UPLOAD_FOLDER", "app/static/uploads")
        subject_path = os.path.join(upload_base, str(subject.id))
        if os.path.exists(subject_path):
            shutil.rmtree(subject_path)
    except Exception as folder_error:
        current_app.logger.error(
            f"Ошибка удаления папки предмета {subject.id}: {folder_error}"
        )
    for material in subject.materials:
        db.session.delete(material)
    db.session.delete(subject)
    db.session.commit()
    flash("Предмет удалён")
    return redirect(url_for("main.index"))


@main_bp.route("/material/<int:material_id>")
@login_required
def material_detail(material_id: int) -> Union[str, Response]:
    material = Material.query.get_or_404(material_id)
    payment_service = YooKassaService()
    if not payment_service.check_user_subscription(current_user):
        flash("Для доступа к материалам необходима активная подписка.", "warning")
        return redirect(url_for("payment.subscription"))
    user_submissions = {}
    total_submissions = 0
    if material.type == "assignment" and current_user.is_authenticated:
        from app.models import Submission

        submission = Submission.query.filter_by(
            user_id=current_user.id, material_id=material_id
        ).first()
        if submission:
            user_submissions[material_id] = submission
        total_submissions = Submission.query.filter_by(material_id=material_id).count()
    created_by_user = None
    if material.created_by:
        from app.models import User

        created_by_user = User.query.get(material.created_by)
    import os

    file_info = None
    if material.file:
        try:
            file_path = os.path.join(
                current_app.config["UPLOAD_FOLDER"],
                str(material.subject_id),
                material.file.split("/")[-1],
            )
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                file_ext = os.path.splitext(material.file)[1].upper().replace(".", "")
                file_info = {
                    "size": file_size,
                    "size_formatted": (
                        f"{file_size / 1024:.1f} КБ"
                        if file_size < 1024 * 1024
                        else f"{file_size / (1024 * 1024):.1f} МБ"
                    ),
                    "extension": file_ext,
                }
        except Exception as e:
            current_app.logger.error(f"Error getting file info: {e}")
    share_url = get_share_url(material) if material.solution_file else None
    return render_template(
        "subjects/material_detail.html",
        material=material,
        user_submissions=user_submissions,
        total_submissions=total_submissions,
        created_by_user=created_by_user,
        file_info=file_info,
        share_url=share_url,
    )


@main_bp.route("/submission/<int:submission_id>/delete", methods=["POST"])
@login_required
def delete_solution(submission_id: int) -> Response:
    from app.models import Submission
    from app.utils.file_storage import FileStorageManager

    submission = Submission.query.get_or_404(submission_id)
    if submission.user_id != current_user.id:
        flash("Доступ запрещён", "error")
        return redirect(url_for("main.index"))
    if submission.file:
        try:
            FileStorageManager.delete_file(submission.file)
        except Exception as e:
            current_app.logger.error(
                f"Ошибка при удалении файла {submission.file}: {e}"
            )
    db.session.delete(submission)
    db.session.commit()
    flash("Решение удалено", "success")
    return redirect(url_for("main.material_detail", material_id=submission.material_id))


@main_bp.route("/material/<int:material_id>/add_solution", methods=["POST"])
@login_required
def add_solution_file(material_id: int) -> Response:
    if not UserManagementService.can_manage_materials(current_user):
        flash("Доступ запрещён")
        return redirect(url_for("main.index"))
    material = Material.query.get_or_404(material_id)
    if current_user.is_moderator:
        accessible_subjects = UserManagementService.get_accessible_subjects(
            current_user
        )
        if material.subject not in accessible_subjects:
            flash("У вас нет доступа к этому предмету.", "error")
            return redirect(url_for("main.index"))
    file = request.files.get("solution_file")
    if file:
        subject = material.subject
        original_filename = get_safe_filename(file.filename)
        file_size = (
            getattr(file, "content_length", None) or len(file.read())
            if hasattr(file, "read")
            else "unknown"
        )
        if hasattr(file, "seek"):
            file.seek(0)
        if isinstance(file_size, int) and current_app.config.get("MAX_CONTENT_LENGTH"):
            if file_size > current_app.config.get("MAX_CONTENT_LENGTH"):
                current_app.logger.error(
                    f"Файл готового решения слишком большой: {file_size} байт > {current_app.config.get('MAX_CONTENT_LENGTH')} байт"
                )
                flash(
                    f"Файл слишком большой. Максимальный размер: {current_app.config.get('MAX_CONTENT_LENGTH', 0) / (1024 * 1024):.1f} MB",
                    "error",
                )
                return redirect(
                    url_for("main.subject_detail", subject_id=material.subject_id)
                )
        full_path, relative_path = FileStorageManager.get_material_upload_path(
            subject.id, original_filename
        )
        try:
            if FileStorageManager.save_file(file, full_path):
                material.solution_file = relative_path
                db.session.commit()
                flash("Готовая практика добавлена")
            else:
                current_app.logger.error(
                    f"Ошибка сохранения готового решения: {original_filename}"
                )
                flash("Ошибка при сохранении файла", "error")
        except Exception as e:
            current_app.logger.error(
                f"Исключение при сохранении готового решения {original_filename}: {str(e)}"
            )
            flash(f"Ошибка при сохранении файла: {str(e)}", "error")
    return redirect(url_for("main.subject_detail", subject_id=material.subject_id))


@main_bp.route("/material/<int:material_id>/submit_solution", methods=["POST"])
@login_required
def submit_solution(material_id: int) -> Response:
    material = Material.query.get_or_404(material_id)
    payment_service = YooKassaService()
    if not payment_service.check_user_subscription(current_user):
        flash("Для загрузки решений необходима активная подписка.", "warning")
        return redirect(url_for("payment.subscription"))
    if material.type != "assignment":
        flash("Можно загружать решение только для практик")
        return redirect(url_for("main.subject_detail", subject_id=material.subject_id))
    file = request.files.get("solution_file")
    if file:
        subject = material.subject
        original_filename = get_safe_filename(file.filename)
        file_size = (
            getattr(file, "content_length", None) or len(file.read())
            if hasattr(file, "read")
            else "unknown"
        )
        if hasattr(file, "seek"):
            file.seek(0)
        if isinstance(file_size, int) and current_app.config.get("MAX_CONTENT_LENGTH"):
            if file_size > current_app.config.get("MAX_CONTENT_LENGTH"):
                current_app.logger.error(
                    f"Файл решения пользователя слишком большой: {file_size} байт > {current_app.config.get('MAX_CONTENT_LENGTH')} байт"
                )
                flash(
                    f"Файл слишком большой. Максимальный размер: {current_app.config.get('MAX_CONTENT_LENGTH', 0) / (1024 * 1024):.1f} MB",
                    "error",
                )
                return redirect(
                    url_for("main.subject_detail", subject_id=material.subject_id)
                )
        full_path, relative_path = FileStorageManager.get_subject_upload_path(
            subject.id, current_user.id, original_filename
        )
        try:
            if FileStorageManager.save_file(file, full_path):
                from ..models import Submission

                submission = Submission.query.filter_by(
                    user_id=current_user.id, material_id=material.id
                ).first()
                if not submission:
                    submission = Submission(
                        user_id=current_user.id, material_id=material.id
                    )
                    db.session.add(submission)
                submission.file = relative_path
                db.session.commit()
                flash("Решение загружено")
            else:
                current_app.logger.error(
                    f"Ошибка сохранения решения пользователя {current_user.id}: {original_filename}"
                )
                flash("Ошибка при сохранении файла решения", "error")
        except Exception as e:
            current_app.logger.error(
                f"Исключение при сохранении решения пользователя {current_user.id} {original_filename}: {str(e)}"
            )
            flash(f"Ошибка при сохранении файла: {str(e)}", "error")
    return redirect(url_for("main.subject_detail", subject_id=material.subject_id))


@main_bp.route("/toggle-admin-mode", methods=["POST"])
@login_required
def toggle_admin_mode() -> Response:
    if not UserManagementService.toggle_admin_mode(current_user):
        flash("Доступ запрещён")
        return redirect(url_for("main.index"))
    mode = "админ" if current_user.admin_mode_enabled else "пользователь"
    flash(f"Переключен в режим {mode}")
    return redirect(request.referrer or url_for("main.index"))


@main_bp.route("/material/<int:material_id>/edit", methods=["POST"])
@login_required
def edit_material(material_id: int) -> Response:
    if not UserManagementService.can_manage_materials(current_user):
        flash("Доступ запрещён")
        return redirect(url_for("main.index"))
    new_title = request.form.get("title", "").strip()
    new_description = request.form.get("description", "").strip()
    if MaterialService.update_material(material_id, new_title, new_description):
        flash("Материал успешно обновлён")
    else:
        flash("Ошибка при обновлении материала", "error")
    return redirect(url_for("main.material_detail", material_id=material_id))


@main_bp.route("/material/<int:material_id>/replace_file", methods=["POST"])
@login_required
def replace_material_file(material_id: int) -> Response:
    if not UserManagementService.can_manage_materials(current_user):
        flash("Доступ запрещён", "error")
        return redirect(url_for("main.index"))
    material = Material.query.get_or_404(material_id)
    if current_user.is_moderator:
        accessible_subjects = UserManagementService.get_accessible_subjects(
            current_user
        )
        if material.subject not in accessible_subjects:
            flash("У вас нет доступа к этому предмету.", "error")
            return redirect(url_for("main.index"))
    file = request.files.get("file")
    if not file or not file.filename:
        flash("Файл не выбран", "error")
        return redirect(url_for("main.material_detail", material_id=material.id))
    if MaterialService.replace_material_file(material, file):
        flash("Файл материала успешно заменён", "success")
    else:
        flash("Ошибка при замене файла", "error")
    return redirect(url_for("main.material_detail", material_id=material.id))


@main_bp.route("/material/<int:material_id>/replace_solution_file", methods=["POST"])
@login_required
def replace_material_solution_file(material_id: int) -> Response:
    if not UserManagementService.can_manage_materials(current_user):
        flash("Доступ запрещён", "error")
        return redirect(url_for("main.index"))
    material = Material.query.get_or_404(material_id)
    if material.type != "assignment":
        flash("Файл решения можно заменить только для практик", "error")
        return redirect(url_for("main.material_detail", material_id=material.id))
    if current_user.is_moderator:
        accessible_subjects = UserManagementService.get_accessible_subjects(
            current_user
        )
        if material.subject not in accessible_subjects:
            flash("У вас нет доступа к этому предмету.", "error")
            return redirect(url_for("main.index"))
    file = request.files.get("solution_file")
    if not file or not file.filename:
        flash("Файл не выбран", "error")
        return redirect(url_for("main.material_detail", material_id=material.id))
    if MaterialService.replace_material_solution_file(material, file):
        flash("Файл решения успешно заменён", "success")
    else:
        flash("Ошибка при замене файла решения", "error")
    return redirect(url_for("main.material_detail", material_id=material.id))


@main_bp.route("/material/<int:material_id>/delete", methods=["POST"])
@login_required
def delete_material(material_id: int) -> Response:
    if not UserManagementService.can_manage_materials(current_user):
        flash("Доступ запрещён")
        return redirect(url_for("main.index"))
    material = Material.query.get_or_404(material_id)
    subject_id = material.subject_id
    if current_user.is_moderator:
        accessible_subjects = UserManagementService.get_accessible_subjects(
            current_user
        )
        if material.subject not in accessible_subjects:
            flash("У вас нет доступа к этому предмету.", "error")
            return redirect(url_for("main.index"))
    if material.file:
        try:
            upload_base = current_app.config.get("UPLOAD_FOLDER", "app/static/uploads")
            file_path = os.path.join(upload_base, material.file)
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as file_error:
            current_app.logger.error(
                f"Ошибка удаления файла материала {material.file}: {file_error}"
            )
    if material.solution_file:
        try:
            upload_base = current_app.config.get("UPLOAD_FOLDER", "app/static/uploads")
            solution_path = os.path.join(upload_base, material.solution_file)
            if os.path.exists(solution_path):
                os.remove(solution_path)
        except Exception as solution_error:
            current_app.logger.error(
                f"Ошибка удаления файла решения {material.solution_file}: {solution_error}"
            )
    db.session.delete(material)
    db.session.commit()
    flash("Материал удалён")
    return redirect(url_for("main.subject_detail", subject_id=subject_id))


@main_bp.route("/privacy")
def privacy() -> str:
    return render_template("static/privacy.html")


@main_bp.route("/terms")
def terms() -> str:
    return render_template("static/terms.html")


@main_bp.route("/security-policy")
def security_policy() -> str:
    return render_template("static/security_policy.html")


@main_bp.route("/.well-known/security.txt")
def security_txt() -> Response:
    """Возвращает файл security.txt для исследователей безопасности"""
    return Response(
        """Contact: mailto:support@cysu.ru
            Expires: 2026-01-15T00:00:00.000Z
            Preferred-Languages: ru, en
            Canonical: https://cysu.ru/.well-known/security.txt
            Policy: https://cysu.ru/security-policy""",
        mimetype="text/plain",
    )


@main_bp.route("/.well-known/humans.txt")
def humans_txt() -> Response:
    """Возвращает файл humans.txt с информацией о команде разработки"""
    return Response(
        """Developer: cysu
    Contact: cysu.ru
    From: Russia
    Font Awesome: https://fontawesome.com/
    Bootstrap: https://getbootstrap.com/
    Flask: https://flask.palletsprojects.com/
    HTML5, CSS3, JavaScript
    Python, Flask
    Bootstrap 5
    Font Awesome 6
    SQLite
    Linux, Nginx
    Last update: 2025-09-13
    Language: Russian
    Doctype: HTML5
    IDE: VS Code
""",
        mimetype="text/plain",
    )


@main_bp.route("/.well-known/robots.txt")
def robots_txt() -> Response:
    """Возвращает файл robots.txt для поисковых роботов"""
    return Response(
        """User-agent: *
Allow: /
Sitemap: https://cysu.ru/sitemap.xml
Crawl-delay: 1
Disallow: /admin/
Disallow: /api/
Disallow: /static/logs/
Disallow: /static/temp/
Allow: /
Allow: /subjects/
Allow: /materials/
Allow: /profile/
Allow: /about/
Allow: /contact/
Allow: /wiki/
Allow: /privacy/
Allow: /terms/""",
        mimetype="text/plain",
    )


@main_bp.route("/robots.txt")
def robots_txt_redirect() -> Response:
    """Редирект с /robots.txt на /.well-known/robots.txt"""
    return redirect(url_for("main.robots_txt"), code=301)


@main_bp.route("/error/<int:error_code>")
def error_page(error_code: int) -> tuple:
    """Универсальная страница ошибок"""
    from datetime import datetime

    error_info = {
        400: {
            "title": "Неверный запрос",
            "description": "Сервер не может обработать запрос из-за неверного синтаксиса.",
        },
        401: {
            "title": "Не авторизован",
            "description": "Для доступа к этой странице необходимо войти в систему.",
        },
        403: {
            "title": "Доступ запрещен",
            "description": "У вас нет прав для доступа к этой странице.",
        },
        404: {
            "title": "Страница не найдена",
            "description": "К сожалению, запрашиваемая страница не существует или была перемещена.",
        },
        405: {
            "title": "Метод не разрешен",
            "description": "Используемый HTTP-метод не поддерживается для этого ресурса.",
        },
        408: {
            "title": "Время ожидания истекло",
            "description": "Сервер не получил полный запрос в течение установленного времени.",
        },
        409: {
            "title": "Конфликт",
            "description": "Запрос конфликтует с текущим состоянием сервера.",
        },
        410: {
            "title": "Ресурс недоступен",
            "description": "Запрашиваемый ресурс больше не доступен на сервере.",
        },
        413: {
            "title": "Слишком большой запрос",
            "description": "Размер запроса превышает максимально допустимый.",
        },
        414: {
            "title": "Слишком длинный URL",
            "description": "URL запроса слишком длинный для обработки сервером.",
        },
        415: {
            "title": "Неподдерживаемый тип медиа",
            "description": "Формат данных в запросе не поддерживается сервером.",
        },
        422: {
            "title": "Необрабатываемая сущность",
            "description": "Сервер понимает тип содержимого, но не может обработать инструкции.",
        },
        429: {
            "title": "Слишком много запросов",
            "description": "Превышено количество запросов. Попробуйте позже.",
        },
        500: {
            "title": "Внутренняя ошибка сервера",
            "description": "Произошла внутренняя ошибка сервера. Мы работаем над исправлением.",
        },
        501: {
            "title": "Не реализовано",
            "description": "Сервер не поддерживает функциональность, необходимую для выполнения запроса.",
        },
        502: {
            "title": "Плохой шлюз",
            "description": "Сервер получил неверный ответ от вышестоящего сервера.",
        },
        503: {
            "title": "Сервис недоступен",
            "description": "Сервер временно недоступен из-за технических работ или перегрузки.",
        },
        504: {
            "title": "Время ожидания шлюза",
            "description": "Сервер не получил ответ от вышестоящего сервера в установленное время.",
        },
        505: {
            "title": "Неподдерживаемая версия HTTP",
            "description": "Сервер не поддерживает версию HTTP-протокола, используемую в запросе.",
        },
    }
    error_data = error_info.get(
        error_code,
        {
            "title": f"Ошибка {error_code}",
            "description": "Произошла неизвестная ошибка.",
        },
    )
    error_details = {
        "error_code": escape(str(error_code)),
        "error_title": escape(str(error_data["title"])),
        "error_description": escape(str(error_data["description"])),
        "error_time": escape(datetime.now().strftime("%d.%m.%Y %H:%M:%S")),
        "error_traceback": None,
    }
    return render_template("error.html", **error_details), error_code


@main_bp.route("/404")
def not_found() -> tuple:
    return error_page(404)


@main_bp.app_errorhandler(400)
def handle_400(error) -> Response:
    return redirect(url_for("main.error_page", error_code=400))


@main_bp.app_errorhandler(401)
def handle_401(error) -> Response:
    return redirect(url_for("main.error_page", error_code=401))


@main_bp.app_errorhandler(403)
def handle_403(error) -> Response:
    return redirect(url_for("main.error_page", error_code=403))


@main_bp.app_errorhandler(404)
def handle_404(error) -> Response:
    return redirect(url_for("main.error_page", error_code=404))


@main_bp.app_errorhandler(405)
def handle_405(error) -> Response:
    return redirect(url_for("main.error_page", error_code=405))


@main_bp.app_errorhandler(500)
def handle_500(error) -> Response:
    return redirect(url_for("main.error_page", error_code=500))


@main_bp.app_errorhandler(502)
def handle_502(error) -> Response:
    return redirect(url_for("main.error_page", error_code=502))


@main_bp.app_errorhandler(503)
def handle_503(error) -> Response:
    return redirect(url_for("main.error_page", error_code=503))


@main_bp.route("/grant-temp-access")
def grant_temp_access() -> Response:
    from datetime import datetime, timedelta

    session["temp_access"] = (datetime.utcnow() + timedelta(minutes=3)).isoformat()
    flash("Временный доступ предоставлен на 3 минуты", "info")
    return redirect(url_for("auth.login"))


@main_bp.route("/static/<path:filename>")
def static_files(filename: str) -> Response:
    """Обработчик статических файлов с кэшированием"""
    import os

    from flask import make_response, send_from_directory

    static_dir = os.path.join(current_app.root_path, "static")
    response = make_response(send_from_directory(static_dir, filename))
    if filename.endswith(
        (
            ".css",
            ".js",
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".ico",
            ".svg",
            ".woff",
            ".woff2",
            ".ttf",
            ".eot",
        )
    ):
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        response.headers["Expires"] = "Thu, 31 Dec 2025 23:59:59 GMT"
    elif filename == "sw.js":
        response.headers["Cache-Control"] = "public, max-age=3600"
    elif filename.endswith((".html", ".xml", ".txt")):
        response.headers["Cache-Control"] = "public, max-age=3600"
    else:
        response.headers["Cache-Control"] = "public, max-age=86400"
    return response


@main_bp.route("/wiki")
def wiki() -> str:
    return render_template("static/wiki.html")


@main_bp.route("/redirect")
def redirect_page() -> str:
    return render_template("redirect.html")


@main_bp.route("/redirect/download")
def download_redirect() -> Response:
    from flask import make_response

    template_path = os.path.join(current_app.root_path, "templates", "redirect.html")
    with open(template_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    import re

    html_content = re.sub(
        r'<a href="/redirect/download"[^>]*download="cysu\.html"[^>]*>.*?</a>\s*',
        "",
        html_content,
        flags=re.DOTALL,
    )
    html_content = re.sub(
        r"\.btn-download\s*\{[^}]*\}", "", html_content, flags=re.DOTALL
    )
    response = make_response(html_content)
    response.headers["Content-Type"] = "text/html; charset=utf-8"
    response.headers["Content-Disposition"] = 'attachment; filename="cysu.html"'
    return response


@main_bp.route("/files/<int:subject_id>/<path:filename>", methods=["GET", "HEAD"])
def serve_file(subject_id: int, filename: str) -> Response:
    import os

    from flask import Response, abort, request

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    safe_filename = secure_filename(filename)
    possible_paths = []
    try:
        # Safely construct paths using os.path.join and os.path.normpath
        path1 = os.path.normpath(os.path.join(upload_folder, safe_filename))
        if path1.startswith(os.path.normpath(upload_folder)):
            possible_paths.append(path1)
    except Exception:
        pass
    try:
        path2 = os.path.normpath(
            os.path.join(upload_folder, str(subject_id), safe_filename)
        )
        if path2.startswith(os.path.normpath(upload_folder)):
            possible_paths.append(path2)
    except Exception:
        pass
    try:
        path3 = os.path.normpath(
            os.path.join(
                upload_folder, str(subject_id), os.path.basename(safe_filename)
            )
        )
        if path3.startswith(os.path.normpath(upload_folder)):
            possible_paths.append(path3)
    except Exception:
        pass
    try:
        users_dir = os.path.join(upload_folder, str(subject_id), "users")
        if os.path.isdir(users_dir):
            for user_folder in os.listdir(users_dir):
                if os.path.isdir(os.path.join(users_dir, user_folder)):
                    path4 = os.path.normpath(
                        os.path.join(users_dir, user_folder, safe_filename)
                    )
                    if path4.startswith(os.path.normpath(upload_folder)):
                        possible_paths.append(path4)
    except (OSError, Exception):
        pass
    try:
        users_dir = os.path.join(upload_folder, str(subject_id), "users")
        if os.path.isdir(users_dir):
            for user_folder in os.listdir(users_dir):
                if os.path.isdir(os.path.join(users_dir, user_folder)):
                    path5 = os.path.normpath(
                        os.path.join(
                            users_dir, user_folder, os.path.basename(safe_filename)
                        )
                    )
                    if path5.startswith(os.path.normpath(upload_folder)):
                        possible_paths.append(path5)
    except (OSError, Exception):
        pass
    file_path = None
    for path in possible_paths:
        if os.path.exists(path):
            file_path = path
            break
    if not file_path:
        current_app.logger.error(
            f"Файл не найден: {filename} для subject_id {subject_id}"
        )
        current_app.logger.error(f"Проверенные пути: {possible_paths}")
        abort(404)
    if filename.lower().endswith(".pdf"):
        mimetype = "application/pdf"
    elif filename.lower().endswith((".jpg", ".jpeg")):
        mimetype = "image/jpeg"
    elif filename.lower().endswith(".png"):
        mimetype = "image/png"
    elif filename.lower().endswith(".docx"):
        mimetype = (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    elif filename.lower().endswith(".doc"):
        mimetype = "application/msword"
    elif filename.lower().endswith(".txt"):
        mimetype = "text/plain"
    elif filename.lower().endswith(".zip"):
        mimetype = "application/zip"
    else:
        mimetype = "application/octet-stream"
    try:
        file_size = os.path.getsize(file_path)
        range_header = request.headers.get("Range")
        if range_header:
            return _handle_range_request(file_path, file_size, mimetype, filename)
        if request.method == "HEAD":
            response = Response(
                status=200,
                mimetype=mimetype,
                headers={
                    "Content-Length": str(file_size),
                    "Accept-Ranges": "bytes",
                    "Cache-Control": "public, max-age=3600",
                    "X-Content-Type-Options": "nosniff",
                    "X-Frame-Options": "SAMEORIGIN",
                },
            )
            response.headers["Content-Disposition"] = (
                f'attachment; filename="{os.path.basename(filename)}"'
            )
            return response

        def generate_file():
            try:
                with open(file_path, "rb") as f:
                    while True:
                        chunk = f.read(65536)
                        if not chunk:
                            break
                        yield chunk
            except Exception as e:
                current_app.logger.error(f"Ошибка чтения файла {file_path}: {e}")
                return

        response = Response(
            generate_file(),
            mimetype=mimetype,
            headers={
                "Content-Length": str(file_size),
                "Accept-Ranges": "bytes",
                "Cache-Control": "public, max-age=3600",
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "SAMEORIGIN",
            },
        )
        response.headers["Content-Disposition"] = (
            f'attachment; filename="{os.path.basename(filename)}"'
        )
        return response
    except Exception as e:
        current_app.logger.error(f"Ошибка обработки файла {file_path}: {e}")
        abort(500)


def _handle_range_request(
    file_path: str, file_size: int, mimetype: str, filename: str
) -> Response:
    import re

    from flask import Response, request

    range_match = re.match(r"bytes=(\d+)-(\d*)", request.headers.get("Range", ""))
    if not range_match:
        return Response("Bad Request", status=400)
    start = int(range_match.group(1))
    end = int(range_match.group(2)) if range_match.group(2) else file_size - 1
    if start >= file_size or end >= file_size or start > end:
        return Response("Requested Range Not Satisfiable", status=416)
    content_length = end - start + 1

    def generate_range():
        try:
            with open(file_path, "rb") as f:
                f.seek(start)
                remaining = content_length
                while remaining > 0:
                    chunk_size = min(65536, remaining)
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    remaining -= len(chunk)
                    yield chunk
        except Exception as e:
            current_app.logger.error(f"Ошибка чтения диапазона файла {file_path}: {e}")
            return

    response = Response(
        generate_range(),
        status=206,
        mimetype=mimetype,
        headers={
            "Content-Length": str(content_length),
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Cache-Control": "public, max-age=3600",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "SAMEORIGIN",
        },
    )
    response.headers["Content-Disposition"] = (
        f'attachment; filename="{os.path.basename(filename)}"'
    )
    return response


@main_bp.route(
    "/files/<int:subject_id>/users/<int:user_id>/<path:filename>",
    methods=["GET", "HEAD"],
)
def serve_user_file(subject_id: int, user_id: int, filename: str) -> Response:
    """Специальный маршрут для файлов решений пользователей"""
    import os

    from flask import Response, abort
    from werkzeug.utils import secure_filename

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    safe_filename = secure_filename(filename)
    file_path = os.path.normpath(
        os.path.join(
            upload_folder, str(subject_id), "users", str(user_id), safe_filename
        )
    )
    if not file_path.startswith(os.path.normpath(upload_folder)):
        # Path traversal attempt
        current_app.logger.error(f" Path traversal attempt: {file_path}")
        abort(404)
    if not os.path.exists(file_path):
        current_app.logger.error(f"Файл пользователя не найден: {file_path}")
        abort(404)
    if filename.lower().endswith(".pdf"):
        mimetype = "application/pdf"
    elif filename.lower().endswith((".jpg", ".jpeg")):
        mimetype = "image/jpeg"
    elif filename.lower().endswith(".png"):
        mimetype = "image/png"
    elif filename.lower().endswith(".docx"):
        mimetype = (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    elif filename.lower().endswith(".doc"):
        mimetype = "application/msword"
    elif filename.lower().endswith(".txt"):
        mimetype = "text/plain"
    elif filename.lower().endswith(".zip"):
        mimetype = "application/zip"
    else:
        mimetype = "application/octet-stream"
    try:
        file_size = os.path.getsize(file_path)

        def generate_file():
            try:
                with open(file_path, "rb") as f:
                    while True:
                        chunk = f.read(65536)
                        if not chunk:
                            break
                        yield chunk
            except Exception as e:
                current_app.logger.error(f"Ошибка чтения файла {file_path}: {e}")
                return

        response = Response(
            generate_file(),
            mimetype=mimetype,
            headers={
                "Content-Length": str(file_size),
                "Accept-Ranges": "bytes",
                "Cache-Control": "public, max-age=3600",
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "SAMEORIGIN",
                "Content-Disposition": f'attachment; filename="{os.path.basename(filename)}"',
            },
        )
        return response
    except Exception as e:
        current_app.logger.error(f"Ошибка обработки файла {file_path}: {e}")
        abort(500)


@main_bp.route("/export-solutions")
@login_required
def export_user_solutions() -> Response:
    from urllib.parse import quote

    temp_file = ExportService.export_user_solutions(
        current_user.id, current_user.username
    )
    if not temp_file:
        flash("У вас нет загруженных решений для экспорта", "info")
        return redirect(url_for("main.profile"))

    def remove_file(response):
        try:
            os.unlink(temp_file)
        except Exception:
            pass
        return response

    timestamp = os.path.basename(temp_file).replace(".zip", "").split("-")[-1]
    filename = f"{current_user.username}-{timestamp}.zip"
    response = send_file(
        temp_file,
        as_attachment=True,
        download_name=filename,
        mimetype="application/zip",
    )
    response.headers["Content-Disposition"] = (
        f"attachment; filename=\"{filename}\"; filename*=UTF-8''{quote(filename)}"
    )
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.call_on_close(
        lambda: os.unlink(temp_file) if os.path.exists(temp_file) else None
    )
    return response


@main_bp.route("/s/<code>")
def share_link(code: str) -> Response:
    """Обработка коротких ссылок на файлы материалов"""
    from ..models import ShortLink, Material, db

    short_link = ShortLink.query.filter_by(code=code).first()
    if not short_link:
        return redirect(url_for("main.not_found"))

    # Проверяем правила ссылки (если есть)
    if short_link.rule:
        from datetime import datetime

        if (
            short_link.rule.expires_at
            and short_link.rule.expires_at < datetime.utcnow()
        ):
            return redirect(url_for("main.not_found"))
        if (
            short_link.rule.max_clicks
            and short_link.clicks >= short_link.rule.max_clicks
        ):
            return redirect(url_for("main.not_found"))

    # Извлекаем ID материала из URL
    original_url = short_link.original_url
    if "/material/" in original_url:
        try:
            material_id = int(original_url.split("/material/")[-1])
            material = Material.query.get(material_id)

            if material and material.solution_file:
                # Для поделения используем только файл решения
                from ..utils.template_filters import extract_filename

                filename_to_share = extract_filename(material.solution_file)

                # Перенаправляем на файл
                file_url = url_for(
                    "main.serve_file",
                    subject_id=material.subject_id,
                    filename=filename_to_share,
                )
                return redirect(file_url)
        except (ValueError, IndexError) as e:
            current_app.logger.error(f"Error parsing material ID from share link: {e}")

    # Увеличиваем счетчик кликов
    short_link.clicks += 1
    db.session.commit()

    # Fallback - перенаправляем на оригинальный URL
    return redirect(short_link.original_url)


def get_share_url(material) -> str:
    """Получить короткую ссылку для решения материала с ленивой генерацией"""
    from ..models import ShortLink
    from datetime import datetime, timedelta

    original_url = url_for(
        "main.material_detail", material_id=material.id, _external=True
    )
    short_link = ShortLink.query.filter_by(original_url=original_url).first()

    if not short_link:
        short_link = ShortLink.create_unique(
            original_url, expires_at=datetime.utcnow() + timedelta(days=1)
        )

    return url_for("main.share_link", code=short_link.code, _external=True)
