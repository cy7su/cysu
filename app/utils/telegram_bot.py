import logging
import os
from datetime import datetime, timedelta


from telegram import (
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models import TelegramUser, User

import os
log_dir = '/root/logs'
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'telegram_bot.log'), encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TG_TOKEN")
ADMIN_TELEGRAM_ID = int(os.getenv("TG_ID", 0))
USERS_PER_PAGE = 5


class TelegramBotManager:
    def __init__(self):
        self.app = create_app()
        self.users_cache = {}
        self.current_page = {}
        self.editing_users = {}  # Для хранения состояния редактирования

    def get_telegram_link(self, user: User) -> str:
        if user.email.endswith("@telegram.org"):
            telegram_id = user.email.replace("@telegram.org", "")
            if telegram_id.isdigit():
                return f"tg://user?id={telegram_id}"

        telegram_user = TelegramUser.query.filter_by(user_id=user.id).first()
        if telegram_user:
            return f"tg://user?id={telegram_user.telegram_id}"

        return "Не указан"

    async def start_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        user = update.effective_user

        with self.app.app_context():
            try:
                TelegramUser.get_or_create(
                    telegram_id=user.id,
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    is_bot=user.is_bot,
                    language_code=user.language_code,
                )
            except Exception as e:
                logger.error(f"Ошибка создания Telegram пользователя: {e}")

            if user.id == ADMIN_TELEGRAM_ID:
                await update.message.reply_text(
                    "Добро пожаловать, администратор!\n\n"
                    "Доступные команды:\n"
                    "/users - Управление пользователями\n"
                    "/groups - Управление группами"
                )
            else:
                await update.message.reply_text(
                    "Добро пожаловать!\n\n"
                    "Этот бот предназначен для управления аккаунтом на сайте cysu.ru\n\n"
                    "Для авторизации на сайте используйте кнопку 'Войти через Telegram'"
                )


    async def users_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        user = update.effective_user

        if user.id != ADMIN_TELEGRAM_ID:
            await update.message.reply_text(
                "У вас нет прав для выполнения этой команды"
            )
            return

        with self.app.app_context():
            await self.show_users_page(update, context, page=0)

    async def groups_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        user = update.effective_user

        if user.id != ADMIN_TELEGRAM_ID:
            await update.message.reply_text(
                "У вас нет прав для выполнения этой команды"
            )
            return

        with self.app.app_context():
            await self.show_groups_page(update, context, page=0)

    async def show_groups_page(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 0
    ):
        with self.app.app_context():
            try:
                from app.models import Group

                # Получаем общее количество групп
                total_groups = Group.query.count()
                total_pages = (total_groups + USERS_PER_PAGE - 1) // USERS_PER_PAGE

                # Получаем группы для текущей страницы
                groups = (
                    Group.query.order_by(Group.name)
                    .offset(page * USERS_PER_PAGE)
                    .limit(USERS_PER_PAGE)
                    .all()
                )

                keyboard = []
                for group in groups:
                    status_icons = []
                    if group.is_active:
                        status_icons.append("✓")
                    else:
                        status_icons.append("✗")

                    status_text = " ".join(status_icons) if status_icons else "✗"

                    keyboard.append([
                        InlineKeyboardButton(
                            f"{group.name} {status_text}",
                            callback_data=f"group_detail_{group.id}",
                        )
                    ])

                # Добавляем навигацию
                nav_buttons = []
                if page > 0:
                    nav_buttons.append(
                        InlineKeyboardButton("←", callback_data=f"groups_page_{page-1}")
                    )

                nav_buttons.append(
                    InlineKeyboardButton("Обновить", callback_data=f"groups_page_{page}")
                )

                if page < total_pages - 1:
                    nav_buttons.append(
                        InlineKeyboardButton("→", callback_data=f"groups_page_{page+1}")
                    )

                if nav_buttons:
                    keyboard.append(nav_buttons)

                # Добавляем кнопку создания новой группы
                keyboard.append([
                    InlineKeyboardButton("Создать группу", callback_data="create_group")
                ])

                reply_markup = InlineKeyboardMarkup(keyboard)

                text = f"Группы (стр. {page + 1}/{total_pages})\nВсего: {total_groups}"

                if update.callback_query:
                    # Удаляем предыдущее сообщение
                    try:
                        await update.callback_query.message.delete()
                    except Exception as e:
                        logger.warning(f"Не удалось удалить сообщение: {e}")

                    # Отправляем новое сообщение
                    await update.callback_query.message.chat.send_message(
                        text, reply_markup=reply_markup
                    )
                else:
                    await update.message.reply_text(
                        text, reply_markup=reply_markup
                    )

            except Exception as e:
                logger.error(f"Ошибка показа групп: {e}")
                await update.message.reply_text(
                    "Ошибка при загрузке групп"
                )

    async def show_group_detail(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, group_id: int
    ):
        with self.app.app_context():
            try:
                from app.models import Group

                group = Group.query.get(group_id)
                if not group:
                    await update.callback_query.answer("Группа не найдена")
                    return

                text = f"Группа: {group.name}\n"
                text += f"Описание: {group.description or 'Не указано'}\n"
                text += f"Статус: {'Активна' if group.is_active else 'Неактивна'}\n"
                text += f"ID: {group.id}"

                keyboard = [
                    [
                        InlineKeyboardButton(
                            f"Статус: {'Активна' if group.is_active else 'Неактивна'}",
                            callback_data=f"toggle_group_status_{group_id}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "Изменить название",
                            callback_data=f"edit_group_name_{group_id}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "Изменить описание",
                            callback_data=f"edit_group_desc_{group_id}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "Удалить группу",
                            callback_data=f"delete_group_{group_id}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "← Назад к списку", callback_data="groups_page_0"
                        )
                    ],
                ]

                reply_markup = InlineKeyboardMarkup(keyboard)

                # Удаляем предыдущее сообщение
                try:
                    await update.callback_query.message.delete()
                except Exception as e:
                    logger.warning(f"Не удалось удалить сообщение: {e}")

                # Отправляем новое сообщение
                await update.callback_query.message.chat.send_message(
                    text, reply_markup=reply_markup
                )

            except Exception as e:
                logger.error(f"Ошибка показа деталей группы: {e}")
                await update.callback_query.answer(
                    "Ошибка при загрузке данных"
                )

    async def start_create_group(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        with self.app.app_context():
            try:
                # Сохраняем состояние создания группы
                user_id = update.effective_user.id
                self.editing_users[user_id] = {
                    "action": "create_group",
                    "step": "name"
                }

                text = "Создание новой группы\n\nВведите название группы:"

                keyboard = [
                    [
                        InlineKeyboardButton(
                            "Отмена", callback_data="groups_page_0"
                        )
                    ]
                ]

                reply_markup = InlineKeyboardMarkup(keyboard)

                # Удаляем предыдущее сообщение
                try:
                    await update.callback_query.message.delete()
                except Exception as e:
                    logger.warning(f"Не удалось удалить сообщение: {e}")

                # Отправляем новое сообщение
                await update.callback_query.message.chat.send_message(
                    text, reply_markup=reply_markup
                )

            except Exception as e:
                logger.error(f"Ошибка начала создания группы: {e}")
                await update.callback_query.answer(
                    "Ошибка при загрузке данных"
                )

    async def show_users_page(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 0
    ):
        with self.app.app_context():
            try:
                users = (
                    User.query.order_by(User.id.desc())
                    .offset(page * USERS_PER_PAGE)
                    .limit(USERS_PER_PAGE)
                    .all()
                )
                total_users = User.query.count()
                total_pages = (
                    total_users + USERS_PER_PAGE - 1
                ) // USERS_PER_PAGE

                if not users:
                    await update.message.reply_text(
                        "Пользователи не найдены"
                    )
                    return

                keyboard = []
                for user in users:
                    status_icons = []
                    if user.is_admin:
                        status_icons.append("★")
                    if user.is_moderator:
                        status_icons.append("▲")
                    if user.is_subscribed or user.is_trial_subscription:
                        status_icons.append("●")
                    if user.is_verified:
                        status_icons.append("✓")

                    status_text = (
                        " ".join(status_icons) if status_icons else "✗"
                    )

                    if user.email.endswith("@telegram.org"):
                        telegram_id = user.email.replace("@telegram.org", "")
                        display_email = f"TG: {telegram_id}"
                    else:
                        display_email = user.email

                    button_text = (
                        f"{status_text} {user.username} ({display_email})"
                    )
                    callback_data = f"user_detail_{user.id}"
                    keyboard.append(
                        [
                            InlineKeyboardButton(
                                button_text, callback_data=callback_data
                            )
                        ]
                    )

                nav_buttons = []
                if page > 0:
                    nav_buttons.append(
                        InlineKeyboardButton(
                            "←", callback_data=f"users_page_{page-1}"
                        )
                    )
                if page < total_pages - 1:
                    nav_buttons.append(
                        InlineKeyboardButton(
                            "→", callback_data=f"users_page_{page+1}"
                        )
                    )

                if nav_buttons:
                    keyboard.append(nav_buttons)

                keyboard.append(
                    [
                        InlineKeyboardButton(
                            "Обновить", callback_data=f"users_page_{page}"
                        )
                    ]
                )

                reply_markup = InlineKeyboardMarkup(keyboard)

                text = f"Пользователи сайта (стр. {page + 1}/{total_pages})\nВсего: {total_users}"

                if update.callback_query:
                    # Удаляем предыдущее сообщение
                    try:
                        await update.callback_query.message.delete()
                    except Exception as e:
                        logger.warning(f"Не удалось удалить сообщение: {e}")

                    # Отправляем новое сообщение
                    await update.callback_query.message.chat.send_message(
                        text, reply_markup=reply_markup
                    )
                else:
                    await update.message.reply_text(
                        text, reply_markup=reply_markup
                    )

            except Exception as e:
                logger.error(f"Ошибка показа пользователей: {e}")
                await update.message.reply_text(
                    "Ошибка при загрузке пользователей"
                )

    async def show_user_detail(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int
    ):
        with self.app.app_context():
            try:
                user = User.query.get(user_id)
                if not user:
                    await update.callback_query.answer(
                        "Пользователь не найден"
                    )
                    return

                status_info = []
                if user.is_admin:
                    status_info.append("★ Администратор")
                if user.is_moderator:
                    status_info.append("▲ Модератор")
                if user.is_subscribed:
                    status_info.append("● Подписка активна")
                elif user.is_trial_subscription:
                    status_info.append("● Пробная подписка")
                else:
                    status_info.append("✗ Без подписки")
                if user.is_verified:
                    status_info.append("✓ Email подтвержден")
                else:
                    status_info.append("✗ Email не подтвержден")

                group_info = f"Группа: {user.group.name if user.group else 'Не назначена'}"
                created_info = f"Создан: {user.created_at.strftime('%d.%m.%Y %H:%M') if user.created_at else 'Не указано'}"

                telegram_link = self.get_telegram_link(user)

                if user.email.endswith("@telegram.org"):
                    telegram_id = user.email.replace("@telegram.org", "")
                    email_display = f"Telegram: {telegram_id}"
                else:
                    email_display = f"Email: {user.email}"

                text = (
                    f"Пользователь: {user.username}\n"
                    f"{email_display}\n"
                    f"Ссылка: {telegram_link}\n"
                    f"ID: {user.id}\n"
                    f"{created_info}\n"
                    f"{group_info}\n\n"
                    "Статус:\n" + "\n".join(status_info)
                )

                keyboard = [
                    [
                        InlineKeyboardButton(
                            "Управление",
                            callback_data=f"user_manage_{user_id}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "Изменить группу",
                            callback_data=f"change_group_{user_id}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "Удалить", callback_data=f"user_delete_{user_id}"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "Изменить", callback_data=f"user_edit_{user_id}"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "← Назад к списку", callback_data="users_page_0"
                        )
                    ],
                ]

                reply_markup = InlineKeyboardMarkup(keyboard)

                # Удаляем предыдущее сообщение
                try:
                    await update.callback_query.message.delete()
                except Exception as e:
                    logger.warning(f"Не удалось удалить сообщение: {e}")

                # Отправляем новое сообщение
                await update.callback_query.message.chat.send_message(
                    text, reply_markup=reply_markup
                )

            except Exception as e:
                logger.error(f"Ошибка показа деталей пользователя: {e}")
                await update.callback_query.answer(
                    "Ошибка при загрузке данных"
                )

    async def show_change_group(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int
    ):
        with self.app.app_context():
            try:
                from app.models import Group, User

                user = User.query.get(user_id)
                if not user:
                    await update.callback_query.answer("Пользователь не найден")
                    return

                # Получаем все активные группы
                groups = Group.query.filter_by(is_active=True).order_by(Group.name).all()

                text = f"Изменение группы для пользователя {user.username}\n\n"
                text += f"Текущая группа: {user.group.name if user.group else 'Не назначена'}\n\n"
                text += "Выберите новую группу:"

                keyboard = []

                # Добавляем кнопку "Убрать группу"
                keyboard.append([
                    InlineKeyboardButton(
                        "Убрать группу",
                        callback_data=f"remove_group_{user_id}",
                    )
                ])

                # Добавляем кнопки для каждой группы
                for group in groups:
                    # Показываем текущую группу с отметкой
                    current_mark = " (текущая)" if user.group and user.group.id == group.id else ""
                    keyboard.append([
                        InlineKeyboardButton(
                            f"{group.name}{current_mark}",
                            callback_data=f"set_group_{user_id}_{group.id}",
                        )
                    ])

                # Кнопка "Назад"
                keyboard.append([
                    InlineKeyboardButton(
                        "← Назад", callback_data=f"user_detail_{user_id}"
                    )
                ])

                reply_markup = InlineKeyboardMarkup(keyboard)

                # Удаляем предыдущее сообщение
                try:
                    await update.callback_query.message.delete()
                except Exception as e:
                    logger.warning(f"Не удалось удалить сообщение: {e}")

                # Отправляем новое сообщение
                await update.callback_query.message.chat.send_message(
                    text, reply_markup=reply_markup
                )

            except Exception as e:
                logger.error(f"Ошибка показа изменения группы: {e}")
                await update.callback_query.answer(
                    "Ошибка при загрузке данных"
                )

    async def set_user_group(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, group_id: int
    ):
        with self.app.app_context():
            try:
                from app.models import User, Group

                user = User.query.get(user_id)
                group = Group.query.get(group_id)

                if not user:
                    await update.callback_query.answer("Пользователь не найден")
                    return

                if not group:
                    await update.callback_query.answer("Группа не найдена")
                    return

                user.group_id = group_id
                db.session.commit()

                await update.callback_query.answer(
                    f"Группа изменена на: {group.name}"
                )
                await self.show_user_detail(update, context, user_id)

            except Exception as e:
                logger.error(f"Ошибка изменения группы: {e}")
                await update.callback_query.answer(
                    "Ошибка при изменении группы"
                )

    async def remove_user_group(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int
    ):
        with self.app.app_context():
            try:
                from app.models import User

                user = User.query.get(user_id)
                if not user:
                    await update.callback_query.answer("Пользователь не найден")
                    return

                user.group_id = None
                db.session.commit()

                await update.callback_query.answer(
                    "Группа убрана у пользователя"
                )
                await self.show_user_detail(update, context, user_id)

            except Exception as e:
                logger.error(f"Ошибка удаления группы: {e}")
                await update.callback_query.answer(
                    "Ошибка при удалении группы"
                )

    async def toggle_group_status(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, group_id: int
    ):
        with self.app.app_context():
            try:
                from app.models import Group

                group = Group.query.get(group_id)
                if not group:
                    await update.callback_query.answer("Группа не найдена")
                    return

                group.is_active = not group.is_active
                db.session.commit()

                status = "активна" if group.is_active else "неактивна"
                await update.callback_query.answer(
                    f"Группа теперь {status}"
                )
                await self.show_group_detail(update, context, group_id)

            except Exception as e:
                logger.error(f"Ошибка переключения статуса группы: {e}")
                await update.callback_query.answer(
                    "Ошибка при изменении статуса"
                )

    async def start_edit_group_name(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, group_id: int
    ):
        with self.app.app_context():
            try:
                from app.models import Group

                group = Group.query.get(group_id)
                if not group:
                    await update.callback_query.answer("Группа не найдена")
                    return

                # Сохраняем состояние редактирования
                user_id = update.effective_user.id
                self.editing_users[user_id] = {
                    "action": "edit_group_name",
                    "group_id": group_id,
                    "current_name": group.name,
                }

                text = f"Изменение названия группы\n\nТекущее название: {group.name}\n\nВведите новое название:"

                keyboard = [
                    [
                        InlineKeyboardButton(
                            "Отмена", callback_data=f"group_detail_{group_id}"
                        )
                    ]
                ]

                reply_markup = InlineKeyboardMarkup(keyboard)

                # Удаляем предыдущее сообщение
                try:
                    await update.callback_query.message.delete()
                except Exception as e:
                    logger.warning(f"Не удалось удалить сообщение: {e}")

                # Отправляем новое сообщение
                await update.callback_query.message.chat.send_message(
                    text, reply_markup=reply_markup
                )

            except Exception as e:
                logger.error(f"Ошибка начала редактирования названия группы: {e}")
                await update.callback_query.answer(
                    "Ошибка при загрузке данных"
                )

    async def start_edit_group_desc(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, group_id: int
    ):
        with self.app.app_context():
            try:
                from app.models import Group

                group = Group.query.get(group_id)
                if not group:
                    await update.callback_query.answer("Группа не найдена")
                    return

                # Сохраняем состояние редактирования
                user_id = update.effective_user.id
                self.editing_users[user_id] = {
                    "action": "edit_group_desc",
                    "group_id": group_id,
                    "current_desc": group.description,
                }

                text = f"Изменение описания группы\n\nТекущее описание: {group.description or 'Не указано'}\n\nВведите новое описание (или отправьте '-' для удаления):"

                keyboard = [
                    [
                        InlineKeyboardButton(
                            "Отмена", callback_data=f"group_detail_{group_id}"
                        )
                    ]
                ]

                reply_markup = InlineKeyboardMarkup(keyboard)

                # Удаляем предыдущее сообщение
                try:
                    await update.callback_query.message.delete()
                except Exception as e:
                    logger.warning(f"Не удалось удалить сообщение: {e}")

                # Отправляем новое сообщение
                await update.callback_query.message.chat.send_message(
                    text, reply_markup=reply_markup
                )

            except Exception as e:
                logger.error(f"Ошибка начала редактирования описания группы: {e}")
                await update.callback_query.answer(
                    "Ошибка при загрузке данных"
                )

    async def delete_group(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, group_id: int
    ):
        with self.app.app_context():
            try:
                from app.models import Group

                group = Group.query.get(group_id)
                if not group:
                    await update.callback_query.answer("Группа не найдена")
                    return

                # Удаляем группу
                db.session.delete(group)
                db.session.commit()

                await update.callback_query.answer(
                    f"Группа '{group.name}' удалена"
                )
                await self.show_groups_page(update, context, page=0)

            except Exception as e:
                logger.error(f"Ошибка удаления группы: {e}")
                await update.callback_query.answer(
                    "Ошибка при удалении группы"
                )

    async def show_user_management(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int
    ):
        with self.app.app_context():
            try:
                user = User.query.get(user_id)
                if not user:
                    await update.callback_query.answer(
                        "Пользователь не найден"
                    )
                    return

                text = f"Управление пользователем: {user.username}\n\nВыберите действие:"

                keyboard = [
                    [
                        InlineKeyboardButton(
                            f"★ Админка: {'✓' if user.is_admin else '✗'}",
                            callback_data=f"toggle_admin_{user_id}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            f"▲ Модерка: {'✓' if user.is_moderator else '✗'}",
                            callback_data=f"toggle_moderator_{user_id}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            f"● Подписка: {'✓' if user.is_subscribed else '✗'}",
                            callback_data=f"toggle_subscription_{user_id}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            f"○ Пробная: {'✓' if user.is_trial_subscription else '✗'}",
                            callback_data=f"toggle_trial_{user_id}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "← Назад", callback_data=f"user_detail_{user_id}"
                        )
                    ],
                ]

                reply_markup = InlineKeyboardMarkup(keyboard)

                # Удаляем предыдущее сообщение
                try:
                    await update.callback_query.message.delete()
                except Exception as e:
                    logger.warning(f"Не удалось удалить сообщение: {e}")

                # Отправляем новое сообщение
                await update.callback_query.message.chat.send_message(
                    text, reply_markup=reply_markup
                )

            except Exception as e:
                logger.error(f"Ошибка показа управления пользователем: {e}")
                await update.callback_query.answer(
                    "Ошибка при загрузке данных"
                )

    async def show_user_edit(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int
    ):
        with self.app.app_context():
            try:
                user = User.query.get(user_id)
                if not user:
                    await update.callback_query.answer(
                        "Пользователь не найден"
                    )
                    return

                text = f"Редактирование пользователя: {user.username}\n\nВыберите что изменить:"

                keyboard = [
                    [
                        InlineKeyboardButton(
                            "Изменить ник",
                            callback_data=f"edit_username_{user_id}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "Изменить пароль",
                            callback_data=f"edit_password_{user_id}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "← Назад", callback_data=f"user_detail_{user_id}"
                        )
                    ],
                ]

                reply_markup = InlineKeyboardMarkup(keyboard)

                # Удаляем предыдущее сообщение
                try:
                    await update.callback_query.message.delete()
                except Exception as e:
                    logger.warning(f"Не удалось удалить сообщение: {e}")

                # Отправляем новое сообщение
                await update.callback_query.message.chat.send_message(
                    text, reply_markup=reply_markup
                )

            except Exception as e:
                logger.error(f"Ошибка показа редактирования пользователя: {e}")
                await update.callback_query.answer(
                    "Ошибка при загрузке данных"
                )

    async def start_edit_username(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int
    ):
        with self.app.app_context():
            try:
                user = User.query.get(user_id)
                if not user:
                    await update.callback_query.answer(
                        "Пользователь не найден"
                    )
                    return

                self.editing_users[update.effective_user.id] = {
                    "action": "edit_username",
                    "user_id": user_id,
                    "current_username": user.username,
                }

                text = f"Изменение имени пользователя\n\nТекущий ник: {user.username}\n\nВведите новый ник:"

                keyboard = [
                    [
                        InlineKeyboardButton(
                            "Отмена", callback_data=f"user_edit_{user_id}"
                        )
                    ]
                ]

                reply_markup = InlineKeyboardMarkup(keyboard)

                # Удаляем предыдущее сообщение
                try:
                    await update.callback_query.message.delete()
                except Exception as e:
                    logger.warning(f"Не удалось удалить сообщение: {e}")

                # Отправляем новое сообщение
                await update.callback_query.message.chat.send_message(
                    text, reply_markup=reply_markup
                )

            except Exception as e:
                logger.error(f"Ошибка начала редактирования имени: {e}")
                await update.callback_query.answer(
                    "Ошибка при загрузке данных"
                )

    async def start_edit_password(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int
    ):
        with self.app.app_context():
            try:
                user = User.query.get(user_id)
                if not user:
                    await update.callback_query.answer(
                        "Пользователь не найден"
                    )
                    return

                self.editing_users[update.effective_user.id] = {
                    "action": "edit_password",
                    "user_id": user_id,
                }

                text = f"Изменение пароля пользователя\n\nПользователь: {user.username}\n\nВведите новый пароль:"

                keyboard = [
                    [
                        InlineKeyboardButton(
                            "Отмена", callback_data=f"user_edit_{user_id}"
                        )
                    ]
                ]

                reply_markup = InlineKeyboardMarkup(keyboard)

                # Удаляем предыдущее сообщение
                try:
                    await update.callback_query.message.delete()
                except Exception as e:
                    logger.warning(f"Не удалось удалить сообщение: {e}")

                # Отправляем новое сообщение
                await update.callback_query.message.chat.send_message(
                    text, reply_markup=reply_markup
                )

            except Exception as e:
                logger.error(f"Ошибка начала редактирования пароля: {e}")
                await update.callback_query.answer(
                    "Ошибка при загрузке данных"
                )

    async def handle_message(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        user_id = update.effective_user.id

        if user_id not in self.editing_users:
            return

        editing_data = self.editing_users[user_id]
        action = editing_data["action"]

        # Для создания группы нет target_user_id
        if "user_id" in editing_data:
            target_user_id = editing_data["user_id"]
        else:
            target_user_id = None

        with self.app.app_context():
            try:
                if action == "edit_username":
                    new_username = update.message.text.strip()

                    if len(new_username) < 3 or len(new_username) > 50:
                        await update.message.reply_text(
                            "Имя пользователя должно быть от 3 до 50 символов"
                        )
                        return

                    existing_user = User.query.filter(
                        User.username == new_username,
                        User.id != target_user_id,
                    ).first()
                    if existing_user:
                        await update.message.reply_text(
                            "Пользователь с таким именем уже существует"
                        )
                        return

                    user = User.query.get(target_user_id)
                    if user:
                        user.username = new_username
                        db.session.commit()

                        await update.message.reply_text(
                            f"Имя пользователя изменено на: {new_username}"
                        )
                        del self.editing_users[user_id]
                    else:
                        await update.message.reply_text(
                            "Пользователь не найден"
                        )
                        del self.editing_users[user_id]

                elif action == "edit_password":
                    new_password = update.message.text.strip()

                    if len(new_password) < 6:
                        await update.message.reply_text(
                            "Пароль должен быть не менее 6 символов"
                        )
                        return

                    user = User.query.get(target_user_id)
                    if user:
                        user.password = generate_password_hash(new_password)
                        db.session.commit()

                        await update.message.reply_text(
                            f"Пароль для пользователя {user.username} изменен"
                        )
                        del self.editing_users[user_id]
                    else:
                        await update.message.reply_text(
                            "Пользователь не найден"
                        )
                        del self.editing_users[user_id]

                elif action == "create_group":
                    step = editing_data.get("step", "name")

                    if step == "name":
                        group_name = update.message.text.strip()

                        if len(group_name) < 2 or len(group_name) > 100:
                            await update.message.reply_text(
                                "Название группы должно быть от 2 до 100 символов"
                            )
                            return

                        # Проверяем, что группа с таким именем не существует
                        from app.models import Group
                        existing_group = Group.query.filter_by(name=group_name).first()
                        if existing_group:
                            await update.message.reply_text(
                                "Группа с таким названием уже существует"
                            )
                            return

                        # Сохраняем название и переходим к описанию
                        self.editing_users[user_id]["group_name"] = group_name
                        self.editing_users[user_id]["step"] = "description"

                        await update.message.reply_text(
                            f"Название группы: {group_name}\n\nВведите описание группы (или отправьте '-' для пропуска):"
                        )

                    elif step == "description":
                        group_description = update.message.text.strip()

                        if group_description == "-":
                            group_description = None

                        # Создаем группу
                        from app.models import Group
                        group = Group(
                            name=self.editing_users[user_id]["group_name"],
                            description=group_description,
                            is_active=True
                        )

                        db.session.add(group)
                        db.session.commit()

                        await update.message.reply_text(
                            f"Группа '{group.name}' успешно создана!"
                        )

                        # Очищаем состояние
                        del self.editing_users[user_id]

                        # Показываем список групп
                        await self.show_groups_page(update, context, page=0)

                elif action == "edit_group_name":
                    new_name = update.message.text.strip()

                    if len(new_name) < 2 or len(new_name) > 100:
                        await update.message.reply_text(
                            "Название группы должно быть от 2 до 100 символов"
                        )
                        return

                    # Проверяем, что группа с таким именем не существует
                    from app.models import Group
                    existing_group = Group.query.filter(
                        Group.name == new_name,
                        Group.id != editing_data["group_id"]
                    ).first()
                    if existing_group:
                        await update.message.reply_text(
                            "Группа с таким названием уже существует"
                        )
                        return

                    group = Group.query.get(editing_data["group_id"])
                    if group:
                        group.name = new_name
                        db.session.commit()

                        await update.message.reply_text(
                            f"Название группы изменено на: {new_name}"
                        )
                        del self.editing_users[user_id]

                        # Показываем детали группы
                        await self.show_group_detail(update, context, editing_data["group_id"])
                    else:
                        await update.message.reply_text(
                            "Группа не найдена"
                        )
                        del self.editing_users[user_id]

                elif action == "edit_group_desc":
                    new_desc = update.message.text.strip()

                    if new_desc == "-":
                        new_desc = None

                    group = Group.query.get(editing_data["group_id"])
                    if group:
                        group.description = new_desc
                        db.session.commit()

                        desc_text = "удалено" if new_desc is None else new_desc
                        await update.message.reply_text(
                            f"Описание группы изменено на: {desc_text}"
                        )
                        del self.editing_users[user_id]

                        # Показываем детали группы
                        await self.show_group_detail(update, context, editing_data["group_id"])
                    else:
                        await update.message.reply_text(
                            "Группа не найдена"
                        )
                        del self.editing_users[user_id]

            except Exception as e:
                logger.error(f"Ошибка обработки сообщения: {e}", exc_info=True)
                await update.message.reply_text(
                    f"Ошибка при обработке данных: {str(e)}"
                )
                if user_id in self.editing_users:
                    del self.editing_users[user_id]

    async def handle_callback_query(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        await query.answer()

        data = query.data

        try:
            if data.startswith("users_page_"):
                page = int(data.split("_")[2])
                await self.show_users_page(update, context, page)

            elif data.startswith("groups_page_"):
                page = int(data.split("_")[2])
                await self.show_groups_page(update, context, page)

            elif data.startswith("group_detail_"):
                group_id = int(data.split("_")[2])
                await self.show_group_detail(update, context, group_id)

            elif data == "create_group":
                await self.start_create_group(update, context)

            elif data.startswith("user_detail_"):
                user_id = int(data.split("_")[2])
                await self.show_user_detail(update, context, user_id)

            elif data.startswith("user_manage_"):
                user_id = int(data.split("_")[2])
                await self.show_user_management(update, context, user_id)

            elif data.startswith("user_edit_"):
                user_id = int(data.split("_")[2])
                await self.show_user_edit(update, context, user_id)

            elif data.startswith("change_group_"):
                user_id = int(data.split("_")[2])
                await self.show_change_group(update, context, user_id)

            elif data.startswith("set_group_"):
                parts = data.split("_")
                user_id = int(parts[2])
                group_id = int(parts[3])
                await self.set_user_group(update, context, user_id, group_id)

            elif data.startswith("remove_group_"):
                user_id = int(data.split("_")[2])
                await self.remove_user_group(update, context, user_id)

            elif data.startswith("toggle_group_status_"):
                group_id = int(data.split("_")[3])
                await self.toggle_group_status(update, context, group_id)

            elif data.startswith("edit_group_name_"):
                group_id = int(data.split("_")[3])
                await self.start_edit_group_name(update, context, group_id)

            elif data.startswith("edit_group_desc_"):
                group_id = int(data.split("_")[3])
                await self.start_edit_group_desc(update, context, group_id)

            elif data.startswith("delete_group_"):
                group_id = int(data.split("_")[2])
                await self.delete_group(update, context, group_id)

            elif data.startswith("edit_username_"):
                user_id = int(data.split("_")[2])
                await self.start_edit_username(update, context, user_id)

            elif data.startswith("edit_password_"):
                user_id = int(data.split("_")[2])
                await self.start_edit_password(update, context, user_id)

            elif data.startswith("toggle_admin_"):
                user_id = int(data.split("_")[2])
                await self.toggle_admin(update, context, user_id)

            elif data.startswith("toggle_moderator_"):
                user_id = int(data.split("_")[2])
                await self.toggle_moderator(update, context, user_id)

            elif data.startswith("toggle_subscription_"):
                user_id = int(data.split("_")[2])
                await self.toggle_subscription(update, context, user_id)

            elif data.startswith("toggle_trial_"):
                user_id = int(data.split("_")[2])
                await self.toggle_trial_subscription(update, context, user_id)

            elif data.startswith("user_delete_"):
                user_id = int(data.split("_")[2])
                await self.confirm_delete_user(update, context, user_id)

            elif data.startswith("confirm_delete_"):
                user_id = int(data.split("_")[2])
                await self.delete_user(update, context, user_id)

        except Exception as e:
            logger.error(f"Ошибка обработки callback: {e}")
            await query.answer("Ошибка при обработке запроса")

    async def toggle_admin(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int
    ):
        with self.app.app_context():
            try:
                user = User.query.get(user_id)
                if not user:
                    await update.callback_query.answer(
                        "Пользователь не найден"
                    )
                    return

                user.is_admin = not user.is_admin
                db.session.commit()

                status = "выданы" if user.is_admin else "забраны"
                await update.callback_query.answer(
                    f"★ Права администратора {status}"
                )
                await self.show_user_management(update, context, user_id)

            except Exception as e:
                logger.error(f"Ошибка переключения админки: {e}")
                await update.callback_query.answer(
                    "Ошибка при изменении прав"
                )

    async def toggle_moderator(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int
    ):
        with self.app.app_context():
            try:
                user = User.query.get(user_id)
                if not user:
                    await update.callback_query.answer(
                        "Пользователь не найден"
                    )
                    return

                user.is_moderator = not user.is_moderator
                db.session.commit()

                status = "выданы" if user.is_moderator else "забраны"
                await update.callback_query.answer(
                    f"▲ Права модератора {status}"
                )
                await self.show_user_management(update, context, user_id)

            except Exception as e:
                logger.error(f"Ошибка переключения модерки: {e}")
                await update.callback_query.answer(
                    "Ошибка при изменении прав"
                )

    async def toggle_subscription(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int
    ):
        with self.app.app_context():
            try:
                user = User.query.get(user_id)
                if not user:
                    await update.callback_query.answer(
                        "Пользователь не найден"
                    )
                    return

                if user.is_subscribed:
                    user.is_subscribed = False
                    user.is_manual_subscription = False
                    user.subscription_expires = None
                else:
                    user.is_subscribed = True
                    user.is_manual_subscription = True
                    user.subscription_expires = datetime.utcnow() + timedelta(
                        days=365
                    )  # Год подписки

                db.session.commit()

                status = "выдана" if user.is_subscribed else "забрана"
                await update.callback_query.answer(f"● Подписка {status}")
                await self.show_user_management(update, context, user_id)

            except Exception as e:
                logger.error(f"Ошибка переключения подписки: {e}")
                await update.callback_query.answer(
                    "Ошибка при изменении подписки"
                )

    async def toggle_trial_subscription(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int
    ):
        with self.app.app_context():
            try:
                user = User.query.get(user_id)
                if not user:
                    await update.callback_query.answer(
                        "Пользователь не найден"
                    )
                    return

                user.is_trial_subscription = not user.is_trial_subscription
                db.session.commit()

                status = "выдана" if user.is_trial_subscription else "отменена"
                await update.callback_query.answer(f"○ Пробная подписка {status}")
                await self.show_user_management(update, context, user_id)

            except Exception as e:
                logger.error(f"Ошибка переключения пробной подписки: {e}")
                await update.callback_query.answer(
                    "Ошибка при изменении пробной подписки"
                )

    async def confirm_delete_user(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int
    ):
        with self.app.app_context():
            try:
                user = User.query.get(user_id)
                if not user:
                    await update.callback_query.answer(
                        "Пользователь не найден"
                    )
                    return

                text = f"ВНИМАНИЕ!\n\nВы действительно хотите удалить пользователя {user.username}?\n\nЭто действие нельзя отменить!"

                keyboard = [
                    [
                        InlineKeyboardButton(
                            "Да, удалить",
                            callback_data=f"confirm_delete_{user_id}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "Отмена", callback_data=f"user_detail_{user_id}"
                        )
                    ],
                ]

                reply_markup = InlineKeyboardMarkup(keyboard)

                # Удаляем предыдущее сообщение
                try:
                    await update.callback_query.message.delete()
                except Exception as e:
                    logger.warning(f"Не удалось удалить сообщение: {e}")

                # Отправляем новое сообщение
                await update.callback_query.message.chat.send_message(
                    text, reply_markup=reply_markup
                )

            except Exception as e:
                logger.error(f"Ошибка подтверждения удаления: {e}")
                await update.callback_query.answer(
                    "Ошибка при загрузке данных"
                )

    async def delete_user(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int
    ):
        with self.app.app_context():
            try:
                user = User.query.get(user_id)
                if not user:
                    await update.callback_query.answer(
                        "Пользователь не найден"
                    )
                    return

                username = user.username

                TelegramUser.query.filter_by(user_id=user_id).delete()

                db.session.delete(user)
                db.session.commit()

                await update.callback_query.answer(
                    f"Пользователь {username} удален"
                )
                await self.show_users_page(update, context, page=0)

            except Exception as e:
                logger.error(f"Ошибка удаления пользователя: {e}")
                await update.callback_query.answer(
                    "Ошибка при удалении пользователя"
                )

    async def error_handler(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        logger.error(f"Ошибка при обработке обновления: {context.error}")
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "Произошла ошибка. Попробуйте позже."
            )

    def run_bot(self):
        if not BOT_TOKEN:
            logger.error("TG_TOKEN не найден в переменных окружения")
            return

        if not ADMIN_TELEGRAM_ID:
            logger.error("TG_ID не найден в переменных окружения")
            return

        application = Application.builder().token(BOT_TOKEN).build()

        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("users", self.users_command))
        application.add_handler(CommandHandler("groups", self.groups_command))
        application.add_handler(
            CallbackQueryHandler(self.handle_callback_query)
        )
        application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, self.handle_message
            )
        )
        application.add_error_handler(self.error_handler)

        commands = [
            BotCommand("start", "Запустить бота"),
            BotCommand(
                "users", "Управление пользователями (только для админов)"
            ),
            BotCommand(
                "groups", "Управление группами (только для админов)"
            ),
        ]

        async def post_init(application):
            await application.bot.set_my_commands(commands)

        application.post_init = post_init

        logger.info("Запуск Telegram бота...")
        application.run_polling()


if __name__ == "__main__":
    bot_manager = TelegramBotManager()
    bot_manager.run_bot()
