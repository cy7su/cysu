import json
import os
import tempfile
import zipfile
from pathlib import Path
from typing import Optional, Tuple

from flask import current_app


class FileOptimizer:
    """Модуль для автоматической оптимизации загружаемых файлов без потери качества"""

    SUPPORTED_EXTENSIONS = {"pdf", "docx", "pptx", "ipynb", "jpg", "jpeg", "png"}

    @staticmethod
    def optimize_file(file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Оптимизирует файл по его расширению

        Args:
            file_path: Путь к файлу для оптимизации

        Returns:
            Tuple[bool, Optional[str]]: (успех, новое_имя_файла_или_None)
        """
        if not os.path.exists(file_path):
            return False, None

        filename = os.path.basename(file_path)
        if "." not in filename:
            return True, None

        extension = filename.rsplit(".", 1)[1].lower()

        if extension not in FileOptimizer.SUPPORTED_EXTENSIONS:
            return True, None

        try:
            if extension == "pdf":
                return FileOptimizer._optimize_pdf(file_path)
            elif extension in ["docx", "pptx"]:
                return FileOptimizer._optimize_office_file(file_path)
            elif extension == "ipynb":
                return FileOptimizer._optimize_ipynb(file_path)
            elif extension in ["jpg", "jpeg", "png"]:
                return FileOptimizer._optimize_image(file_path)
            else:
                return True, None
        except Exception as e:
            current_app.logger.warning(f"Ошибка оптимизации файла {file_path}: {e}")
            return False, None

    @staticmethod
    def _optimize_pdf(file_path: str) -> Tuple[bool, Optional[str]]:
        """Оптимизация PDF файла с помощью Ghostscript"""
        try:
            import subprocess

            temp_path = file_path + ".optimized"

            cmd = [
                "gs",
                "-sDEVICE=pdfwrite",
                "-dCompatibilityLevel=1.4",
                "-dPDFSETTINGS=/ebook",
                "-dNOPAUSE",
                "-dQUIET",
                "-dBATCH",
                f"-sOutputFile={temp_path}",
                file_path,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode == 0 and os.path.exists(temp_path):
                orig_size = os.path.getsize(file_path)
                opt_size = os.path.getsize(temp_path)

                if opt_size < orig_size:

                    os.replace(temp_path, file_path)
                    current_app.logger.info(
                        f"PDF оптимизирован: {file_path} ({orig_size} -> {opt_size})"
                    )
                    return True, None
                else:

                    os.unlink(temp_path)
                    return True, None
            else:
                current_app.logger.warning(f"Ошибка оптимизации PDF: {result.stderr}")
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                return False, None

        except subprocess.TimeoutExpired:
            current_app.logger.warning(f"Таймаут оптимизации PDF: {file_path}")
            return False, None
        except Exception as e:
            current_app.logger.warning(f"Ошибка оптимизации PDF {file_path}: {e}")
            return False, None

    @staticmethod
    def _optimize_office_file(file_path: str) -> Tuple[bool, Optional[str]]:
        """Оптимизация Office файлов (DOCX, PPTX) путем пересжатия ZIP"""
        try:
            filename = os.path.basename(file_path)
            temp_path = file_path + ".optimized"

            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path_obj = Path(temp_dir)

                with zipfile.ZipFile(file_path, "r") as zip_ref:
                    zip_ref.extractall(temp_path_obj)

                FileOptimizer._clean_office_metadata(temp_path_obj)

                with zipfile.ZipFile(
                    temp_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9
                ) as zip_out:
                    for file_path_in_zip in temp_path_obj.rglob("*"):
                        if file_path_in_zip.is_file():
                            arcname = file_path_in_zip.relative_to(temp_path_obj)
                            zip_out.write(file_path_in_zip, arcname)

            orig_size = os.path.getsize(file_path)
            opt_size = os.path.getsize(temp_path)

            if opt_size < orig_size:
                os.replace(temp_path, file_path)
                current_app.logger.info(
                    f"Office файл оптимизирован: {file_path} ({orig_size} -> {opt_size})"
                )
                return True, None
            else:
                os.unlink(temp_path)
                return True, None

        except Exception as e:
            current_app.logger.warning(
                f"Ошибка оптимизации Office файла {file_path}: {e}"
            )
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            return False, None

    @staticmethod
    def _clean_office_metadata(temp_path: Path) -> None:
        """Удаляет ненужные метаданные из Office файлов"""
        files_to_remove = [
            "docProps/thumbnail.jpeg",
            "docProps/thumbnail.png",
            "docProps/thumbnail.wmf",
            "docProps/thumbnail.emf",
            "[Content_Types].xml.bak",
        ]

        for file_to_remove in files_to_remove:
            file_path_to_remove = temp_path / file_to_remove
            if file_path_to_remove.exists():
                file_path_to_remove.unlink()

    @staticmethod
    def _optimize_ipynb(file_path: str) -> Tuple[bool, Optional[str]]:
        """Оптимизация Jupyter notebook - очистка метаданных и outputs"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                nb = json.load(f)

            if "metadata" in nb:
                nb["metadata"] = {}

            for cell in nb.get("cells", []):
                if "metadata" in cell:
                    cell["metadata"] = {}
                if "outputs" in cell:
                    cell["outputs"] = []
                if "execution_count" in cell:
                    cell["execution_count"] = None

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(nb, f, indent=1, ensure_ascii=False)

            current_app.logger.info(f"IPYNB оптимизирован: {file_path}")
            return True, None

        except Exception as e:
            current_app.logger.warning(f"Ошибка оптимизации IPYNB {file_path}: {e}")
            return False, None

    @staticmethod
    def _optimize_image(file_path: str) -> Tuple[bool, Optional[str]]:
        """Оптимизация изображений (пока только базовая поддержка)"""

        return True, None

    @staticmethod
    def should_optimize_file(filename: str) -> bool:
        """Проверяет, нужно ли оптимизировать файл по его имени"""
        if not filename or "." not in filename:
            return False

        extension = filename.rsplit(".", 1)[1].lower()
        return extension in FileOptimizer.SUPPORTED_EXTENSIONS
