import os
import tempfile
import zipfile
from datetime import datetime
from typing import Dict, Optional

from flask import current_app
from werkzeug.utils import secure_filename

from ..models import Material, Subject, Submission


class ExportService:
    @staticmethod
    def clean_folder_name(name: str) -> str:
        if not name:
            return "Без_названия"

        name = name.strip()

        invalid_chars = ["/", "\\", ":", "*", "?", '"', "<", ">", "|", "\n", "\r", "\t"]
        for char in invalid_chars:
            name = name.replace(char, "_")

        while "__" in name:
            name = name.replace("__", "_")

        if " " in name:
            name = "_".join(name.split())

        name = name.strip("_")

        if not name or len(name) > 100:
            return "Предмет"
        return name

    @staticmethod
    def export_user_solutions(user_id: int, username: str) -> Optional[str]:
        submissions = Submission.query.filter_by(user_id=user_id).all()
        if not submissions:
            return None
        temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
        temp_zip.close()
        upload_folder = current_app.config.get("UPLOAD_FOLDER", "app/static/uploads")
        with zipfile.ZipFile(temp_zip.name, "w", zipfile.ZIP_DEFLATED) as zip_file:
            subjects_dict = {}
            for submission in submissions:
                if not submission.file:
                    continue
                material = Material.query.get(submission.material_id)
                if not material:
                    continue
                subject = Subject.query.get(material.subject_id)
                if not subject:
                    continue
                if subject.id not in subjects_dict:
                    subjects_dict[subject.id] = {"subject": subject, "files": []}
                file_path = os.path.join(upload_folder, submission.file)
                if os.path.exists(file_path):
                    safe_filename = secure_filename(os.path.basename(submission.file))
                    subject_name = ExportService.clean_folder_name(subject.title)
                    archive_path = os.path.join(subject_name, safe_filename)
                    subjects_dict[subject.id]["files"].append(
                        {
                            "file_path": file_path,
                            "archive_path": archive_path,
                            "material_title": material.title,
                        }
                    )
            for subject_data in subjects_dict.values():
                for file_info in subject_data["files"]:
                    try:
                        zip_file.write(
                            file_info["file_path"], file_info["archive_path"]
                        )
                    except Exception as e:
                        current_app.logger.error(
                            f"Error adding file {file_info['file_path']} to archive: {e}"
                        )
            readme_content = ExportService._generate_readme_content(
                username, subjects_dict
            )
            zip_file.writestr("README.txt", readme_content.encode("utf-8"))
        return temp_zip.name

    @staticmethod
    def _generate_readme_content(username: str, subjects_dict: Dict) -> str:
        content = f"""Архив решений пользователя {username}
Дата создания: {datetime.now().strftime("%d.%m.%Y %H:%M")}
Содержимое архива:
"""
        for subject_data in subjects_dict.values():
            subject = subject_data["subject"]
            folder_name = ExportService.clean_folder_name(subject.title)
            content += f"\n{subject.title} (папка: {folder_name}):\n"
            for file_info in subject_data["files"]:
                content += f"  - {file_info['material_title']} ({os.path.basename(file_info['archive_path'])})\n"
        return content
