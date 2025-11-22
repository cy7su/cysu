# type: ignore
import os
from datetime import datetime
from typing import List, Tuple, Optional

from flask import current_app
from sqlalchemy.orm import selectinload

from .. import db
from ..models import Material, Submission, Subject
from ..utils.file_storage import FileStorageManager
from ..utils.transliteration import get_safe_filename


class MaterialService:
    @staticmethod
    def get_subject_materials(subject_id: int) -> Tuple[List[Material], List[Material]]:
        lectures = Material.query.filter_by(subject_id=subject_id, type="lecture").all()
        assignments = (
            Material.query.options(selectinload('submissions'))
            .filter_by(subject_id=subject_id, type="assignment")
            .all()
        )
        return lectures, assignments

    @staticmethod
    def create_material(
        subject_id: int,
        title: str,
        description: str,
        material_type: str,
        file_data=None,
        solution_file_data=None,
        created_by: Optional[int] = None,
    ) -> Material:
        filename = None
        solution_filename = None
        if file_data:
            full_path, relative_path = FileStorageManager.get_material_upload_path(
                subject_id, get_safe_filename(file_data.filename)
            )
            if FileStorageManager.save_file(file_data, full_path):
                filename = relative_path
        if solution_file_data and material_type == "assignment":
            full_path, relative_path = FileStorageManager.get_material_upload_path(
                subject_id, get_safe_filename(solution_file_data.filename)
            )
            if FileStorageManager.save_file(solution_file_data, full_path):
                solution_filename = relative_path
        material = Material(
            title=title,
            description=description,
            file=filename,
            type=material_type,
            solution_file=solution_filename,
            subject_id=subject_id,
            created_by=created_by,
        )
        db.session.add(material)
        db.session.commit()
        return material

    @staticmethod
    def update_material(material_id: int, title: str, description: Optional[str]) -> bool:
        material = Material.query.get_or_404(material_id)
        if len(title) > 255:
            return False
        if description and len(description) > 300:
            return False
        material.title = title
        material.description = description or None
        db.session.commit()
        return True

    @staticmethod
    def replace_material_file(material: Material, file_data) -> bool:
        if not file_data or not file_data.filename:
            return False
        filename = get_safe_filename(file_data.filename)
        if hasattr(file_data, "content_length") and file_data.content_length:
            if file_data.content_length > current_app.config.get(
                "MAX_CONTENT_LENGTH", 500 * 1024 * 1024
            ):
                return False
        old_file_path = None
        if material.file:
            old_file_path = os.path.join(
                current_app.config["UPLOAD_FOLDER"], material.file
            )
            if os.path.exists(old_file_path):
                os.remove(old_file_path)
        full_path, relative_path = FileStorageManager.get_material_upload_path(
            material.subject_id, filename
        )
        if FileStorageManager.save_file(file_data, full_path):
            material.file = relative_path
            material.updated_at = datetime.utcnow()
            db.session.commit()
            return True
        return False

    @staticmethod
    def add_solution_file(material: Material, file_data) -> bool:
        if not file_data or not file_data.filename:
            return False
        subject = Subject.query.get(material.subject_id)
        filename = get_safe_filename(file_data.filename)
        if hasattr(file_data, "content_length") and file_data.content_length:
            if file_data.content_length > current_app.config.get(
                "MAX_CONTENT_LENGTH", 500 * 1024 * 1024
            ):
                return False
        full_path, relative_path = FileStorageManager.get_material_upload_path(
            subject.id, filename
        )
        if FileStorageManager.save_file(file_data, full_path):
            material.solution_file = relative_path
            db.session.commit()
            return True
        return False

    @staticmethod
    def delete_material(material: Material) -> None:
        for submission in material.submissions:
            if submission.file:
                FileStorageManager.delete_file(submission.file)
        if material.file:
            FileStorageManager.delete_file(material.file)
        if material.solution_file:
            FileStorageManager.delete_file(material.solution_file)
        db.session.delete(material)
        db.session.commit()

    @staticmethod
    def submit_solution(material: Material, user_id: int, file_data) -> bool:
        if material.type != "assignment":
            return False
        if not file_data or not file_data.filename:
            return False
        filename = get_safe_filename(file_data.filename)
        if hasattr(file_data, "content_length") and file_data.content_length:
            if file_data.content_length > current_app.config.get(
                "MAX_CONTENT_LENGTH", 500 * 1024 * 1024
            ):
                return False
        full_path, relative_path = FileStorageManager.get_subject_upload_path(
            material.subject_id, user_id, filename
        )
        submission = Submission.query.filter_by(
            user_id=user_id, material_id=material.id
        ).first()
        if not submission:
            submission = Submission(
                user_id=user_id, material_id=material.id
            )
            db.session.add(submission)
        submission.file = relative_path
        db.session.commit()
        return True
