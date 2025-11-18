import logging
import os
import sys
from dataclasses import dataclass
from logging.handlers import RotatingFileHandler
from typing import Optional


@dataclass
class ColorScheme:
    """Цветовая схема для красивых логов"""

    peach_orange = "\033[38;5;208m"  # Основной песочный цвет
    orange = "\033[38;5;202m"
    salmon = "\033[38;5;203m"
    coral = "\033[38;5;204m"
    border_gray = "\033[38;5;244m"
    success_green = "\033[38;5;46m"
    error_red = "\033[38;5;196m"
    warning_orange = "\033[38;5;214m"
    info_blue = "\033[38;5;39m"
    debug_gray = "\033[38;5;247m"
    reset = "\033[0m"
    dim = "\033[2m"
    bold = "\033[1m"


@dataclass
class LogSymbols:
    """Символы для структуризации логов"""

    corner_top_left = "┌"
    corner_top_right = "┐"
    corner_bottom_left = "└"
    corner_bottom_right = "┘"
    line_horizontal = "─"
    line_vertical = "│"


class CYSULogger:
    """Красивый централизованный логгер для CYSU"""

    def __init__(self):
        self.colors = ColorScheme()
        self.symbols = LogSymbols()
        self._configured = False

    def configure(
        self,
        log_level: str = "INFO",
        log_file: Optional[str] = None,
        max_file_size: int = 10 * 1024 * 1024,
        backup_count: int = 5,
        console_enabled: bool = True,
        file_enabled: bool = True,
    ) -> None:
        """Настройка красивого централизованного логирования"""

        if self._configured:
            return

        # Основной логгер для CYSU
        logger = logging.getLogger("cysu")
        logger.setLevel(getattr(logging, log_level.upper()))

        # Очищаем существующие хендлеры
        logger.handlers.clear()

        # Создаём красивый форматтер для консоли
        console_formatter = self._create_beautiful_formatter()

        # Консольный хендлер
        if console_enabled:
            console_handler = logging.StreamHandler(sys.stderr)
            console_handler.setLevel(getattr(logging, log_level.upper()))
            console_handler.setFormatter(console_formatter)
            console_handler.addFilter(self._console_filter)
            logger.addHandler(console_handler)

        # Файловый хендлер (простой формат без цветов)
        if file_enabled and log_file:
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)

            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_file_size,
                backupCount=backup_count,
                encoding="utf-8",
            )
            file_formatter = logging.Formatter(
                "[%(asctime)s] %(levelname)-8s %(name)-20s %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            file_handler.setLevel(getattr(logging, log_level.upper()))
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

        # Подавляем шумные библиотеки
        self._suppress_noisy_libraries()

        # Корневой логгер устанавливаем на высокий уровень
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.WARNING)

        self._configured = True

    def _create_beautiful_formatter(self) -> logging.Formatter:
        """Создаёт красивый форматтер с цветами и отступами"""

        colors = self.colors

        class BeautifulFormatter(logging.Formatter):
            def format(self, record):
                # Получаем базовое форматирование
                formatted_time = self.formatTime(record, "%H:%M:%S")

                # Уровень с персиково-оранжевой цветовой схемой
                level_name = record.levelname
                if level_name == "DEBUG":
                    level_str = f"{colors.debug_gray}[DBG]{colors.reset}"
                elif level_name == "INFO":
                    level_str = f"{colors.peach_orange}[INF]{colors.reset}"
                elif level_name == "WARNING":
                    level_str = f"{colors.orange}[WRN]{colors.reset}"
                elif level_name == "ERROR":
                    level_str = f"{colors.error_red}[ERR]{colors.reset}"
                elif level_name == "CRITICAL":
                    level_str = f"{colors.error_red}[CRI]{colors.reset}"
                else:
                    level_str = f"[{level_name}]"

                # Модуль с отступом (ограничение до 15 символов)
                module_name = record.name
                module_parts = module_name.split(".")
                display_name = module_parts[-1] if len(module_parts) > 1 else module_name
                if len(display_name) > 15:
                    display_name = display_name[:12] + "..."
                module_str = f"{colors.dim}{display_name:<15}{colors.reset}"

                # Сообщение с дополнительной стилизацией
                message = record.getMessage()

                # Финальная компоновка с красивым отступом
                result = f" {formatted_time}  {level_str}  {module_str}  {message}"

                return result

        return BeautifulFormatter()

    def _console_filter(self, record) -> bool:
        """Фильтр для консольных логов - показывать только важное"""
        message = record.getMessage().lower()
        module = record.name.lower()

        # Исключаем частые и неинтересные логи
        noise_patterns = [
            "get /static/",
            "get /favicon",
            "status code",
            "content-length",
            "cache-control",
            "request.method",
            "request.path",
        ]

        for pattern in noise_patterns:
            if pattern in message:
                return False

        return True

    def _suppress_noisy_libraries(self):
        """Установка высокого уровня логирования для шумных библиотек"""
        noisy_libs = [
            "werkzeug",
            "sqlalchemy",
            "flask",
            "flask_sqlalchemy",
            "flask_migrate",
            "telethon",
            "telegram",
            "urllib3",
            "requests",
            "httpx",
            "mail",
        ]

        for lib in noisy_libs:
            logging.getLogger(lib).setLevel(logging.WARNING)


# Глобальный экземпляр логгера
logger = CYSULogger()


def get_logger(name: str) -> logging.Logger:
    """Получение настроенного логгера для модуля"""
    log = logging.getLogger(f"cysu.{name}")

    if not logger._configured:
        logger.configure()

    return log


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    console_enabled: bool = True,
    file_enabled: bool = True,
):
    """Быстрая настройка логирования"""
    logger.configure(
        log_level=log_level,
        log_file=log_file,
        console_enabled=console_enabled,
        file_enabled=file_enabled,
    )


# Вспомогательные функции для логирования
def log_success(message: str):
    """Логирование успешных операций"""
    get_logger("app").info(f"SUCCESS: {message}")


def log_error(message: str, exc_info=None):
    """Логирование ошибок"""
    get_logger("app").error(f"ERROR: {message}", exc_info=exc_info)


def log_warning(message: str):
    """Логирование предупреждений"""
    get_logger("app").warning(f"WARNING: {message}")


def log_info(message: str):
    """Логирование информации"""
    get_logger("app").info(message)


def log_debug(message: str):
    """Логирование отладочной информации"""
    get_logger("app").debug(message)
