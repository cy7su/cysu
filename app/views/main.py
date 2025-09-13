
import os
import shutil
from typing import Any, Dict, Union

from flask import (
    Blueprint,
    Response,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    escape,
)
from flask_login import current_user, login_required
from sqlalchemy.orm import joinedload
from werkzeug.utils import secure_filename

from .. import db
from ..forms import MaterialForm
from ..models import Material, SiteSettings, Subject, SubjectGroup, User
from ..utils.file_storage import FileStorageManager, safe_path_join
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

def generate_svg_pattern(pattern_type: str) -> str:

    fallback_patterns = {
        'dots': 'default_dots',
        'circles': 'default_circles', 
        'triangles': 'default_triangles',
        'hexagons': 'default_hexagons',
        'waves': 'default_waves',
        'stars': 'default_stars',
        'spiral': 'default_spiral'
    }

    return fallback_patterns.get(pattern_type, fallback_patterns['dots'])

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

        if current_user.is_admin:
            if request.method == "POST" and request.form.get("title"):
                try:
                    pattern_type = request.form.get("pattern_type", "dots")
                    pattern_svg = request.form.get("pattern_svg", "")  # Получаем SVG из формы

                    if not pattern_svg:
                        pattern_svg = generate_svg_pattern(pattern_type)

                    subject = Subject(
                        title=request.form.get("title"),
                        description=request.form.get("description", ""),
                        pattern_type=pattern_type,
                        pattern_svg=pattern_svg,  # Сохраняем полученный SVG
                        created_by=current_user.id,
                    )
                    db.session.add(subject)
                    db.session.commit()

                    try:
                        upload_base = current_app.config.get("UPLOAD_FOLDER", "app/static/uploads")
                        subject_path = os.path.join(upload_base, str(subject.id))
                        os.makedirs(subject_path, exist_ok=True)
                        current_app.logger.info(f"Создана папка для предмета {subject.id}: {subject_path}")
                    except Exception as folder_error:
                        current_app.logger.error(f"Ошибка создания папки для предмета {subject.id}: {folder_error}")

                    flash("Предмет добавлен")
                    return redirect(url_for("main.index"))
                except Exception as e:
                    current_app.logger.error(f"Error creating subject: {e}")
                    flash("Ошибка при создании предмета", "error")
                    db.session.rollback()

    try:
        if current_user.is_authenticated:
            subjects = current_user.get_accessible_subjects()
            subjects = Subject.query.options(
                joinedload(Subject.materials),
                joinedload(Subject.groups)
            ).filter(Subject.id.in_([s.id for s in subjects])).all()

            if not subjects and current_user.group_id:
                flash("У вашей группы нет назначенных предметов. Обратитесь к администратору.", "warning")
            elif not subjects and not current_user.group_id:
                flash("У вас не назначена группа. Обратитесь к администратору.", "warning")
        else:
            subjects = Subject.query.options(
                joinedload(Subject.materials),
                joinedload(Subject.groups)
            ).all()
    except Exception as e:
        current_app.logger.error(f"Error querying subjects: {e}")
        subjects = []
        flash("Ошибка загрузки предметов. Попробуйте обновить страницу.", "error")

    pattern_generation_enabled = SiteSettings.get_setting('pattern_generation_enabled', True)

    return render_template(
        "index.html",
        subjects=subjects,
        is_subscribed=is_subscribed,
        pattern_generation_enabled=pattern_generation_enabled
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
        subscription_expires=subscription_expires
    )

@main_bp.route("/subject/<int:subject_id>", methods=["GET", "POST"])
def subject_detail(subject_id: int) -> Union[str, Response]:
    if request.method == "POST":
        current_app.logger.info(f"POST запрос к subject_detail для предмета {subject_id}")
        current_app.logger.info(f"Content-Length: {request.content_length}")
        current_app.logger.info(f"Content-Type: {request.content_type}")
        current_app.logger.info(f"MAX_CONTENT_LENGTH: {current_app.config.get('MAX_CONTENT_LENGTH')}")

        if request.files:
            for key, file in request.files.items():
                if file and file.filename:
                    current_app.logger.info(f"Файл в запросе {key}: {file.filename}")
                    file_size = getattr(file, 'content_length', None)
                    if file_size:
                        current_app.logger.info(f"Размер файла {key}: {file_size} байт ({file_size / (1024*1024):.2f} MB)")
                    else:
                        current_app.logger.info(f"Размер файла {key}: неизвестен")
    try:
        subject = Subject.query.get_or_404(subject_id)
    except Exception as e:
        current_app.logger.error(f"Error loading subject {subject_id}: {e}")
        flash("Ошибка загрузки предмета.", "error")
        return redirect(url_for("main.index"))

    if current_user.is_authenticated:
        accessible_subjects = current_user.get_accessible_subjects()
        if subject not in accessible_subjects:
            flash("У вас нет доступа к этому предмету.", "error")
            return redirect(url_for("main.index"))

    if current_user.is_authenticated:
        try:
            payment_service = YooKassaService()
            if not payment_service.check_user_subscription(current_user):
                flash("Для доступа к предметам необходима активная подписка.", "warning")
                return redirect(url_for("payment.subscription"))

            if not current_user.is_effective_admin():
                if current_user.group:
                    subject_group = SubjectGroup.query.filter_by(
                        subject_id=subject.id,
                        group_id=current_user.group.id
                    ).first()
                    if not subject_group:
                        flash("У вас нет доступа к этому предмету.", "error")
                        return redirect(url_for("main.index"))
                else:
                    flash("У вас не назначена группа. Обратитесь к администратору.", "error")
                    return redirect(url_for("main.index"))
        except Exception as e:
            current_app.logger.error(f"Error checking subscription in subject_detail: {e}")
            flash("Ошибка проверки подписки.", "error")
            return redirect(url_for("main.index"))

    try:
        lectures = Material.query.filter_by(subject_id=subject.id, type="lecture").all()
        assignments = (
            Material.query.options(joinedload(Material.submissions))
            .filter_by(subject_id=subject.id, type="assignment")
            .all()
        )
    except Exception as e:
        current_app.logger.error(f"Error loading materials for subject {subject.id}: {e}")
        lectures = []
        assignments = []
        flash("Ошибка загрузки материалов.", "error")

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
    if current_user.is_authenticated and current_user.can_add_materials_to_subject(subject):
        form = MaterialForm()
        form.subject_id.choices = [(subject.id, subject.title)]
        form.subject_id.data = subject.id

        current_app.logger.info(f"Обработка формы материала для предмета {subject.id}")
        current_app.logger.info(f"Метод запроса: {request.method}")
        current_app.logger.info(f"Данные формы: {request.form}")
        current_app.logger.info(f"Файлы: {request.files}")

        if form and form.validate_on_submit():
            current_app.logger.info("Форма валидна, начинаем обработку")
            filename = None
            solution_filename = None

            subject = Subject.query.get_or_404(subject_id)

            if form.file.data:
                file = form.file.data
                original_filename = get_safe_filename(file.filename)

                file_size = getattr(file, 'content_length', None) or len(file.read()) if hasattr(file, 'read') else 'unknown'
                if hasattr(file, 'seek'):
                    file.seek(0)  # Возвращаем указатель в начало

                current_app.logger.info(f"Загрузка файла материала: {file.filename} -> {original_filename}")
                current_app.logger.info(f"Размер файла: {file_size} байт ({file_size / (1024*1024):.2f} MB)" if isinstance(file_size, int) else f"Размер файла: {file_size}")
                current_app.logger.info(f"MAX_CONTENT_LENGTH: {current_app.config.get('MAX_CONTENT_LENGTH')} байт ({current_app.config.get('MAX_CONTENT_LENGTH', 0) / (1024*1024):.2f} MB)")

                if isinstance(file_size, int) and current_app.config.get('MAX_CONTENT_LENGTH'):
                    if file_size > current_app.config.get('MAX_CONTENT_LENGTH'):
                        current_app.logger.error(f"Файл слишком большой: {file_size} байт > {current_app.config.get('MAX_CONTENT_LENGTH')} байт")
                        flash(f"Файл слишком большой. Максимальный размер: {current_app.config.get('MAX_CONTENT_LENGTH', 0) / (1024*1024):.1f} MB", "error")
                        return redirect(url_for("main.subject_detail", subject_id=subject_id))

                full_path, relative_path = FileStorageManager.get_material_upload_path(
                    subject.id, original_filename
                )

                current_app.logger.info(f"Путь для сохранения: {full_path}")
                current_app.logger.info(f"Относительный путь: {relative_path}")

                try:
                    if FileStorageManager.save_file(file, full_path):
                        filename = relative_path
                        current_app.logger.info(f"Файл материала успешно сохранен: {filename}")
                    else:
                        current_app.logger.error(f"Ошибка сохранения файла материала: {original_filename}")
                        flash("Ошибка при сохранении файла материала", "error")
                        return redirect(url_for("main.subject_detail", subject_id=subject_id))
                except Exception as e:
                    current_app.logger.error(f"Исключение при сохранении файла материала {original_filename}: {str(e)}")
                    flash(f"Ошибка при сохранении файла: {str(e)}", "error")
                    return redirect(url_for("main.subject_detail", subject_id=subject_id))

            if form.type.data == "assignment" and form.solution_file.data:
                solution_file = form.solution_file.data
                original_solution_filename = get_safe_filename(solution_file.filename)

                solution_file_size = getattr(solution_file, 'content_length', None) or len(solution_file.read()) if hasattr(solution_file, 'read') else 'unknown'
                if hasattr(solution_file, 'seek'):
                    solution_file.seek(0)  # Возвращаем указатель в начало

                current_app.logger.info(f"Загрузка файла решения: {solution_file.filename} -> {original_solution_filename}")
                current_app.logger.info(f"Размер файла решения: {solution_file_size} байт ({solution_file_size / (1024*1024):.2f} MB)" if isinstance(solution_file_size, int) else f"Размер файла решения: {solution_file_size}")

                if isinstance(solution_file_size, int) and current_app.config.get('MAX_CONTENT_LENGTH'):
                    if solution_file_size > current_app.config.get('MAX_CONTENT_LENGTH'):
                        current_app.logger.error(f"Файл решения слишком большой: {solution_file_size} байт > {current_app.config.get('MAX_CONTENT_LENGTH')} байт")
                        flash(f"Файл решения слишком большой. Максимальный размер: {current_app.config.get('MAX_CONTENT_LENGTH', 0) / (1024*1024):.1f} MB", "error")
                        return redirect(url_for("main.subject_detail", subject_id=subject_id))

                full_solution_path, relative_solution_path = (
                    FileStorageManager.get_material_upload_path(
                        subject.id,
                        original_solution_filename,
                    )
                )

                if FileStorageManager.save_file(solution_file, full_solution_path):
                    solution_filename = relative_solution_path
                    current_app.logger.info(f"Файл решения сохранен: {solution_filename}")
                else:
                    current_app.logger.error(f"Ошибка сохранения файла решения: {original_solution_filename}")
                    flash("Ошибка при сохранении файла решения", "error")
                    return redirect(url_for("main.subject_detail", subject_id=subject_id))

            material = Material(
                title=form.title.data,
                description=form.description.data,
                file=filename,
                type=form.type.data,
                solution_file=solution_filename,
                created_by=current_user.id,
                subject_id=subject.id,
            )
            db.session.add(material)
            db.session.commit()
            flash("Материал добавлен")
            return redirect(url_for("main.subject_detail", subject_id=subject.id))
        else:
            current_app.logger.warning(f"Форма не валидна: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    current_app.logger.warning(f"Ошибка в поле {field}: {error}")

    can_add_materials = False
    can_manage_materials = False
    if current_user.is_authenticated:
        can_add_materials = current_user.can_add_materials_to_subject(subject)
        can_manage_materials = current_user.can_manage_subject_materials(subject)

    return render_template(
        "subjects/subject_detail.html",
        subject=subject,
        lectures=lectures,
        assignments=assignments,
        form=form if can_add_materials else None,
        user_submissions=user_submissions,
        can_add_materials=can_add_materials,
        can_manage_materials=can_manage_materials,
    )

@main_bp.route("/subject/<int:subject_id>/edit", methods=["POST"])
@login_required
def edit_subject(subject_id: int) -> Response:
    if not current_user.is_effective_admin():
        flash("Доступ запрещён")
        return redirect(url_for("main.index"))

    subject = Subject.query.get_or_404(subject_id)

    try:
        new_title = request.form.get("title", "").strip()
        new_description = request.form.get("description", "").strip()

        if not new_title:
            flash("Название предмета не может быть пустым", "error")
            return redirect(url_for("main.subject_detail", subject_id=subject_id))

        if len(new_title) > 255:
            flash("Название предмета слишком длинное (максимум 255 символов)", "error")
            return redirect(url_for("main.subject_detail", subject_id=subject_id))

        if len(new_description) > 500:
            flash("Описание слишком длинное (максимум 500 символов)", "error")
            return redirect(url_for("main.subject_detail", subject_id=subject_id))

        subject.title = new_title
        subject.description = new_description if new_description else None

        db.session.commit()
        flash("Предмет успешно обновлён")
        current_app.logger.info(f"Предмет {subject.id} обновлён пользователем {current_user.id}")

    except Exception as e:
        current_app.logger.error(f"Ошибка редактирования предмета {subject_id}: {e}")
        flash("Ошибка при обновлении предмета", "error")
        db.session.rollback()

    return redirect(url_for("main.subject_detail", subject_id=subject_id))

@main_bp.route("/subject/<int:subject_id>/delete", methods=["POST"])
@login_required
def delete_subject(subject_id: int) -> Response:
    if not current_user.is_effective_admin():
        flash("Доступ запрещён")
        return redirect(url_for("main.index"))

    subject = Subject.query.get_or_404(subject_id)

    try:
        upload_base = current_app.config.get("UPLOAD_FOLDER", "app/static/uploads")
        subject_path = os.path.join(upload_base, str(subject.id))
        if os.path.exists(subject_path):
            shutil.rmtree(subject_path)
            current_app.logger.info(f"Удалена папка предмета {subject.id}: {subject_path}")
        else:
            current_app.logger.info(f"Папка предмета {subject.id} не существует: {subject_path}")
    except Exception as folder_error:
        current_app.logger.error(f"Ошибка удаления папки предмета {subject.id}: {folder_error}")

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
    if material.type == 'assignment' and current_user.is_authenticated:
        from app.models import Submission
        submission = Submission.query.filter_by(
            user_id=current_user.id,
            material_id=material_id
        ).first()
        if submission:
            user_submissions[material_id] = submission

    return render_template("subjects/material_detail.html", material=material, user_submissions=user_submissions)

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
            current_app.logger.error(f"Ошибка при удалении файла {submission.file}: {e}")

    db.session.delete(submission)
    db.session.commit()

    flash("Решение удалено", "success")
    return redirect(url_for("main.material_detail", material_id=submission.material_id))

@main_bp.route("/material/<int:material_id>/add_solution", methods=["POST"])
@login_required
def add_solution_file(material_id: int) -> Response:
    current_app.logger.info(f"POST запрос к add_solution_file для материала {material_id}")
    current_app.logger.info(f"Content-Length: {request.content_length}")
    current_app.logger.info(f"Content-Type: {request.content_type}")
    current_app.logger.info(f"MAX_CONTENT_LENGTH: {current_app.config.get('MAX_CONTENT_LENGTH')}")

    if request.files:
        for key, file in request.files.items():
            if file and file.filename:
                current_app.logger.info(f"Файл в запросе {key}: {file.filename}")
                file_size = getattr(file, 'content_length', None)
                if file_size:
                    current_app.logger.info(f"Размер файла {key}: {file_size} байт ({file_size / (1024*1024):.2f} MB)")
                else:
                    current_app.logger.info(f"Размер файла {key}: неизвестен")
    if not current_user.can_manage_materials():
        flash("Доступ запрещён")
        return redirect(url_for("main.index"))

    material = Material.query.get_or_404(material_id)

    if current_user.is_moderator:
        accessible_subjects = current_user.get_accessible_subjects()
        if material.subject not in accessible_subjects:
            flash("У вас нет доступа к этому предмету.", "error")
            return redirect(url_for("main.index"))
    file = request.files.get("solution_file")
    if file:
        subject = material.subject
        original_filename = get_safe_filename(file.filename)

        file_size = getattr(file, 'content_length', None) or len(file.read()) if hasattr(file, 'read') else 'unknown'
        if hasattr(file, 'seek'):
            file.seek(0)  # Возвращаем указатель в начало

        current_app.logger.info(f"Загрузка готового решения: {file.filename} -> {original_filename}")
        current_app.logger.info(f"Размер файла: {file_size} байт ({file_size / (1024*1024):.2f} MB)" if isinstance(file_size, int) else f"Размер файла: {file_size}")

        if isinstance(file_size, int) and current_app.config.get('MAX_CONTENT_LENGTH'):
            if file_size > current_app.config.get('MAX_CONTENT_LENGTH'):
                current_app.logger.error(f"Файл готового решения слишком большой: {file_size} байт > {current_app.config.get('MAX_CONTENT_LENGTH')} байт")
                flash(f"Файл слишком большой. Максимальный размер: {current_app.config.get('MAX_CONTENT_LENGTH', 0) / (1024*1024):.1f} MB", "error")
                return redirect(url_for("main.subject_detail", subject_id=material.subject_id))

        full_path, relative_path = FileStorageManager.get_material_upload_path(
            subject.id, original_filename
        )

        try:
            if FileStorageManager.save_file(file, full_path):
                material.solution_file = relative_path
                db.session.commit()
                current_app.logger.info(f"Готовое решение успешно сохранено: {relative_path}")
                flash("Готовая практика добавлена")
            else:
                current_app.logger.error(f"Ошибка сохранения готового решения: {original_filename}")
                flash("Ошибка при сохранении файла", "error")
        except Exception as e:
            current_app.logger.error(f"Исключение при сохранении готового решения {original_filename}: {str(e)}")
            flash(f"Ошибка при сохранении файла: {str(e)}", "error")

    return redirect(url_for("main.subject_detail", subject_id=material.subject_id))

@main_bp.route("/material/<int:material_id>/submit_solution", methods=["POST"])
@login_required
def submit_solution(material_id: int) -> Response:
    current_app.logger.info(f"POST запрос к submit_solution для материала {material_id} от пользователя {current_user.id}")
    current_app.logger.info(f"Content-Length: {request.content_length}")
    current_app.logger.info(f"Content-Type: {request.content_type}")
    current_app.logger.info(f"MAX_CONTENT_LENGTH: {current_app.config.get('MAX_CONTENT_LENGTH')}")

    if request.files:
        for key, file in request.files.items():
            if file and file.filename:
                current_app.logger.info(f"Файл в запросе {key}: {file.filename}")
                file_size = getattr(file, 'content_length', None)
                if file_size:
                    current_app.logger.info(f"Размер файла {key}: {file_size} байт ({file_size / (1024*1024):.2f} MB)")
                else:
                    current_app.logger.info(f"Размер файла {key}: неизвестен")
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

        file_size = getattr(file, 'content_length', None) or len(file.read()) if hasattr(file, 'read') else 'unknown'
        if hasattr(file, 'seek'):
            file.seek(0)  # Возвращаем указатель в начало

        current_app.logger.info(f"Загрузка решения пользователя {current_user.id}: {file.filename} -> {original_filename}")
        current_app.logger.info(f"Размер файла: {file_size} байт ({file_size / (1024*1024):.2f} MB)" if isinstance(file_size, int) else f"Размер файла: {file_size}")

        if isinstance(file_size, int) and current_app.config.get('MAX_CONTENT_LENGTH'):
            if file_size > current_app.config.get('MAX_CONTENT_LENGTH'):
                current_app.logger.error(f"Файл решения пользователя слишком большой: {file_size} байт > {current_app.config.get('MAX_CONTENT_LENGTH')} байт")
                flash(f"Файл слишком большой. Максимальный размер: {current_app.config.get('MAX_CONTENT_LENGTH', 0) / (1024*1024):.1f} MB", "error")
                return redirect(url_for("main.subject_detail", subject_id=material.subject_id))

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
                current_app.logger.info(f"Решение пользователя {current_user.id} успешно сохранено: {relative_path}")
                flash("Решение загружено")
            else:
                current_app.logger.error(f"Ошибка сохранения решения пользователя {current_user.id}: {original_filename}")
                flash("Ошибка при сохранении файла решения", "error")
        except Exception as e:
            current_app.logger.error(f"Исключение при сохранении решения пользователя {current_user.id} {original_filename}: {str(e)}")
            flash(f"Ошибка при сохранении файла: {str(e)}", "error")

    return redirect(url_for("main.subject_detail", subject_id=material.subject_id))

@main_bp.route("/toggle-admin-mode", methods=["POST"])
@login_required
def toggle_admin_mode() -> Response:
    if not current_user.is_admin:
        flash("Доступ запрещён")
        return redirect(url_for("main.index"))

    current_user.admin_mode_enabled = not current_user.admin_mode_enabled
    db.session.commit()

    mode = "админ" if current_user.admin_mode_enabled else "пользователь"
    flash(f"Переключен в режим {mode}")

    return redirect(request.referrer or url_for("main.index"))

@main_bp.route("/material/<int:material_id>/edit", methods=["POST"])
@login_required
def edit_material(material_id: int) -> Response:
    if not current_user.can_manage_materials():
        flash("Доступ запрещён")
        return redirect(url_for("main.index"))

    material = Material.query.get_or_404(material_id)

    if current_user.is_moderator:
        accessible_subjects = current_user.get_accessible_subjects()
        if material.subject not in accessible_subjects:
            flash("У вас нет доступа к этому предмету.", "error")
            return redirect(url_for("main.index"))

    try:
        new_title = request.form.get("title", "").strip()
        new_description = request.form.get("description", "").strip()

        if not new_title:
            flash("Название материала не может быть пустым", "error")
            return redirect(url_for("main.material_detail", material_id=material.id))

        if len(new_title) > 255:
            flash("Название материала слишком длинное (максимум 255 символов)", "error")
            return redirect(url_for("main.material_detail", material_id=material.id))

        if len(new_description) > 300:
            flash("Описание слишком длинное (максимум 300 символов)", "error")
            return redirect(url_for("main.material_detail", material_id=material.id))

        material.title = new_title
        material.description = new_description if new_description else None

        db.session.commit()
        flash("Материал успешно обновлён")
        current_app.logger.info(f"Материал {material.id} обновлён пользователем {current_user.id}")

    except Exception as e:
        current_app.logger.error(f"Ошибка редактирования материала {material_id}: {e}")
        flash("Ошибка при обновлении материала", "error")
        db.session.rollback()

    return redirect(url_for("main.material_detail", material_id=material.id))

@main_bp.route("/material/<int:material_id>/delete", methods=["POST"])
@login_required
def delete_material(material_id: int) -> Response:
    if not current_user.can_manage_materials():
        flash("Доступ запрещён")
        return redirect(url_for("main.index"))

    material = Material.query.get_or_404(material_id)
    subject_id = material.subject_id

    if current_user.is_moderator:
        accessible_subjects = current_user.get_accessible_subjects()
        if material.subject not in accessible_subjects:
            flash("У вас нет доступа к этому предмету.", "error")
            return redirect(url_for("main.index"))

    if material.file:
        try:
            upload_base = current_app.config.get("UPLOAD_FOLDER", "app/static/uploads")
            file_path = os.path.join(upload_base, material.file)
            if os.path.exists(file_path):
                os.remove(file_path)
                current_app.logger.info(f"Удален файл материала: {file_path}")
        except Exception as file_error:
            current_app.logger.error(f"Ошибка удаления файла материала {material.file}: {file_error}")

    if material.solution_file:
        try:
            upload_base = current_app.config.get("UPLOAD_FOLDER", "app/static/uploads")
            solution_path = os.path.join(upload_base, material.solution_file)
            if os.path.exists(solution_path):
                os.remove(solution_path)
                current_app.logger.info(f"Удален файл решения: {solution_path}")
        except Exception as solution_error:
            current_app.logger.error(f"Ошибка удаления файла решения {material.solution_file}: {solution_error}")

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
Policy: https://cysu.ru/security-policy

# Политика безопасности
# Если вы нашли уязвимость, пожалуйста, сообщите нам
# We appreciate responsible disclosure of security vulnerabilities""",
        mimetype="text/plain"
    )

@main_bp.route("/.well-known/humans.txt")
def humans_txt() -> Response:
    """Возвращает файл humans.txt с информацией о команде разработки"""
    return Response(
        """# humanstxt.org/
# The humans responsible & technology colophon

# TEAM

    Developer: cy7su
    Contact: cysu.ru
    From: Russia

# THANKS

    Font Awesome: https://fontawesome.com/
    Bootstrap: https://getbootstrap.com/
    Flask: https://flask.palletsprojects.com/

# TECHNOLOGY COLOPHON

    HTML5, CSS3, JavaScript
    Python, Flask
    Bootstrap 5
    Font Awesome 6
    SQLite
    Linux, Nginx

# SITE

    Last update: 2025/09/13
    Language: Russian
    Doctype: HTML5
    IDE: VS Code""",
        mimetype="text/plain"
    )

@main_bp.route("/.well-known/robots.txt")
def robots_txt() -> Response:
    """Возвращает файл robots.txt для поисковых роботов"""
    return Response(
        """User-agent: *
Allow: /

# Sitemap
Sitemap: https://cysu.ru/sitemap.xml

# Дополнительные директивы для поисковых систем
Crawl-delay: 1

# Контактная информация
# Host: cysu.ru

# Разрешаем индексацию всех страниц
Disallow: /admin/
Disallow: /api/
Disallow: /static/logs/
Disallow: /static/temp/

# Разрешаем индексацию основных страниц
Allow: /
Allow: /subjects/
Allow: /materials/
Allow: /profile/
Allow: /about/
Allow: /contact/
Allow: /wiki/
Allow: /privacy/
Allow: /terms/""",
        mimetype="text/plain"
    )

@main_bp.route("/robots.txt")
def robots_txt_redirect() -> Response:
    """Редирект с /robots.txt на /.well-known/robots.txt"""
    return redirect(url_for('main.robots_txt'), code=301)

@main_bp.route("/error/<int:error_code>")
def error_page(error_code: int) -> tuple:
    """Универсальная страница ошибок"""
    from datetime import datetime
    
    # Определяем информацию об ошибке по коду
    error_info = {
        400: {
            "title": "Неверный запрос",
            "description": "Сервер не может обработать запрос из-за неверного синтаксиса."
        },
        401: {
            "title": "Не авторизован",
            "description": "Для доступа к этой странице необходимо войти в систему."
        },
        403: {
            "title": "Доступ запрещен",
            "description": "У вас нет прав для доступа к этой странице."
        },
        404: {
            "title": "Страница не найдена",
            "description": "К сожалению, запрашиваемая страница не существует или была перемещена."
        },
        405: {
            "title": "Метод не разрешен",
            "description": "Используемый HTTP-метод не поддерживается для этого ресурса."
        },
        408: {
            "title": "Время ожидания истекло",
            "description": "Сервер не получил полный запрос в течение установленного времени."
        },
        409: {
            "title": "Конфликт",
            "description": "Запрос конфликтует с текущим состоянием сервера."
        },
        410: {
            "title": "Ресурс недоступен",
            "description": "Запрашиваемый ресурс больше не доступен на сервере."
        },
        413: {
            "title": "Слишком большой запрос",
            "description": "Размер запроса превышает максимально допустимый."
        },
        414: {
            "title": "Слишком длинный URL",
            "description": "URL запроса слишком длинный для обработки сервером."
        },
        415: {
            "title": "Неподдерживаемый тип медиа",
            "description": "Формат данных в запросе не поддерживается сервером."
        },
        422: {
            "title": "Необрабатываемая сущность",
            "description": "Сервер понимает тип содержимого, но не может обработать инструкции."
        },
        429: {
            "title": "Слишком много запросов",
            "description": "Превышено количество запросов. Попробуйте позже."
        },
        500: {
            "title": "Внутренняя ошибка сервера",
            "description": "Произошла внутренняя ошибка сервера. Мы работаем над исправлением."
        },
        501: {
            "title": "Не реализовано",
            "description": "Сервер не поддерживает функциональность, необходимую для выполнения запроса."
        },
        502: {
            "title": "Плохой шлюз",
            "description": "Сервер получил неверный ответ от вышестоящего сервера."
        },
        503: {
            "title": "Сервис недоступен",
            "description": "Сервер временно недоступен из-за технических работ или перегрузки."
        },
        504: {
            "title": "Время ожидания шлюза",
            "description": "Сервер не получил ответ от вышестоящего сервера в установленное время."
        },
        505: {
            "title": "Неподдерживаемая версия HTTP",
            "description": "Сервер не поддерживает версию HTTP-протокола, используемую в запросе."
        }
    }
    
    # Получаем информацию об ошибке или используем значения по умолчанию
    error_data = error_info.get(error_code, {
        "title": f"Ошибка {error_code}",
        "description": "Произошла неизвестная ошибка."
    })
    
    # Дополнительная информация для отладки
    error_details = {
        "error_code": escape(str(error_code)),
        "error_title": escape(str(error_data["title"])),
        "error_description": escape(str(error_data["description"])),
        "error_time": escape(datetime.now().strftime("%d.%m.%Y %H:%M:%S")),
        "error_traceback": None  # Можно добавить traceback в production
    }
    
    return render_template("error.html", **error_details), error_code

@main_bp.route("/404")
def not_found() -> tuple:
    return error_page(404)

@main_bp.app_errorhandler(400)
def handle_400(error) -> Response:
    return redirect(url_for('main.error_page', error_code=400))

@main_bp.app_errorhandler(401)
def handle_401(error) -> Response:
    return redirect(url_for('main.error_page', error_code=401))

@main_bp.app_errorhandler(403)
def handle_403(error) -> Response:
    return redirect(url_for('main.error_page', error_code=403))

@main_bp.app_errorhandler(404)
def handle_404(error) -> Response:
    return redirect(url_for('main.error_page', error_code=404))

@main_bp.app_errorhandler(405)
def handle_405(error) -> Response:
    return redirect(url_for('main.error_page', error_code=405))

@main_bp.app_errorhandler(500)
def handle_500(error) -> Response:
    return redirect(url_for('main.error_page', error_code=500))

@main_bp.app_errorhandler(502)
def handle_502(error) -> Response:
    return redirect(url_for('main.error_page', error_code=502))

@main_bp.app_errorhandler(503)
def handle_503(error) -> Response:
    return redirect(url_for('main.error_page', error_code=503))

@main_bp.route("/maintenance")
def maintenance() -> str:
    return render_template("maintenance.html")

@main_bp.route("/static/<path:filename>")
def static_files(filename: str) -> Response:
    """Обработчик статических файлов с кэшированием"""
    from flask import send_from_directory, make_response
    import os
    
    # Путь к статическим файлам
    static_dir = os.path.join(current_app.root_path, 'static')
    
    # Отправляем файл
    response = make_response(send_from_directory(static_dir, filename))
    
    # Добавляем заголовки кэширования
    if filename.endswith(('.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.woff', '.woff2', '.ttf', '.eot')):
        # Статические ресурсы кэшируем на 1 год
        response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
        response.headers['Expires'] = 'Thu, 31 Dec 2025 23:59:59 GMT'
    elif filename == 'sw.js':
        # Service Worker кэшируем на 1 час
        response.headers['Cache-Control'] = 'public, max-age=3600'
    elif filename.endswith(('.html', '.xml', '.txt')):
        # HTML и текстовые файлы кэшируем на 1 час
        response.headers['Cache-Control'] = 'public, max-age=3600'
    else:
        # Остальные файлы кэшируем на 1 день
        response.headers['Cache-Control'] = 'public, max-age=86400'
    
    return response

@main_bp.route("/wiki")
def wiki() -> str:
    return render_template("static/wiki.html")

@main_bp.route("/macro/time")
def macro_time() -> str:
    return render_template("for_my_love/time.html")

@main_bp.route("/macro")
def macro() -> str:
    return render_template("for_my_love/macro.html")

@main_bp.route("/redirect")
def redirect_page() -> str:
    return render_template("redirect.html")

@main_bp.route("/redirect/download")
def download_redirect() -> Response:
    from flask import make_response

    with open('/root/cysu/app/templates/redirect.html', 'r', encoding='utf-8') as f:
        html_content = f.read()

    import re

    html_content = re.sub(
        r'<a href="/redirect/download"[^>]*download="cysu\.html"[^>]*>.*?</a>\s*',
        '',
        html_content,
        flags=re.DOTALL
    )

    html_content = re.sub(
        r'\.btn-download\s*\{[^}]*\}',
        '',
        html_content,
        flags=re.DOTALL
    )

    response = make_response(html_content)
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    response.headers['Content-Disposition'] = 'attachment; filename="cysu.html"'

    return response

@main_bp.route('/files/<int:subject_id>/<path:filename>', methods=['GET', 'HEAD'])
def serve_file(subject_id: int, filename: str) -> Response:
    import os
    import time

    from flask import Response, abort, request

    current_app.logger.info(f"serve_file вызвана: subject_id={subject_id}, filename={filename}")
    current_app.logger.info(f"UPLOAD_FOLDER: {current_app.config['UPLOAD_FOLDER']}")
    start_time = time.time()

    # Безопасное создание возможных путей
    upload_folder = current_app.config['UPLOAD_FOLDER']
    safe_filename = secure_filename(filename)
    
    possible_paths = []
    try:
        # Базовый путь
        possible_paths.append(safe_path_join(upload_folder, safe_filename))
    except ValueError:
        pass
    
    try:
        # Путь с subject_id
        possible_paths.append(safe_path_join(upload_folder, str(subject_id), safe_filename))
    except ValueError:
        pass
    
    try:
        # Путь с basename
        possible_paths.append(safe_path_join(upload_folder, str(subject_id), os.path.basename(safe_filename)))
    except ValueError:
        pass

    file_path = None
    for i, path in enumerate(possible_paths):
        current_app.logger.info(f"Проверяем путь {i+1}: {path}")
        current_app.logger.info(f"Путь существует: {os.path.exists(path)}")
        if os.path.exists(path):
            file_path = path
            current_app.logger.info(f"Файл найден по пути: {path}")
            break

    if not file_path:
        current_app.logger.error(f"Файл не найден: {filename} для subject_id {subject_id}")
        current_app.logger.error(f"Проверенные пути: {possible_paths}")
        abort(404)

    if filename.lower().endswith('.pdf'):
        mimetype = 'application/pdf'
    elif filename.lower().endswith(('.jpg', '.jpeg')):
        mimetype = 'image/jpeg'
    elif filename.lower().endswith('.png'):
        mimetype = 'image/png'
    else:
        mimetype = 'application/octet-stream'

    try:
        file_size = os.path.getsize(file_path)
        current_app.logger.info(f"Размер файла {filename}: {file_size} байт")

        range_header = request.headers.get('Range')
        if range_header:
            current_app.logger.info(f"Range запрос: {range_header}")
            return _handle_range_request(file_path, file_size, mimetype, filename)

        if request.method == 'HEAD':
            response = Response(
                status=200,
                mimetype=mimetype,
                headers={
                    'Content-Length': str(file_size),
                    'Accept-Ranges': 'bytes',
                    'Cache-Control': 'public, max-age=3600',
                    'X-Content-Type-Options': 'nosniff',
                    'X-Frame-Options': 'SAMEORIGIN'
                }
            )

            if filename.lower().endswith('.pdf'):
                response.headers['Content-Disposition'] = f'attachment; filename="{os.path.basename(filename)}"'

            return response

        def generate_file():
            try:
                with open(file_path, 'rb') as f:
                    while True:
                        chunk = f.read(65536)  # Читаем по 64KB для лучшей производительности
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
                'Content-Length': str(file_size),
                'Accept-Ranges': 'bytes',
                'Cache-Control': 'public, max-age=3600',
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': 'SAMEORIGIN'
            }
        )

        if filename.lower().endswith('.pdf'):
            response.headers['Content-Disposition'] = f'attachment; filename="{os.path.basename(filename)}"'

        execution_time = time.time() - start_time
        current_app.logger.info(f"Файл {filename} обработан за {execution_time:.3f} секунд")

        return response

    except Exception as e:
        current_app.logger.error(f"Ошибка обработки файла {file_path}: {e}")
        abort(500)

def _handle_range_request(file_path: str, file_size: int, mimetype: str, filename: str) -> Response:
    import re

    from flask import Response, request

    range_match = re.match(r'bytes=(\d+)-(\d*)', request.headers.get('Range', ''))
    if not range_match:
        current_app.logger.warning("Некорректный Range заголовок")
        return Response('Bad Request', status=400)

    start = int(range_match.group(1))
    end = int(range_match.group(2)) if range_match.group(2) else file_size - 1

    if start >= file_size or end >= file_size or start > end:
        current_app.logger.warning(f"Некорректный диапазон: {start}-{end} для файла размером {file_size}")
        return Response('Requested Range Not Satisfiable', status=416)

    content_length = end - start + 1

    current_app.logger.info(f"Range запрос: {start}-{end} из {file_size} байт")

    def generate_range():
        try:
            with open(file_path, 'rb') as f:
                f.seek(start)
                remaining = content_length
                while remaining > 0:
                    chunk_size = min(65536, remaining)  # Читаем по 64KB для лучшей производительности
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
        status=206,  # Partial Content
        mimetype=mimetype,
        headers={
            'Content-Length': str(content_length),
            'Content-Range': f'bytes {start}-{end}/{file_size}',
            'Accept-Ranges': 'bytes',
            'Cache-Control': 'public, max-age=3600',
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'SAMEORIGIN'
        }
    )

    if filename.lower().endswith('.pdf'):
        response.headers['Content-Disposition'] = f'attachment; filename="{os.path.basename(filename)}"'

    return response

