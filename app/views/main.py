"""
Основной модуль views с базовыми функциями
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, Response
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from ..utils.transliteration import get_safe_filename
from sqlalchemy.orm import joinedload
from typing import Union, Dict, Any
import os
import shutil

from ..models import User, Material, Subject, SubjectGroup, SiteSettings
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
                    
                    # Создаем папку для предмета
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
            # Используем новый метод для получения доступных предметов
            subjects = current_user.get_accessible_subjects()
            # Добавляем связанные данные
            subjects = Subject.query.options(
                joinedload(Subject.materials),
                joinedload(Subject.groups)
            ).filter(Subject.id.in_([s.id for s in subjects])).all()
            
            # Показываем предупреждение если нет доступных предметов
            if not subjects and current_user.group_id:
                flash("У вашей группы нет назначенных предметов. Обратитесь к администратору.", "warning")
            elif not subjects and not current_user.group_id:
                flash("У вас не назначена группа. Обратитесь к администратору.", "warning")
        else:
            # Для неавторизованных пользователей показываем все предметы
            subjects = Subject.query.options(
                joinedload(Subject.materials),
                joinedload(Subject.groups)
            ).all()
    except Exception as e:
        current_app.logger.error(f"Error querying subjects: {e}")
        subjects = []
        flash("Ошибка загрузки предметов. Попробуйте обновить страницу.", "error")
    
    # Получаем настройку генерации паттернов
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
    """Страница профиля пользователя"""
    try:
        # Создаем сервис платежей
        payment_service = YooKassaService()
        # Проверяем актуальность подписки
        is_subscribed = payment_service.check_user_subscription(current_user)
        
        # Определяем тип подписки
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
    """Детальная страница предмета"""
    if request.method == "POST":
        current_app.logger.info(f"POST запрос к subject_detail для предмета {subject_id}")
        current_app.logger.info(f"Content-Length: {request.content_length}")
        current_app.logger.info(f"Content-Type: {request.content_type}")
        current_app.logger.info(f"MAX_CONTENT_LENGTH: {current_app.config.get('MAX_CONTENT_LENGTH')}")
        
        # Логируем информацию о файлах в запросе
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
    
    # Проверяем доступ к предмету
    if current_user.is_authenticated:
        accessible_subjects = current_user.get_accessible_subjects()
        if subject not in accessible_subjects:
            flash("У вас нет доступа к этому предмету.", "error")
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
            if not current_user.is_effective_admin():
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
    
    # Создаем форму только если пользователь может добавлять материалы
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

            # Получаем информацию о предмете
            subject = Subject.query.get_or_404(subject_id)

            if form.file.data:
                file = form.file.data
                original_filename = get_safe_filename(file.filename)
                
                # Логируем информацию о файле
                file_size = getattr(file, 'content_length', None) or len(file.read()) if hasattr(file, 'read') else 'unknown'
                if hasattr(file, 'seek'):
                    file.seek(0)  # Возвращаем указатель в начало
                
                current_app.logger.info(f"Загрузка файла материала: {file.filename} -> {original_filename}")
                current_app.logger.info(f"Размер файла: {file_size} байт ({file_size / (1024*1024):.2f} MB)" if isinstance(file_size, int) else f"Размер файла: {file_size}")
                current_app.logger.info(f"MAX_CONTENT_LENGTH: {current_app.config.get('MAX_CONTENT_LENGTH')} байт ({current_app.config.get('MAX_CONTENT_LENGTH', 0) / (1024*1024):.2f} MB)")
                
                # Проверяем размер файла
                if isinstance(file_size, int) and current_app.config.get('MAX_CONTENT_LENGTH'):
                    if file_size > current_app.config.get('MAX_CONTENT_LENGTH'):
                        current_app.logger.error(f"Файл слишком большой: {file_size} байт > {current_app.config.get('MAX_CONTENT_LENGTH')} байт")
                        flash(f"Файл слишком большой. Максимальный размер: {current_app.config.get('MAX_CONTENT_LENGTH', 0) / (1024*1024):.1f} MB", "error")
                        return redirect(url_for("main.subject_detail", subject_id=subject_id))

                # Создаем путь для файла материала
                full_path, relative_path = FileStorageManager.get_material_upload_path(
                    subject.id, original_filename
                )
                
                current_app.logger.info(f"Путь для сохранения: {full_path}")
                current_app.logger.info(f"Относительный путь: {relative_path}")

                # Сохраняем файл
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
                
                # Логируем информацию о файле решения
                solution_file_size = getattr(solution_file, 'content_length', None) or len(solution_file.read()) if hasattr(solution_file, 'read') else 'unknown'
                if hasattr(solution_file, 'seek'):
                    solution_file.seek(0)  # Возвращаем указатель в начало
                
                current_app.logger.info(f"Загрузка файла решения: {solution_file.filename} -> {original_solution_filename}")
                current_app.logger.info(f"Размер файла решения: {solution_file_size} байт ({solution_file_size / (1024*1024):.2f} MB)" if isinstance(solution_file_size, int) else f"Размер файла решения: {solution_file_size}")
                
                # Проверяем размер файла решения
                if isinstance(solution_file_size, int) and current_app.config.get('MAX_CONTENT_LENGTH'):
                    if solution_file_size > current_app.config.get('MAX_CONTENT_LENGTH'):
                        current_app.logger.error(f"Файл решения слишком большой: {solution_file_size} байт > {current_app.config.get('MAX_CONTENT_LENGTH')} байт")
                        flash(f"Файл решения слишком большой. Максимальный размер: {current_app.config.get('MAX_CONTENT_LENGTH', 0) / (1024*1024):.1f} MB", "error")
                        return redirect(url_for("main.subject_detail", subject_id=subject_id))

                # Создаем путь для файла решения
                full_solution_path, relative_solution_path = (
                    FileStorageManager.get_material_upload_path(
                        subject.id,
                        original_solution_filename,
                    )
                )

                # Сохраняем файл решения
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
    
    # Проверяем, может ли пользователь добавлять материалы
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
    """Редактирование предмета"""
    if not current_user.is_effective_admin():
        flash("Доступ запрещён")
        return redirect(url_for("main.index"))
    
    subject = Subject.query.get_or_404(subject_id)
    
    try:
        # Получаем данные из формы
        new_title = request.form.get("title", "").strip()
        new_description = request.form.get("description", "").strip()
        
        # Валидация
        if not new_title:
            flash("Название предмета не может быть пустым", "error")
            return redirect(url_for("main.subject_detail", subject_id=subject_id))
        
        if len(new_title) > 255:
            flash("Название предмета слишком длинное (максимум 255 символов)", "error")
            return redirect(url_for("main.subject_detail", subject_id=subject_id))
        
        if len(new_description) > 500:
            flash("Описание слишком длинное (максимум 500 символов)", "error")
            return redirect(url_for("main.subject_detail", subject_id=subject_id))
        
        # Обновляем данные
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
    """Удаление предмета"""
    if not current_user.is_effective_admin():
        flash("Доступ запрещён")
        return redirect(url_for("main.index"))
    
    subject = Subject.query.get_or_404(subject_id)
    
    # Удаляем папку предмета с файлами
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

    # Получаем решения пользователя для заданий
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
    """Удаление решения пользователя"""
    from app.models import Submission
    from app.utils.file_storage import FileStorageManager
    
    submission = Submission.query.get_or_404(submission_id)
    
    # Проверяем, что пользователь может удалить это решение
    if submission.user_id != current_user.id:
        flash("Доступ запрещён", "error")
        return redirect(url_for("main.index"))
    
    # Удаляем файл с диска
    if submission.file:
        try:
            FileStorageManager.delete_file(submission.file)
        except Exception as e:
            current_app.logger.error(f"Ошибка при удалении файла {submission.file}: {e}")
    
    # Удаляем запись из базы данных
    db.session.delete(submission)
    db.session.commit()
    
    flash("Решение удалено", "success")
    return redirect(url_for("main.material_detail", material_id=submission.material_id))


@main_bp.route("/material/<int:material_id>/add_solution", methods=["POST"])
@login_required
def add_solution_file(material_id: int) -> Response:
    """Добавление файла решения к материалу"""
    current_app.logger.info(f"POST запрос к add_solution_file для материала {material_id}")
    current_app.logger.info(f"Content-Length: {request.content_length}")
    current_app.logger.info(f"Content-Type: {request.content_type}")
    current_app.logger.info(f"MAX_CONTENT_LENGTH: {current_app.config.get('MAX_CONTENT_LENGTH')}")
    
    # Логируем информацию о файлах в запросе
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
    
    # Проверяем доступ к предмету для модераторов
    if current_user.is_moderator:
        accessible_subjects = current_user.get_accessible_subjects()
        if material.subject not in accessible_subjects:
            flash("У вас нет доступа к этому предмету.", "error")
            return redirect(url_for("main.index"))
    file = request.files.get("solution_file")
    if file:
        # Получаем информацию о предмете
        subject = material.subject
        original_filename = get_safe_filename(file.filename)
        
        # Логируем информацию о файле
        file_size = getattr(file, 'content_length', None) or len(file.read()) if hasattr(file, 'read') else 'unknown'
        if hasattr(file, 'seek'):
            file.seek(0)  # Возвращаем указатель в начало
        
        current_app.logger.info(f"Загрузка готового решения: {file.filename} -> {original_filename}")
        current_app.logger.info(f"Размер файла: {file_size} байт ({file_size / (1024*1024):.2f} MB)" if isinstance(file_size, int) else f"Размер файла: {file_size}")
        
        # Проверяем размер файла
        if isinstance(file_size, int) and current_app.config.get('MAX_CONTENT_LENGTH'):
            if file_size > current_app.config.get('MAX_CONTENT_LENGTH'):
                current_app.logger.error(f"Файл готового решения слишком большой: {file_size} байт > {current_app.config.get('MAX_CONTENT_LENGTH')} байт")
                flash(f"Файл слишком большой. Максимальный размер: {current_app.config.get('MAX_CONTENT_LENGTH', 0) / (1024*1024):.1f} MB", "error")
                return redirect(url_for("main.subject_detail", subject_id=material.subject_id))

        # Создаем путь для файла решения
        full_path, relative_path = FileStorageManager.get_material_upload_path(
            subject.id, original_filename
        )

        # Сохраняем файл
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
    """Загрузка решения пользователем"""
    current_app.logger.info(f"POST запрос к submit_solution для материала {material_id} от пользователя {current_user.id}")
    current_app.logger.info(f"Content-Length: {request.content_length}")
    current_app.logger.info(f"Content-Type: {request.content_type}")
    current_app.logger.info(f"MAX_CONTENT_LENGTH: {current_app.config.get('MAX_CONTENT_LENGTH')}")
    
    # Логируем информацию о файлах в запросе
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
        original_filename = get_safe_filename(file.filename)
        
        # Логируем информацию о файле
        file_size = getattr(file, 'content_length', None) or len(file.read()) if hasattr(file, 'read') else 'unknown'
        if hasattr(file, 'seek'):
            file.seek(0)  # Возвращаем указатель в начало
        
        current_app.logger.info(f"Загрузка решения пользователя {current_user.id}: {file.filename} -> {original_filename}")
        current_app.logger.info(f"Размер файла: {file_size} байт ({file_size / (1024*1024):.2f} MB)" if isinstance(file_size, int) else f"Размер файла: {file_size}")
        
        # Проверяем размер файла
        if isinstance(file_size, int) and current_app.config.get('MAX_CONTENT_LENGTH'):
            if file_size > current_app.config.get('MAX_CONTENT_LENGTH'):
                current_app.logger.error(f"Файл решения пользователя слишком большой: {file_size} байт > {current_app.config.get('MAX_CONTENT_LENGTH')} байт")
                flash(f"Файл слишком большой. Максимальный размер: {current_app.config.get('MAX_CONTENT_LENGTH', 0) / (1024*1024):.1f} MB", "error")
                return redirect(url_for("main.subject_detail", subject_id=material.subject_id))

        # Создаем путь для файла решения пользователя
        full_path, relative_path = FileStorageManager.get_subject_upload_path(
            subject.id, current_user.id, original_filename
        )

        # Сохраняем файл
        try:
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
    """Переключение режима админа"""
    if not current_user.is_admin:
        flash("Доступ запрещён")
        return redirect(url_for("main.index"))
    
    current_user.admin_mode_enabled = not current_user.admin_mode_enabled
    db.session.commit()
    
    mode = "админ" if current_user.admin_mode_enabled else "пользователь"
    flash(f"Переключен в режим {mode}")
    
    return redirect(request.referrer or url_for("main.index"))


@main_bp.route("/material/<int:material_id>/delete", methods=["POST"])
@login_required
def delete_material(material_id: int) -> Response:
    """Удаление материала"""
    if not current_user.can_manage_materials():
        flash("Доступ запрещён")
        return redirect(url_for("main.index"))
    
    material = Material.query.get_or_404(material_id)
    subject_id = material.subject_id
    
    # Проверяем доступ к предмету для модераторов
    if current_user.is_moderator:
        accessible_subjects = current_user.get_accessible_subjects()
        if material.subject not in accessible_subjects:
            flash("У вас нет доступа к этому предмету.", "error")
            return redirect(url_for("main.index"))
    
    # Удаляем файл материала, если он существует
    if material.file:
        try:
            upload_base = current_app.config.get("UPLOAD_FOLDER", "app/static/uploads")
            file_path = os.path.join(upload_base, material.file)
            if os.path.exists(file_path):
                os.remove(file_path)
                current_app.logger.info(f"Удален файл материала: {file_path}")
        except Exception as file_error:
            current_app.logger.error(f"Ошибка удаления файла материала {material.file}: {file_error}")
    
    # Удаляем файл решения, если он существует
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


@main_bp.route("/redirect")
def redirect_page() -> str:
    """Страница редиректа на cysu.ru"""
    return render_template("redirect.html")


@main_bp.route("/redirect/download")
def download_redirect() -> Response:
    """Скачивание HTML файла редиректа без кнопки скачать"""
    from flask import make_response
    
    # Читаем содержимое шаблона
    with open('/root/cysu/app/templates/redirect.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Удаляем кнопку скачать из HTML
    # Ищем и удаляем кнопку скачать и связанные с ней стили
    import re
    
    # Удаляем кнопку скачать из модальных действий
    html_content = re.sub(
        r'<a href="/redirect/download"[^>]*download="cysu\.html"[^>]*>.*?</a>\s*',
        '',
        html_content,
        flags=re.DOTALL
    )
    
    # Удаляем стили для кнопки скачать
    html_content = re.sub(
        r'\.btn-download\s*\{[^}]*\}',
        '',
        html_content,
        flags=re.DOTALL
    )
    
    # Создаем ответ с HTML файлом
    response = make_response(html_content)
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    response.headers['Content-Disposition'] = 'attachment; filename="cysu.html"'
    
    return response


@main_bp.route('/files/<int:subject_id>/<path:filename>', methods=['GET', 'HEAD'])
def serve_file(subject_id: int, filename: str) -> Response:
    """Отдача файлов с поддержкой Range запросов для PDF"""
    from flask import Response, abort, request
    import os
    import time
    
    current_app.logger.info(f"serve_file вызвана: subject_id={subject_id}, filename={filename}")
    current_app.logger.info(f"UPLOAD_FOLDER: {current_app.config['UPLOAD_FOLDER']}")
    start_time = time.time()
    
    # Получаем полный путь к файлу
    # Сначала пробуем найти файл по разным вариантам путей
    possible_paths = [
        # Если filename уже содержит полный путь (например, "13/users/123/filename.pdf")
        os.path.join(current_app.config['UPLOAD_FOLDER'], filename),
        # Если filename только имя файла (например, "Fajrvol.pdf")
        os.path.join(current_app.config['UPLOAD_FOLDER'], str(subject_id), filename),
        # Если filename начинается с subject_id/
        os.path.join(current_app.config['UPLOAD_FOLDER'], f"{subject_id}/{filename}"),
        # Если filename содержит только basename
        os.path.join(current_app.config['UPLOAD_FOLDER'], str(subject_id), os.path.basename(filename))
    ]
    
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
    
    # Определяем Content-Type по расширению
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
        
        # Обработка Range запросов для больших файлов
        range_header = request.headers.get('Range')
        if range_header:
            current_app.logger.info(f"Range запрос: {range_header}")
            return _handle_range_request(file_path, file_size, mimetype, filename)
        
        # Для HEAD запросов возвращаем только заголовки
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
            
            # Для PDF файлов устанавливаем принудительное скачивание
            if filename.lower().endswith('.pdf'):
                response.headers['Content-Disposition'] = f'attachment; filename="{os.path.basename(filename)}"'
            
            return response
        
        # Потоковая передача файла
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
        
        # Для PDF файлов устанавливаем принудительное скачивание
        if filename.lower().endswith('.pdf'):
            response.headers['Content-Disposition'] = f'attachment; filename="{os.path.basename(filename)}"'
        
        # Логируем время выполнения
        execution_time = time.time() - start_time
        current_app.logger.info(f"Файл {filename} обработан за {execution_time:.3f} секунд")
        
        return response
        
    except Exception as e:
        current_app.logger.error(f"Ошибка обработки файла {file_path}: {e}")
        abort(500)


def _handle_range_request(file_path: str, file_size: int, mimetype: str, filename: str) -> Response:
    """Обработка HTTP Range запросов для частичной загрузки файлов"""
    from flask import request, Response
    import re
    
    # Парсим Range заголовок
    range_match = re.match(r'bytes=(\d+)-(\d*)', request.headers.get('Range', ''))
    if not range_match:
        current_app.logger.warning("Некорректный Range заголовок")
        return Response('Bad Request', status=400)
    
    start = int(range_match.group(1))
    end = int(range_match.group(2)) if range_match.group(2) else file_size - 1
    
    # Проверяем корректность диапазона
    if start >= file_size or end >= file_size or start > end:
        current_app.logger.warning(f"Некорректный диапазон: {start}-{end} для файла размером {file_size}")
        return Response('Requested Range Not Satisfiable', status=416)
    
    # Вычисляем длину контента
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
    
    # Для PDF файлов устанавливаем принудительное скачивание
    if filename.lower().endswith('.pdf'):
        response.headers['Content-Disposition'] = f'attachment; filename="{os.path.basename(filename)}"'
    
    return response


