"""
Основной модуль views с базовыми функциями
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, Response
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy.orm import joinedload
from typing import Union, Dict, Any

from ..models import User, Material, Subject, SubjectGroup
from ..forms import MaterialForm
from ..utils.payment_service import YooKassaService
from ..utils.file_storage import FileStorageManager
from .. import db
from .context_processors import (
    inject_json_parser, inject_timestamp, inject_moment,
    inject_admin_users, inject_subscription_status
)

main_bp = Blueprint("main", __name__)

# Регистрируем context processors
main_bp.app_context_processor(inject_json_parser)
main_bp.app_context_processor(inject_timestamp)
main_bp.app_context_processor(inject_moment)
main_bp.app_context_processor(inject_admin_users)
main_bp.app_context_processor(inject_subscription_status)

def generate_svg_pattern(pattern_type: str) -> str:
    """Генерирует уникальный SVG паттерн для предмета используя существующий генератор"""
    # Используем простые SVG паттерны как fallback, если генератор не доступен
    # В реальности SVG будет генерироваться на клиенте через svg-patterns.js
    
    # Простые fallback паттерны
    fallback_patterns = {
        'dots': '''<svg xmlns="http://www.w3.org/2000/svg" width="300" height="200">
            <rect x="0" y="0" width="100%" height="100%" fill="#2a2a2a"/>
            <circle cx="50" cy="50" r="8" fill="#B595FF" opacity="0.8"/>
            <circle cx="150" cy="80" r="12" fill="#9A7FE6" opacity="0.6"/>
            <circle cx="250" cy="120" r="6" fill="#FFFFFF" opacity="0.7"/>
        </svg>''',
        'circles': '''<svg xmlns="http://www.w3.org/2000/svg" width="300" height="200">
            <rect x="0" y="0" width="100%" height="100%" fill="#333333"/>
            <circle cx="75" cy="100" r="30" fill="#B595FF" opacity="0.3"/>
            <circle cx="225" cy="100" r="25" fill="#9A7FE6" opacity="0.4"/>
        </svg>''',
        'triangles': '''<svg xmlns="http://www.w3.org/2000/svg" width="300" height="200">
            <rect x="0" y="0" width="100%" height="100%" fill="#2d2d2d"/>
            <polygon points="50,50 80,20 110,50" fill="#B595FF" opacity="0.6"/>
            <polygon points="200,100 230,70 260,100" fill="#9A7FE6" opacity="0.5"/>
        </svg>''',
        'hexagons': '''<svg xmlns="http://www.w3.org/2000/svg" width="300" height="200">
            <rect x="0" y="0" width="100%" height="100%" fill="#2b2b2b"/>
            <polygon points="75,50 85,40 95,40 105,50 95,60 85,60" fill="#B595FF" opacity="0.5"/>
            <polygon points="200,100 210,90 220,90 230,100 220,110 210,110" fill="#9A7FE6" opacity="0.4"/>
        </svg>''',
        'waves': '''<svg xmlns="http://www.w3.org/2000/svg" width="300" height="200">
            <rect x="0" y="0" width="100%" height="100%" fill="#303030"/>
            <path d="M0,100 Q75,50 150,100 T300,100" stroke="#B595FF" stroke-width="3" fill="none" opacity="0.6"/>
            <path d="M0,120 Q75,70 150,120 T300,120" stroke="#9A7FE6" stroke-width="2" fill="none" opacity="0.5"/>
        </svg>''',
        'stars': '''<svg xmlns="http://www.w3.org/2000/svg" width="300" height="200">
            <rect x="0" y="0" width="100%" height="100%" fill="#353535"/>
            <polygon points="50,50 55,45 60,50 55,55" fill="#B595FF" opacity="0.8"/>
            <polygon points="200,100 205,95 210,100 205,105" fill="#9A7FE6" opacity="0.7"/>
        </svg>''',
        'spiral': '''<svg xmlns="http://www.w3.org/2000/svg" width="300" height="200">
            <rect x="0" y="0" width="100%" height="100%" fill="#2a2a2a"/>
            <path d="M150,100 Q160,90 170,100 Q180,110 190,100 Q200,90 210,100" stroke="#B595FF" stroke-width="2" fill="none" opacity="0.6"/>
        </svg>'''
    }
    
    # Возвращаем fallback паттерн
    return fallback_patterns.get(pattern_type, fallback_patterns['dots'])

@main_bp.route("/", methods=["GET", "POST"])
def index() -> Union[str, Response]:
    """Главная страница"""
    is_subscribed = False

    if current_user.is_authenticated:
        # Проверяем подписку пользователя
        try:
            payment_service = YooKassaService()
            is_subscribed = payment_service.check_user_subscription(current_user)
        except Exception as e:
            current_app.logger.error(f"Error checking subscription in index: {e}")
            is_subscribed = False

        if current_user.is_admin:
            # Обрабатываем данные из модального окна
            if request.method == "POST" and request.form.get("title"):
                try:
                    pattern_type = request.form.get("pattern_type", "dots")
                    pattern_svg = request.form.get("pattern_svg", "")  # Получаем SVG из формы
                    
                    # Если SVG не передан, используем fallback
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
                    flash("Предмет добавлен")
                    return redirect(url_for("main.index"))
                except Exception as e:
                    current_app.logger.error(f"Error creating subject: {e}")
                    flash("Ошибка при создании предмета", "error")
                    db.session.rollback()

    try:
        if current_user.is_authenticated and not current_user.is_admin:
            # Для обычных пользователей показываем только предметы их группы
            if current_user.group:
                subjects = Subject.query.options(
                    joinedload(Subject.materials),
                    joinedload(Subject.groups)
                ).join(SubjectGroup).filter(
                    SubjectGroup.group_id == current_user.group.id
                ).all()
            else:
                subjects = []
                flash("У вас не назначена группа. Обратитесь к администратору.", "warning")
        else:
            # Для админов и неавторизованных пользователей показываем все предметы
            subjects = Subject.query.options(
                joinedload(Subject.materials),
                joinedload(Subject.groups)
            ).all()
    except Exception as e:
        current_app.logger.error(f"Error querying subjects: {e}")
        subjects = []
        flash("Ошибка загрузки предметов. Попробуйте обновить страницу.", "error")
    
    return render_template(
        "index.html", subjects=subjects, is_subscribed=is_subscribed
    )


@main_bp.route("/profile")
@login_required
def profile() -> str:
    """Страница профиля пользователя"""
    try:
        # Создаем сервис платежей
        payment_service = YooKassaService()
        # Проверяем актуальность подписки
        is_subscribed = payment_service.check_user_subscription(current_user)
    except Exception as e:
        current_app.logger.error(f"Error checking subscription in profile: {e}")
        is_subscribed = False
        flash("Ошибка проверки подписки.", "error")

    return render_template(
        "profile.html", user=current_user, is_subscribed=is_subscribed
    )


@main_bp.route("/subject/<int:subject_id>", methods=["GET", "POST"])
def subject_detail(subject_id: int) -> Union[str, Response]:
    """Детальная страница предмета"""
    try:
        subject = Subject.query.get_or_404(subject_id)
    except Exception as e:
        current_app.logger.error(f"Error loading subject {subject_id}: {e}")
        flash("Ошибка загрузки предмета.", "error")
        return redirect(url_for("main.index"))

    # Проверяем подписку для аутентифицированных пользователей
    if current_user.is_authenticated:
        try:
            # Создаем сервис платежей
            payment_service = YooKassaService()
            # Проверяем подписку пользователя
            if not payment_service.check_user_subscription(current_user):
                flash("Для доступа к предметам необходима активная подписка.", "warning")
                return redirect(url_for("payment.subscription"))
            
            # Проверяем доступ к предмету по группе (если пользователь не админ)
            if not current_user.is_admin:
                # Проверяем, есть ли у пользователя группа
                if current_user.group:
                    # Проверяем, доступен ли предмет для группы пользователя
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
    
    if current_user.is_authenticated and current_user.is_admin:
        form = MaterialForm()
        form.subject_id.choices = [(subject.id, subject.title)]
        form.subject_id.data = subject.id
        if form.validate_on_submit():
            filename = None
            solution_filename = None

            # Получаем информацию о предмете
            subject = Subject.query.get_or_404(subject_id)

            if form.file.data:
                file = form.file.data
                original_filename = secure_filename(file.filename)

                # Создаем путь для файла материала
                full_path, relative_path = FileStorageManager.get_material_upload_path(
                    subject.id, original_filename
                )

                # Сохраняем файл
                if FileStorageManager.save_file(file, full_path):
                    filename = relative_path

            if form.type.data == "assignment" and form.solution_file.data:
                solution_file = form.solution_file.data
                original_solution_filename = secure_filename(solution_file.filename)

                # Создаем путь для файла решения
                full_solution_path, relative_solution_path = (
                    FileStorageManager.get_material_upload_path(
                        subject.id,
                        f"solution_{original_solution_filename}",
                    )
                )

                # Сохраняем файл решения
                if FileStorageManager.save_file(solution_file, full_solution_path):
                    solution_filename = relative_solution_path
            
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
    
    return render_template(
        "subjects/subject_detail.html",
        subject=subject,
        lectures=lectures,
        assignments=assignments,
        form=form,
        user_submissions=user_submissions,
    )


@main_bp.route("/subject/<int:subject_id>/delete", methods=["POST"])
@login_required
def delete_subject(subject_id: int) -> Response:
    """Удаление предмета"""
    if not current_user.is_admin:
        flash("Доступ запрещён")
        return redirect(url_for("main.index"))
    
    subject = Subject.query.get_or_404(subject_id)
    # Удаляем все материалы этого предмета
    for material in subject.materials:
        db.session.delete(material)
    db.session.delete(subject)
    db.session.commit()
    flash("Предмет удалён")
    return redirect(url_for("main.index"))


@main_bp.route("/material/<int:material_id>")
@login_required
def material_detail(material_id: int) -> Union[str, Response]:
    """Детальная страница материала"""
    material = Material.query.get_or_404(material_id)

    # Создаем сервис платежей
    payment_service = YooKassaService()
    # Проверяем подписку пользователя
    if not payment_service.check_user_subscription(current_user):
        flash("Для доступа к материалам необходима активная подписка.", "warning")
        return redirect(url_for("payment.subscription"))

    return render_template("subjects/material_detail.html", material=material)


@main_bp.route("/material/<int:material_id>/add_solution", methods=["POST"])
@login_required
def add_solution_file(material_id: int) -> Response:
    """Добавление файла решения к материалу"""
    if not current_user.is_admin:
        flash("Доступ запрещён")
        return redirect(url_for("main.index"))
    
    material = Material.query.get_or_404(material_id)
    file = request.files.get("solution_file")
    if file:
        # Получаем информацию о предмете
        subject = material.subject
        original_filename = secure_filename(file.filename)

        # Создаем путь для файла решения
        full_path, relative_path = FileStorageManager.get_material_upload_path(
            subject.id, f"admin_solution_{original_filename}"
        )

        # Сохраняем файл
        if FileStorageManager.save_file(file, full_path):
            material.solution_file = relative_path
            db.session.commit()
            flash("Готовая практика добавлена")
    
    return redirect(url_for("main.subject_detail", subject_id=material.subject_id))


@main_bp.route("/material/<int:material_id>/submit_solution", methods=["POST"])
@login_required
def submit_solution(material_id: int) -> Response:
    """Загрузка решения пользователем"""
    material = Material.query.get_or_404(material_id)

    # Создаем сервис платежей и проверяем подписку
    payment_service = YooKassaService()
    if not payment_service.check_user_subscription(current_user):
        flash("Для загрузки решений необходима активная подписка.", "warning")
        return redirect(url_for("payment.subscription"))

    if material.type != "assignment":
        flash("Можно загружать решение только для практик")
        return redirect(url_for("main.subject_detail", subject_id=material.subject_id))
    
    file = request.files.get("solution_file")
    if file:
        # Получаем информацию о предмете
        subject = material.subject
        original_filename = secure_filename(file.filename)

        # Создаем путь для файла решения пользователя
        full_path, relative_path = FileStorageManager.get_subject_upload_path(
            subject.id, current_user.id, f"user_solution_{original_filename}"
        )

        # Сохраняем файл
        if FileStorageManager.save_file(file, full_path):
            # Обновить или создать Submission
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
    
    return redirect(url_for("main.subject_detail", subject_id=material.subject_id))


@main_bp.route("/material/<int:material_id>/delete", methods=["POST"])
@login_required
def delete_material(material_id: int) -> Response:
    """Удаление материала"""
    if not current_user.is_admin:
        flash("Доступ запрещён")
        return redirect(url_for("main.index"))
    
    material = Material.query.get_or_404(material_id)
    subject_id = material.subject_id
    db.session.delete(material)
    db.session.commit()
    flash("Материал удалён")
    return redirect(url_for("main.subject_detail", subject_id=subject_id))


@main_bp.route("/privacy")
def privacy() -> str:
    """Страница политики конфиденциальности"""
    return render_template("static/privacy.html")


@main_bp.route("/terms")
def terms() -> str:
    """Страница условий предоставления услуг"""
    return render_template("static/terms.html")


@main_bp.route("/404")
def not_found() -> tuple:
    """Страница 404"""
    return render_template("static/404.html"), 404


@main_bp.app_errorhandler(404)
def handle_404(error) -> Response:
    """Обработчик ошибки 404"""
    return redirect(url_for('main.not_found'))


@main_bp.route("/maintenance")
def maintenance() -> str:
    """Страница технических работ"""
    return render_template("maintenance.html")


@main_bp.route("/wiki")
def wiki() -> str:
    """Wiki-страница с документацией и руководствами"""
    return render_template("static/wiki.html")


@main_bp.route("/macro/time")
def macro_time() -> str:
    """Страница конвертера времени"""
    return render_template("for_my_love/time.html")


@main_bp.route("/macro")
def macro() -> str:
    """Страница макросов"""
    return render_template("for_my_love/macro.html")
