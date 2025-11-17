import os
import shutil
from .. import db
from ..models import Subject, SubjectGroup, Material
from ..utils.transliteration import get_safe_filename


class SubjectService:
    @staticmethod
    def create_subject(
        title: str,
        description: str,
        pattern_type: str,
        pattern_svg: str,
        created_by: int,
        upload_path: str,
    ):
        subject = Subject(
            title=title,
            description=description,
            pattern_type=pattern_type,
            pattern_svg=pattern_svg,
            created_by=created_by,
        )
        db.session.add(subject)
        db.session.commit()
        subject_path = os.path.join(upload_path, str(subject.id))
        os.makedirs(subject_path, exist_ok=True)
        return subject

    @staticmethod
    def update_subject(subject_id: int, title: str, description: str) -> bool:
        subject = Subject.query.get_or_404(subject_id)
        if not title or len(title) > 255:
            return False
        if len(description) > 500:
            return False
        subject.title = title
        subject.description = description if description else None
        db.session.commit()
        return True

    @staticmethod
    def delete_subject(subject: Subject, upload_path: str) -> None:
        subject_path = os.path.join(upload_path, str(subject.id))
        if os.path.exists(subject_path):
            shutil.rmtree(subject_path)
        for material in subject.materials:
            db.session.delete(material)
        db.session.delete(subject)
        db.session.commit()

    @staticmethod
    def get_subject_or_404(subject_id: int):
        return Subject.query.get_or_404(subject_id)
