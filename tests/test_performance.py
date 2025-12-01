"""Тесты производительности и нагрузки."""

import time
import uuid
from concurrent.futures import ThreadPoolExecutor

import pytest


class TestPerformance:
    """Тесты производительности."""

    def test_database_query_performance(self, app, db):
        """Тест производительности запросов к базе данных."""
        from app.models import Material, Subject, User

        with app.app_context():

            users = []
            for i in range(10):
                user = User(
                    username=f"testuser{i}_{uuid.uuid4()}",
                    email=f"test{i}_{uuid.uuid4()}@gmail.com",
                    password="test",
                )
                users.append(user)
                db.session.add(user)

            subjects = []
            for i in range(5):
                subject = Subject(
                    title=f"Test Subject {i}_{uuid.uuid4()}",
                    description=f"Description {i}",
                )
                subjects.append(subject)
                db.session.add(subject)

            db.session.commit()

            for subject in subjects:
                for j in range(3):
                    material = Material(
                        title=f"Material {j} for {subject.title}",
                        description=f"Description {j}",
                        type="lecture" if j % 2 == 0 else "assignment",
                        subject_id=subject.id,
                    )
                    db.session.add(material)

            db.session.commit()

            start_time = time.time()
            for _ in range(100):
                users_result = User.query.all()
                subjects_result = Subject.query.all()
            end_time = time.time()

            query_time = end_time - start_time
            assert query_time < 5.0, f"Database queries too slow: {query_time:.2f}s"

    def test_api_response_time(self, client):
        """Тест времени отклика API."""
        start_time = time.time()
        response = client.get("/")
        end_time = time.time()

        response_time = end_time - start_time
        assert response.status_code == 200
        assert response_time < 2.0, f"Response too slow: {response_time:.2f}s"

    def test_static_file_serving(self, client, app):
        """Тест производительности отдачи статических файлов."""
        with app.app_context():
            import os

            start_time = time.time()
            response = client.get("/robots.txt")
            end_time = time.time()

            response_time = end_time - start_time
            assert response.status_code in [200, 301]

            assert (
                response_time < 1.0
            ), f"Static file serving too slow: {response_time:.2f}s"


class TestLoad:
    """Нагрузочные тесты."""

    def test_concurrent_requests(self, client):
        """Тест одновременных запросов."""

        def make_request(url):
            response = client.get(url)
            return response.status_code

        urls = ["/", "/privacy", "/terms"] * 10

        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(make_request, urls))

        successful_requests = sum(1 for status in results if status == 200)
        assert successful_requests == len(
            urls
        ), f"Only {successful_requests}/{len(urls)} requests successful"


class TestIntegration:
    """Интеграционные тесты."""

    def test_full_user_workflow(self, app, client, db):
        """Тест полного рабочего процесса пользователя."""
        with app.app_context():

            assert True, "Integration test placeholder"

    def test_subject_material_workflow(self, app, client, db):
        """Тест рабочего процесса предмет-материал."""
        from app.models import Material, Subject

        with app.app_context():

            subject = Subject(
                title="Integration Test Subject", description="Test description"
            )
            db.session.add(subject)
            db.session.commit()

            material = Material(
                title="Integration Test Material", type="lecture", subject_id=subject.id
            )
            db.session.add(material)
            db.session.commit()

            assert len(subject.materials) == 1
            assert subject.materials[0].title == "Integration Test Material"
            assert material.subject.title == "Integration Test Subject"


class TestCoverage:
    """Тесты покрытия."""

    def test_import_coverage(self, app):
        """Тест покрытия импортов всех модулей."""

        try:
            import app.models
            import app.services.material_service
            import app.services.subject_service
            import app.services.user_service
            import app.utils.email_service
            import app.utils.payment_service
            import app.views.auth
            import app.views.main

            assert True, "All critical modules imported successfully"
        except ImportError as e:
            pytest.fail(f"Import failed: {e}")

    def test_service_integration_coverage(self, app, db):
        """Тест интеграции сервисов."""
        from app.models import Material, Subject
        from app.services.material_service import MaterialService
        from app.services.subject_service import SubjectService

        with app.app_context():
            import tempfile

            with tempfile.TemporaryDirectory() as temp_dir:
                subject = SubjectService.create_subject(
                    title="Coverage Test Subject",
                    description="Coverage test",
                    pattern_type="dots",
                    pattern_svg="<svg></svg>",
                    created_by=1,
                    upload_path=temp_dir,
                )

                material = MaterialService.create_material(
                    subject_id=subject.id,
                    title="Coverage Test Material",
                    description="Coverage test material",
                    material_type="lecture",
                )

                assert subject.title == "Coverage Test Subject"
                assert material.title == "Coverage Test Material"
                assert material.subject_id == subject.id
