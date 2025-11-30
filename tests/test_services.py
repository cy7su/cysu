"""Тесты для сервисов."""

import pytest
import tempfile
import os
import uuid
from app.services.subject_service import SubjectService
from app.services.material_service import MaterialService
from app.services.export_service import ExportService
from app.models import Subject, Material, db


class TestSubjectService:
    """Тесты для SubjectService."""

    def test_create_subject(self, app):
        """Тест создания предмета."""
        with app.app_context():
            with tempfile.TemporaryDirectory() as temp_dir:
                subject = SubjectService.create_subject(
                    title="Тестовый предмет",
                    description="Описание предмета",
                    pattern_type="dots",
                    pattern_svg="<svg></svg>",
                    created_by=1,
                    upload_path=temp_dir,
                )

                assert subject.id is not None
                assert subject.title == "Тестовый предмет"
                assert subject.description == "Описание предмета"
                assert subject.pattern_type == "dots"
                assert subject.created_by == 1

                subject_path = os.path.join(temp_dir, str(subject.id))
                assert os.path.exists(subject_path)

    def test_update_subject(self, app):
        """Тест обновления предмета."""
        with app.app_context():

            subject = Subject(title="Old Title", description="Old Description")
            db.session.add(subject)
            db.session.commit()

            result = SubjectService.update_subject(
                subject.id, "New Title", "New Description"
            )

            assert result is True
            updated_subject = Subject.query.get(subject.id)
            assert updated_subject.title == "New Title"
            assert updated_subject.description == "New Description"

    def test_update_subject_invalid_title(self, app):
        """Тест обновления предмета с некорректным заголовком."""
        with app.app_context():
            subject = Subject(title="Test")
            db.session.add(subject)
            db.session.commit()

            result = SubjectService.update_subject(subject.id, "", "Description")
            assert result is False

            long_title = "A" * 300
            result = SubjectService.update_subject(
                subject.id, long_title, "Description"
            )
            assert result is False

    def test_get_subject_or_404(self, app):
        """Тест получения предмета или 404."""
        with app.app_context():
            subject = Subject(title="Test Subject")
            db.session.add(subject)
            db.session.commit()

            found_subject = SubjectService.get_subject_or_404(subject.id)
            assert found_subject.id == subject.id

            with pytest.raises(Exception):

                SubjectService.get_subject_or_404(99999)


class TestMaterialService:
    """Тесты для MaterialService."""

    def test_get_subject_materials(self, app):
        """Тест получения материалов предмета."""
        with app.app_context():

            subject = Subject(title=f"Test Subject {uuid.uuid4()}")
            db.session.add(subject)
            db.session.commit()

            lecture = Material(title="Лекция", type="lecture", subject_id=subject.id)
            assignment = Material(
                title="Задание", type="assignment", subject_id=subject.id
            )

            db.session.add(lecture)
            db.session.add(assignment)
            db.session.commit()

            lectures, assignments = MaterialService.get_subject_materials(subject.id)

            assert len(lectures) == 1
            assert len(assignments) == 1
            assert lectures[0].type == "lecture"
            assert assignments[0].type == "assignment"

    def test_create_material(self, app):
        """Тест создания материала."""
        with app.app_context():

            subject = Subject(title="Test Subject")
            db.session.add(subject)
            db.session.commit()

            material = MaterialService.create_material(
                subject_id=subject.id,
                title="Тестовый материал",
                description="Описание",
                material_type="lecture",
                file_data=None,
                solution_file_data=None,
                created_by=1,
            )

            assert material.id is not None
            assert material.title == "Тестовый материал"
            assert material.type == "lecture"
            assert material.subject_id == subject.id

    def test_update_material(self, app):
        """Тест обновления материала."""
        with app.app_context():

            subject = Subject(title="Subject")
            db.session.add(subject)
            db.session.commit()

            material = Material(
                title="Old Title",
                description="Old Description",
                type="lecture",
                subject_id=subject.id,
            )
            db.session.add(material)
            db.session.commit()

            result = MaterialService.update_material(
                material.id, "New Title", "New Description"
            )

            assert result is True
            updated_material = Material.query.get(material.id)
            assert updated_material.title == "New Title"
            assert updated_material.description == "New Description"

    def test_update_material_invalid_data(self, app):
        """Тест обновления материала с некорректными данными."""
        with app.app_context():
            subject = Subject(title="Subject")
            db.session.add(subject)
            db.session.commit()

            material = Material(title="Test", type="lecture", subject_id=subject.id)
            db.session.add(material)
            db.session.commit()

            long_title = "A" * 300
            result = MaterialService.update_material(material.id, long_title, "Desc")
            assert result is False

            long_desc = "A" * 400
            result = MaterialService.update_material(material.id, "Title", long_desc)
            assert result is False

    def test_submit_solution_invalid_material_type(self, app):
        """Тест отправки решения для некорректного типа материала."""
        with app.app_context():
            subject = Subject(title="Subject")
            db.session.add(subject)
            db.session.commit()

            lecture = Material(title="Lecture", type="lecture", subject_id=subject.id)
            db.session.add(lecture)
            db.session.commit()

            class MockFile:
                filename = "test.pdf"
                content_length = 1024

            result = MaterialService.submit_solution(lecture, 1, MockFile())
            assert result is False

    def test_submit_solution_no_file(self, app):
        """Тест отправки решения без файла."""
        with app.app_context():
            subject = Subject(title="Subject")
            db.session.add(subject)
            db.session.commit()

            assignment = Material(
                title="Assignment", type="assignment", subject_id=subject.id
            )
            db.session.add(assignment)
            db.session.commit()

            result = MaterialService.submit_solution(assignment, 1, None)
            assert result is False


class TestExportService:
    """Тесты для ExportService."""

    def test_clean_folder_name_valid(self, app):
        """Тест очистки названия папки с валидными именами."""

        result = ExportService.clean_folder_name("Математика")
        assert result == "Математика"

        result = ExportService.clean_folder_name("")
        assert result == "Без_названия"

        result = ExportService.clean_folder_name("   Алгебра   ")
        assert result == "Алгебра"

    def test_clean_folder_name_with_invalid_chars(self, app):
        """Тест очистки названия папки с недопустимыми символами."""

        result = ExportService.clean_folder_name("Мат/?*\\:<>|")
        assert result == "Мат"

        result = ExportService.clean_folder_name("Мат Алгебра")
        assert result == "Мат_Алгебра"

        result = ExportService.clean_folder_name("Файл\\:\\  :/?")
        assert result == "Файл"

        long_name = "A" * 150
        result = ExportService.clean_folder_name(long_name)
        assert result == "Предмет"

    def test_export_user_solutions_no_submissions(self, app):
        """Тест экспорта решений для пользователя без решений."""
        with app.app_context():
            result = ExportService.export_user_solutions(999, "testuser")
            assert result is None

    def test_export_user_solutions_with_submissions(self, app):
        """Тест экспорта решений для пользователя с решениями."""
        with app.app_context():

            subject = Subject(title="Математика")
            db.session.add(subject)
            db.session.commit()

            material = Material(
                title="Упражнение 1", type="assignment", subject_id=subject.id
            )
            db.session.add(material)
            db.session.commit()

            result = ExportService.export_user_solutions(1, "testuser")

            assert result is None

    def test_generate_readme_content(self, app):
        """Тест генерации содержимого README."""
        with app.app_context():

            subjects_dict = {
                1: {
                    "subject": type("MockSubject", (), {"title": "Математика"})(),
                    "files": [
                        {
                            "material_title": "Упражнение 1",
                            "archive_path": "Математика/exercise1.pdf",
                        },
                        {
                            "material_title": "Упражнение 2",
                            "archive_path": "Математика/exercise2.pdf",
                        },
                    ],
                }
            }

            content = ExportService._generate_readme_content("Иванов", subjects_dict)

            assert "Архив решений пользователя Иванов" in content
            assert "Математика" in content
            assert "Упражнение 1" in content
            assert "Упражнение 2" in content
            assert "Дата создания:" in content
